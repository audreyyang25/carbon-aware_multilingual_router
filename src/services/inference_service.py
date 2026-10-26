# src/worker.py
import argparse
import logging
import os
import time

# os.environ['TORCH_USE_CUDA_DSA'] = '1'
import torch
import transformers
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    StoppingCriteria,
    StoppingCriteriaList,
)

from config.manager import load_config
from src.metrics.energy import EnergyMeasurement

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")


def _multimodal_auto_class():
    """Auto class for *ForConditionalGeneration checkpoints (Qwen3.5, Gemma 4)."""
    for name in ("AutoModelForMultimodalLM", "AutoModelForImageTextToText"):
        if hasattr(transformers, name):
            return getattr(transformers, name)
    return AutoModelForCausalLM


class KeywordsStoppingCriteria(StoppingCriteria):
    """Stop once a stop string appears in the generated text.

    Matches on decoded text rather than token ids, because a stop string like "####"
    tokenizes differently mid-sentence than on its own. Leading whitespace is ignored
    so a "\n" stop doesn't fire before the model has answered.
    """

    def __init__(self, tokenizer, stop_words, prompt_length):
        self.tokenizer = tokenizer
        self.stop_words = [word for word in stop_words if word]
        self.prompt_length = prompt_length

    def __call__(
        self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs
    ) -> bool:
        generated = self.tokenizer.decode(
            input_ids[0, self.prompt_length :], skip_special_tokens=True
        ).lstrip()
        return any(word in generated for word in self.stop_words)


