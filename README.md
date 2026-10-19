# Carbon-Aware Multilingual LLM Router

Contextual multi-armed bandit routing for LLM inference that trades off **multilingual accuracy** against **carbon emissions**. For each query, the router picks one model from a pool of open-weight LLMs, using the query's language, task, and complexity along with the current grid carbon intensity.

> **Status:** work in progress. This repo is being adapted from GreenServ. Sections marked *(planned)* describe the target design and aren't implemented yet.

## Acknowledgement

This project builds on the code for **GreenServ** ([TZData1/llm-inference-router](https://github.com/TZData1/llm-inference-router)), a contextual-bandit router that balances accuracy against energy. The bandit implementations, feature-extraction pipeline, and simulation framework come from that repository. Its commit history was squashed on import to remove a credential that appears in the upstream history. If you use this code, please cite:

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
| Accuracy signal | English benchmarks (MMLU, GSM8K, HellaSwag, Winogrande, CNN/DM) | Multilingual benchmarks (XNLI, Belebele, MGSM) |
| Cost term | Energy per token | Carbon emissions = energy per query × PUE × grid carbon intensity |
| Context | Task type, semantic cluster, complexity | + grid carbon intensity, + language, multilingual embeddings |
| Evaluation | Single setting | Multiple grid zones |

### Reward

```
reward = (1 − λ) · accuracy_norm + λ · (1 − cost_norm)
```

`cost` is either energy (GreenServ) or carbon (this project). Carbon is normalized with **global** bounds shared across all zones, so differences between grids stay visible in the reward.

## Routers compared

| Router | Cost | Context |
|---|---|---|
| `greenserv` | energy | task, cluster, complexity (English MiniLM embeddings) |
| `carbon` | carbon | same + carbon intensity |
| `lang_carbon` | carbon | same + language one-hot + multilingual embeddings |
| `random` | n/a | picks a random model |
| `smallest` | n/a | always the smallest model |
| `largest` | n/a | always the largest model |

Each router changes one thing from the router above it, so `greenserv → carbon` isolates carbon awareness and `carbon → lang_carbon` isolates language awareness. `lang_carbon` is also evaluated across multiple grid zones.

**Bandit algorithms:** LinUCB (primary), Thompson Sampling, and ε-greedy are in `src/bandit/`. In GreenServ's experiments LinUCB had the lowest regret, but it wasn't significantly better than the other contextual algorithms.

## Benchmarks and languages

- **XNLI**: natural language inference (3-way)
- **Belebele**: reading comprehension (4-way multiple choice)
- **MGSM**: grade-school math (numeric answer)

The languages covered by all three benchmarks are **en, de, es, fr, ru, zh, th, sw**. The final language set is still being decided, with the aim of including more low-resource languages.

## Model pool (tentative)

| Family | Models |
|---|---|
| Qwen 3.5 | 2B, 9B, 27B (thinking mode off) |
| Gemma 4 | E4B, 31B |
| Multilingual | Tiny Aya Global |

## How it works

1. **Offline data generation** *(planned)*: every model runs on every benchmark query on a RunPod GPU. Outputs, accuracy, energy, and token counts are stored in Postgres (`pregenerated_results`).
2. **Simulation**: a router replays a shuffled query stream. For each query it builds a context vector, picks a model, looks up the stored result, computes the reward, and updates the bandit. Regret is measured against the best model for each query.
3. **Carbon at simulation time** *(planned)*: only energy is stored. Carbon is computed during replay from each zone's PUE and carbon-intensity time series, so one GPU run supports any number of zones.

## Usage

### Planned interface

```bash
python -m experiments.run --router lang_carbon --algorithm linucb --zone DE --lambda 0.5
python -m experiments.run --router carbon
python -m experiments.run --router random
```

Router profiles (cost term, feature blocks, embedding model) will be defined in `experiments/config/routers.yaml`, so adding a router or an ablation only requires a config change.

### Current interface (inherited from GreenServ)

```bash
make setup        # venv, dependencies, Postgres container
make exp01-full   # run the algorithm comparison over all configured algorithms and baselines
make exp01-plot   # regenerate plots from saved results
```

## Repository structure

```
config/                 # Datasets, models, features, MAB, infrastructure
data/                   # Dataset loading, preprocessing, and DB ingestion
db/                     # Postgres schema and docker-compose
experiments/
├── config/             # Experiment-level configs (algorithms, baselines, λ)
├── shared/             # Data loading, reward/normalization, baselines, plotting
└── X1_algorithm_comparison/   # Simulation runner (template for the new experiments)
src/
├── bandit/             # LinUCB, Thompson Sampling, ε-greedy
├── feature_extractor/  # Task type, semantic cluster, complexity
├── metrics/            # Accuracy, energy, normalization
├── services/           # Orchestrator, router, feature, evaluation, inference worker
└── api/                # FastAPI endpoint
```

## Setup

### Prerequisites
- Python 3.10+
- Docker and docker-compose
- A GPU for data generation (RunPod; ~80 GB VRAM for the 27B/31B models in bf16)
- Hugging Face account and token (some models are gated)

### Installation

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
docker-compose -f db/docker-compose-db.yaml up -d
export HF_TOKEN="your_token_here"
```

Keep tokens and API keys in environment variables, not in config files.
