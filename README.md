# Carbon-Aware Multilingual LLM Router

Contextual multi-armed bandit routing for LLM inference that trades off **multilingual accuracy** against **carbon emissions**. For each query, the router picks one model from a pool of open-weight LLMs, using the query's language, task, and complexity along with the current grid carbon intensity.

> **Status:** work in progress. The data pipeline, router features, grid data download and routing simulation are implemented; the full RunPod data collection is next.

## Acknowledgement

This project builds on the code for **GreenServ** ([TZData1/llm-inference-router](https://github.com/TZData1/llm-inference-router)), a contextual-bandit router that balances accuracy against energy. The bandit algorithms, reward, complexity and semantic-cluster features, energy measurement and inference service come from that repository. GreenServ's code that this project does not use was removed (see [Removed GreenServ code](#removed-greenserv-code)). Its commit history was squashed on import to remove a credential that appears in the upstream history. If you use this code, please cite:

```bibtex
@article{ziller2026greenserv,
  title={GreenServ: Energy-efficient context-aware dynamic routing for multi-model LLM inference},
  author={Ziller, Thomas and Ilager, Shashikant and Tundo, Alessandro and Bartocci, Ezio and Mariani, Leonardo and Brandic, Ivona},
  journal={arXiv preprint arXiv:2601.17551},
  year={2026}
}
```

## What changes from GreenServ

| | GreenServ | This project |
|---|---|---|
| Accuracy signal | English benchmarks (MMLU, GSM8K, HellaSwag, Winogrande, CNN/DM) | Multilingual benchmarks (XNLI, Belebele, MGSM) in 8 languages |
| Cost term | Energy per token | Carbon emissions = energy per query × grid carbon intensity × PUE |
| Context | Task type, semantic cluster, complexity | + grid carbon intensity, + language one-hot, + multilingual embeddings |
| Evaluation | Online regret on one stream | Online learning on training items, frozen evaluation on held-out items, across grid zones |

### Reward

```
reward = (1 − λ) · accuracy + λ · (1 − cost_norm)
```

`cost_norm` is energy per token (GreenServ), energy per query, or carbon, scaled to [0, 1]. Energy bounds are per benchmark, taken from the training items of the results being simulated; carbon additionally uses **global** intensity bounds shared by all zones (`data/grid/bounds.yaml`), so a dirty hour costs more than a clean one in every zone. The reward is identical for every router being compared; routers differ only in what they can see.

## Routers compared

Profiles live in `config/routers.yaml`; each is a cost term plus a feature list.

| Router | Cost | Context |
|---|---|---|
| `greenserv` | energy per token | benchmark, complexity, semantic cluster (English MiniLM) |
| `energy_pq` | energy per query | same as greenserv |
| `carbon` | carbon | same + carbon intensity |
| `carbon_en_emb` | carbon | benchmark, complexity, English embedding (PCA), carbon intensity |
| `carbon_onehot` | carbon | `carbon` + language one-hot |
| `carbon_ml_emb` | carbon | benchmark, complexity, multilingual embedding (PCA), carbon intensity |
| `lang_carbon` | carbon | benchmark, complexity, multilingual embedding, language one-hot, carbon intensity |

`greenserv → energy_pq → carbon` isolates per-query cost and then carbon awareness. The three ablations separate what `lang_carbon` adds: the language label alone, the multilingual encoder alone (against an English-encoder control), and both.

**Baselines**, run on the same stream as every router: `random`, `smallest`, `largest`, `best_fixed` (the best single model on the training stream, in hindsight). The **oracle** picks the best model for every query and defines regret.

**Bandit algorithms:** LinUCB (default), Thompson Sampling, ε-greedy and linear ε-greedy, in `src/bandit/`. In GreenServ's experiments LinUCB had the lowest regret, but not significantly lower than the other contextual algorithms.

## Benchmarks and languages

- **XNLI**: natural language inference (3-way)
- **Belebele**: reading comprehension (4-way multiple choice)
- **MGSM**: grade-school math (numeric answer)

Languages: **en, de, es, fr, ru, zh, th, sw** (the overlap of all three benchmarks). 250 items per benchmark, chosen once on English with balanced difficulty buckets (answer label and length) and used in every language: 750 items × 8 languages = 6,000 queries. Instructions are in English; the content is in the target language. Items are split 70/30 into train/test **by item**, so all language versions of an item fall on the same side (`data/preprocessed/splits.csv`).

## Model pool

| Family | Models |
|---|---|
| Qwen 3.5 | 2B, 9B, 27B (thinking mode off) |
| Gemma 4 | E4B, 31B |
| Multilingual | Tiny Aya Global |

Defined in `config/models.yaml`. Greedy decoding; chat templates applied with thinking disabled.

## How it works

1. **Data generation (GPU, once).** Every model answers every query on one RunPod GPU type (`data/generate.py`). Each result row stores the output, accuracy, GPU energy (J), tokens, a `truncated` flag, the GPU name, data center and timestamp. Energy depends on the model, query and hardware, not on when or where it ran, so no carbon is computed here.
2. **Router features (local, no GPU).** Query embeddings from the router's encoders are cached (`data/embed.py`); PCA and clustering are fit on training items at simulation time.
3. **Grid data (local).** Hourly carbon intensity for a fixed past year (2025) per zone (`data/fetch_grid.py`).
4. **Simulation (local).** For each zone, router and run: the training items are shuffled into a stream and the clock starts at a random hour of the zone's year. The router picks a model, receives that model's stored accuracy and energy (turned into carbon with the intensity at that step) as its reward, and updates. The policy is then frozen and evaluated on the test items. The router's own encoder energy is charged to it.

## Usage

### 1. Prepare data (local)

```bash
python data/process.py          # select items -> data/preprocessed/*.csv (250/benchmark, 8 languages)
python data/split.py            # item-level train/test split -> data/preprocessed/splits.csv
python data/embed.py            # router encoder embeddings -> data/features/
export ELECTRICITYMAPS_TOKEN=...  # keep in your shell profile, not in files
python data/fetch_grid.py       # hourly intensity per zone in config/grid.yaml -> data/grid/
#   No historical API access on your plan? Download Electricity Maps' yearly hourly CSVs and run
#   python data/fetch_grid.py --from-csv DE=path/to/DE_2025_hourly.csv FR=...
```

The selection is deterministic: re-running `process.py` gives the same items. `--samples N` selects a smaller balanced subset (the first N of the full selection) but overwrites the CSVs.

### 2. Generate results (RunPod)

```bash
# Pod: PyTorch template, one 80 GB GPU (same type for every model), >=250 GB volume at /workspace
cd /workspace && git clone <this repo> && cd carbon-aware_multilingual_router_fork
export HF_TOKEN=...                          # accept the Tiny Aya and Gemma 4 licenses on HF first
bash scripts/runpod_setup.sh                 # model cache on the volume, deps, tmux, GPU check
python data/generate.py --models qwen3.5-2b gemma-4-31b --languages en sw \
    --items-per-dataset 10 --output results/pilot.jsonl     # pilot: check outputs, accuracy, energy
tmux new -s gen
python data/generate.py 2>&1 | tee -a gen.log                # full sweep: 6,000 queries x 6 models
#   -> results/generations_<gpu>.jsonl; resumable: re-run the same command after a restart
#   Subsets: --models, --datasets, --languages (all append to the same file)
#   Parallel: one Pod per model group, same GPU type, distinct --output files
python scripts/measure_encoder_energy.py     # router encoder energy, same GPU -> results/encoder_energy_<gpu>.json
python scripts/summarize_pilot.py results/generations_<gpu>.jsonl   # accuracy, energy, truncation, sample errors
```

Copy `results/*.jsonl` and `results/encoder_energy_*.json` back to your machine (`scp`, or commit them).

### 3. Simulate routing (local)

```bash
python -m experiments.run --router lang_carbon --zone DE --results results/generations_*.jsonl
python -m experiments.run --router all --zone all --results results/generations_*.jsonl
python -m experiments.run --router lang_carbon carbon_onehot --holdout-language th --results results/generations_*.jsonl
```

Options: `--algorithm`, `--lambda`, `--pue`, `--runs`, `--models`, `--hardware`, `--seed`. Results go to `experiments/results/<timestamp>/`:

| File | Contents |
|---|---|
| `summary.csv` | per zone × router × strategy × phase: reward, cumulative regret, accuracy, grams CO₂, energy, accuracy per language, worst language and gap (mean and std over runs) |
| `choices.csv` | share of each model per language |
| `steps.csv.gz` | every decision (skip with `--no-steps`) |
| `config.json` | everything needed to reproduce the run |

`--holdout-language` removes a language from training entirely (its one-hot becomes all zeros and it never shapes PCA or clusters), to test whether embeddings generalize to an unseen language.

### Optional: Postgres

The simulation reads JSONL directly. To keep results in Postgres as well:

```bash
docker-compose -f db/docker-compose-db.yaml up -d
psql ... -f db/schema.sql
python data/ingest.py --input-file data/preprocessed/combined.csv
python data/ingest.py --results-file results/generations_<gpu>.jsonl
```

## Removed GreenServ code

GreenServ ran a live routing API and replayed results from Postgres; this project collects results once on RunPod and simulates routing locally, so the following were removed. They remain in [the upstream repository](https://github.com/TZData1/llm-inference-router) for reference.

| Removed | Why | Replaced by |
|---|---|---|
| `experiments/X1_algorithm_comparison/`, `X2_feature_ablation/`, `experiments/config/` (`experiments.yaml`, `baselines.yaml`, `mab.yaml`, copies of `config/`) | GreenServ's experiment runners and their config: English datasets, GreenServ's model pool, energy-only reward, Postgres input | `experiments/run.py` with `config/routers.yaml`; the bandit factory moved to `src/bandit/factory.py` |
| `experiments/shared/` data loader, baseline selectors, results handler, plot utils, config loader | Used only by those runners | `experiments/shared/simulation_data.py`, baselines inside `experiments/run.py` |
| `src/api/`, `src/services/orchestrator.py`, `router_service.py`, `feature_service.py`, `src/models/registry.py`, `src/queue/` and the Redis worker loop in `inference_service.py` | Live routing API and Redis task queue | `data/generate.py` calls `InferenceService` directly |
| `src/feature_extractor/task_type.py` and the `task_classification` config | Classifier over GreenServ's five English task types, needing a pickled model | The `dataset` one-hot, read from the query's benchmark |
| `src/feature_extractor/semantic_cluster.py` and the `semantic_clustering` config | Online k-means on live queries | k-means fit on training items in `experiments/shared/context_builder.py` |
| `src/metrics/normalizer.py`, `config/metrics.yaml` | Fixed energy bounds measured on GreenServ's datasets and hardware | Bounds from the training items of the results being simulated (`TrainBounds`) |
| `config/explore_dataset.py`, the Makefile's `exp01-*` targets, the API/Redis requirements | Exploration script and entry points for the removed code | |

## Repository structure

```
config/                  # datasets, models, features, router profiles, grid zones, Postgres
data/
├── process.py           # item selection and prompt formatting
├── split.py             # item-level train/test split
├── embed.py             # cached router embeddings
├── fetch_grid.py        # Electricity Maps hourly intensity
├── generate.py          # GPU data generation (accuracy + energy per query x model)
├── ingest.py            # optional Postgres loading
├── preprocessed/        # selected queries and splits (committed)
├── features/            # cached embeddings (committed)
└── grid/                # intensity series and global bounds
experiments/
├── run.py               # routing simulation (--router, --zone, ...)
└── shared/              # results loading, context builder, reward functions
results/                 # generation results and encoder energy from RunPod
scripts/                 # RunPod setup, encoder energy, pilot summary
src/
├── bandit/              # LinUCB, Thompson Sampling, ε-greedy, factory
├── feature_extractor/   # complexity, language one-hot, sentence-embedding encoder
├── metrics/             # accuracy extraction, energy, carbon, grid intensity
└── services/            # inference (generation) and answer evaluation
```

## Setup

### Prerequisites
- Python 3.10+ (on Apple silicon, use a native arm64 Python such as Homebrew's; an Intel/Rosetta build caps PyTorch at 2.2)
- A GPU for data generation (RunPod; ~80 GB VRAM for the 27B/31B models in bf16)
- Hugging Face account and token (Tiny Aya is gated)
- Electricity Maps API token, or its downloadable hourly datasets
- Docker, only for the optional Postgres database

### Installation

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt        # local: data prep, features, simulation
# On the Pod instead: pip install -r requirements-gpu.txt (via scripts/runpod_setup.sh)
export HF_TOKEN=...
export ELECTRICITYMAPS_TOKEN=...
```

Keep tokens and API keys in environment variables, not in config files.