class InferenceService:
    """Worker that pulls tasks from Redis and runs inference"""

    def __init__(
        self,
        redis_client,
        general_configs,
        model_configs,
        device_id=0,
        energy_method="pynvml",
    ):
        self.redis_client = redis_client
        self.general_configs = general_configs
        self.model_configs = model_configs
        self.device = f"cuda:{device_id}" if torch.cuda.is_available() else "cpu"
        self.energy_measurement = EnergyMeasurement.create(
            method=energy_method, device_id=device_id
        )
        self.loaded_model = None
        self.loaded_model_id = None
        self.tokenizer = None

    def _load_model(self, model_id):
        """Load model if not already loaded"""
        if self.loaded_model_id == model_id:
            return self.loaded_model, self.tokenizer
        if self.loaded_model is not None:
            logger.info(f"Unloading model {self.loaded_model_id}")
            self.loaded_model = None
            self.tokenizer = None
            torch.cuda.empty_cache()

        logger.info(f"Loading model {model_id}")
        model_config = self.model_configs[model_id]
        model_name = model_config["name"]
        hf_token = os.environ.get("HF_TOKEN")  # never stored in config files
        cache_dir = os.path.expanduser(self.general_configs.get("cache_dir", "~/.cache/huggingface"))
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, cache_dir=cache_dir, token=hf_token
        )
        auto_class = (
            _multimodal_auto_class()
            if model_config.get("auto_class") == "multimodal"
            else AutoModelForCausalLM
        )
        self.loaded_model = auto_class.from_pretrained(
            model_name,
            dtype=torch.bfloat16,
            device_map=self.device,
            cache_dir=cache_dir,
            token=hf_token,
            attn_implementation=model_config.get("attn_implementation", "sdpa"),
        )
        self.loaded_model.eval()
        self.loaded_model_id = model_id
        self._warm_up_model(self.loaded_model, self.tokenizer)

        return self.loaded_model, self.tokenizer

    def run_inference(self, query_text, model_id, generation_parameters=None):
        """Run inference on a query"""
        model, tokenizer = self._load_model(model_id)
        inputs, input_tokens, gen_params = self._prepare_generation_params(
            query_text, tokenizer, generation_parameters
        )
        self.energy_measurement.start()
        start_time = time.time()

        logger.debug(
            f"Generating response for input starting with: {query_text[:100]}..."
        )
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids, attention_mask=inputs.attention_mask, **gen_params
            )
        latency = time.time() - start_time
        energy = self.energy_measurement.stop()
        output_tokens = outputs.shape[1] - input_tokens
        output_text = tokenizer.decode(
            outputs[0, input_tokens:], skip_special_tokens=True
        )

        return {
            "response": output_text,
            "latency": latency,
            "metrics": {
                "latency": latency,
                "energy_consumption": energy,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
        }

    def _warm_up_model(self, model, tokenizer):
        """Run a warm-up inference to initialize model compilation and caches"""
        logger.info(f"Warming up model {self.loaded_model_id}")
        try:
            warm_up_text, add_special_tokens = self._format_prompt(
                "Hello, how are you today?", tokenizer
            )
            inputs = tokenizer(
                warm_up_text, return_tensors="pt", add_special_tokens=add_special_tokens
            ).to(model.device)
            with torch.no_grad():
                _ = model.generate(inputs.input_ids, max_new_tokens=20, do_sample=False)
            logger.info("Model warm-up complete")
        except Exception as e:
            logger.warning(f"Model warm-up failed: {e}")

    def _format_prompt(self, query_text, tokenizer):
        """Wrap the query in the model's chat template (thinking off by default).

        Returns (prompt, add_special_tokens). Per-model template options can be set
        with `chat_template_kwargs` in config/models.yaml.
        """
        if not getattr(tokenizer, "chat_template", None):
            return query_text, True

        model_config = self.model_configs.get(self.loaded_model_id, {})
        template_kwargs = {
            "enable_thinking": False,
            **model_config.get("chat_template_kwargs", {}),
        }
        prompt = tokenizer.apply_chat_template(
            [{"role": "user", "content": query_text}],
            tokenize=False,
            add_generation_prompt=True,
            **template_kwargs,
        )
        # The template already includes BOS/special tokens
        return prompt, False

    def _prepare_generation_params(
        self, query_text, tokenizer, generation_parameters=None
    ):
        """Prepare generation parameters and inputs"""

        prompt, add_special_tokens = self._format_prompt(query_text, tokenizer)
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=8192,
            add_special_tokens=add_special_tokens,
        ).to(self.device)
        input_tokens = inputs.input_ids.shape[1]
        # Greedy decoding so accuracy and energy are reproducible across runs
        gen_params = {
            "max_new_tokens": 256,
            "do_sample": False,
            "temperature": None,
            "top_p": None,
            "top_k": None,
            "pad_token_id": tokenizer.pad_token_id
            if tokenizer.pad_token_id is not None
            else tokenizer.eos_token_id,
        }
        generation_parameters = dict(generation_parameters or {})
        if generation_parameters:
            if "stop_sequence" in generation_parameters:
                stop_sequences = generation_parameters.pop("stop_sequence")
                if isinstance(stop_sequences, str):
                    try:
                        import ast

                        stop_sequences = ast.literal_eval(stop_sequences)
                    except (ValueError, SyntaxError):
                        stop_sequences = [stop_sequences]
                if not isinstance(stop_sequences, list):
                    stop_sequences = [stop_sequences]
                if stop_sequences:
                    stopping_criteria = StoppingCriteriaList()
                    stopping_criteria.append(
                        KeywordsStoppingCriteria(tokenizer, stop_sequences, input_tokens)
                    )
                    gen_params["stopping_criteria"] = stopping_criteria
            for key, value in generation_parameters.items():
                if key in ["max_new_tokens", "max_length"]:
                    gen_params["max_new_tokens"] = int(value)
                elif key == "num_beams":
                    gen_params[key] = value

        return inputs, input_tokens, gen_params

    def run(self):
        """Main worker loop"""
        logger.info(f"Worker started on {self.device}")

        while True:
            task = self.redis_client.get_next_task(timeout=1)
            if not task:
                time.sleep(0.1)
                continue

            logger.info(
                f"Processing task {task['id']} with model {task['selected_model']}"
            )

            try:
                result = self.run_inference(
                    task["query_text"],
                    task["selected_model"],
                    task.get("generation_parameters"),
                )
                self.redis_client.set_result(
                    task["id"],
                    {
                        **result,
                        "status": "completed",
                        "selected_model": task["selected_model"],
                        "extraction_method": task.get("extraction_method"),
                        "evaluation_metric": task.get("evaluation_metric"),
                    },
                )

                logger.info(f"Completed task {task['id']}")
            except Exception as e:
                logger.error(f"Error processing task {task['id']}: {e}")
                self.redis_client.set_result(
                    task["id"],
                    {
                        "error": str(e),
                        "status": "failed",
                        "selected_model": task["selected_model"],
                    },
                )


def main():
    parser = argparse.ArgumentParser(description="LLM Inference Worker")
    parser.add_argument("--redis-host", default="localhost")
    parser.add_argument("--redis-port", type=int, default=6380)
    parser.add_argument(
        "--redis-password", default=None, help="Redis password (if required)"
    )
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument(
        "--energy-method",
        default="zeus",
        choices=["pynvml", "zeus"],
        help="Energy measurement method",
    )
    args = parser.parse_args()
    from src.queue.redis_client import RedisClient  # only the queue worker needs redis

    redis_client = RedisClient(
        host=args.redis_host, port=args.redis_port, password=args.redis_password
    )

    model_configs = load_config("models")
    general_configs = load_config("general")
    worker = InferenceService(
        redis_client,
        general_configs,
        model_configs,
        device_id=args.device,
        energy_method=args.energy_method,
    )
    worker.run()


if __name__ == "__main__":
    main()
