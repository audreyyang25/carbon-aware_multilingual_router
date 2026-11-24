# Carbon-Aware Multilingual LLM Router

Contextual multi-armed bandit routing for LLM inference that trades off **multilingual accuracy** against **carbon emissions**. For each query, the router picks one model from a pool of open-weight LLMs, using the query's language, task, and content along with the current grid carbon intensity.

> **Status:** work in progress. Data collection is done (A100 runs for the main 8 languages and for 12 extra low-resource languages on Belebele), and the routing simulation and analysis run on both. See [Results so far](#results-so-far).

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

`cost_norm` is energy per token (GreenServ), energy per query, carbon per query, or carbon per token, scaled to [0, 1]. Energy bounds are per benchmark, taken from the training items of the results being simulated; carbon additionally uses **global** intensity bounds shared by all zones (`data/grid/bounds.yaml`), so a dirty hour costs more than a clean one in every zone. Routers with the same cost term get the same reward and differ only in what they can see.

## Routers compared

Profiles live in `config/routers.yaml`; each is a cost term plus a feature list.

| Router | Cost | Context |
|---|---|---|
| `greenserv` | energy per token | benchmark, complexity, semantic cluster (English MiniLM) |
| `carbon_pt` | carbon per token | same + carbon intensity |
| `carbon_pt_lang` | carbon per token | *Extension:* `carbon_pt` + language one-hot (control for floors) |
| `carbon_pt_floor` | carbon per token | *Extension:* `carbon_pt_lang` + per-language accuracy floors |
| `energy_pq` | energy per query | same as greenserv |
| `carbon` | carbon | same + carbon intensity |
| `carbon_no_flesch` | carbon | `carbon` without complexity |
| `carbon_en_emb` | carbon | benchmark, English embedding (PCA), carbon intensity |
| `carbon_onehot` | carbon | `carbon_no_flesch` + language one-hot |
| `carbon_ml_emb` | carbon | benchmark, multilingual embedding (PCA), carbon intensity |
| `lang_carbon` | carbon | benchmark, multilingual embedding, language one-hot, carbon intensity |

**Per-language floors** (extension, not part of the main experiment; `floor:` in a profile): the router learns from reward + μ_l · (1 − λ) · accuracy, where each language's multiplier μ_l is tuned on the training stream by dual ascent. Each pass trains a fresh bandit with μ fixed, scores its frozen policy on the training items, and raises μ_l by `step` × (floor_l − accuracy_l). The floor is `ratio` × the best single model's training accuracy in that language. μ is fixed within a pass because LinUCB averages away a multiplier that drifts during training. The run log prints the final multipliers.

`greenserv → carbon_pt` adds only the grid: same per-token cost unit and features, priced in carbon. `greenserv → energy_pq → carbon` isolates per-query cost and then carbon awareness. The three ablations separate what `lang_carbon` adds: the language label alone, the multilingual encoder alone (against an English-encoder control), and both. Each is compared with `carbon_no_flesch`.

**Why our routers drop complexity:** GreenServ's complexity feature is a Flesch reading-ease bin, an English formula. On our queries, the same item lands in a different bin depending on its language. Only 46% of Russian queries share their English version's bin, because the formula can't count syllables in Cyrillic, and 94% of Russian queries fall in the easiest bin. Chinese and Thai, written without spaces, also look easy. The feature mostly separates benchmarks (already a one-hot) and leaks a rough language signal. There is no multilingual Flesch: textstat's per-language formulas don't cover zh, th or sw and aren't on a common scale. It stays in the three GreenServ-faithful routers; `carbon` vs `carbon_no_flesch` measures its effect. Multilingual embeddings describe an item nearly identically across languages, so whatever difficulty they capture transfers between languages.

**Baselines**, run on the same stream as every router: `random`, `smallest`, `largest`, `best_fixed` (the best single model on the training stream, in hindsight). The **oracle** picks the best model for every query and defines regret.

**Bandit algorithms:** LinUCB (default), Thompson Sampling, ε-greedy and linear ε-greedy, in `src/bandit/`. In GreenServ's experiments LinUCB had the lowest regret, but not significantly lower than the other contextual algorithms.

## Benchmarks and languages

- **XNLI**: natural language inference (3-way)
- **Belebele**: reading comprehension (4-way multiple choice)
- **MGSM**: grade-school math (numeric answer)

Languages: **en, de, es, fr, ru, zh, th, sw** (the overlap of all three benchmarks). 250 items per benchmark, chosen once on English, balanced by answer label (XNLI) and input length, and used in every language: 750 items × 8 languages = 6,000 queries. Instructions are in English; the content is in the target language. Items are split 70/30 into train/test **by item**, so all language versions of an item fall on the same side (`data/preprocessed/splits.csv`).

**Full run (A100, `results/generations_NVIDIA-A100-SXM4-80GB.jsonl`):** all 250 XNLI and 250 Belebele items, but only the first 100 MGSM items (`mgsm_0000`–`mgsm_0099`): 600 items × 8 languages = **4,800 queries** per model, 28,800 generations. The simulation uses exactly the queries in the results file, so this is the setup every experiment runs on. The selection in `data/preprocessed/` still lists all 250 MGSM items; leave it as is so item IDs keep matching the results. 105 tiny-aya-global answers (74 Belebele, 31 XNLI, each about 90 ms) read 0 J because the energy counter missed them; at load time the simulation replaces any 0 J reading with the median energy of the same model, benchmark and language and logs how many it replaced (`impute_missing_energy` in `experiments/simulation/data.py`).

| Benchmark | Items | Train | Test |
|---|---|---|---|
| XNLI | 250 | 175 | 75 |
| Belebele | 250 | 175 | 75 |
| MGSM | 100 | 68 | 32 |
| **Total** | **600** (4,800 queries) | 418 (3,344) | 182 (1,456) |

**Low-resource extension (Belebele only, `results/generations_lowres_NVIDIA-A100-SXM4-80GB.jsonl.gz`):** the 8 languages above are the overlap of all three benchmarks, which leaves out most low-resource languages. Belebele alone covers 122 language variants (XNLI 15, MGSM 11), so a separate run adds 12 low-resource languages on Belebele: Yoruba, Hausa, Igbo, Amharic, Zulu, Wolof, Nepali, Sinhala, Khmer, Lao, Burmese and Guarani (`config/lowres_languages.yaml`), plus en and sw re-run as anchors. It uses the same 250 Belebele items (same `item_id`, so `splits.csv` applies), prompts and models: 14 languages × 250 items × 6 models = 21,000 generations. It is kept in its own file so the main 4,800-query setup is unchanged. The anchors reproduce the main run's answers exactly; energy on that Pod reads 2–18% higher, so scale by the anchors before comparing energy across files. Accuracy per language and model, and caveats: `results/lowres_summary.md`. Rebuild the queries with `python data/process_lowres.py` (needs Hugging Face access), then `python data/generate.py --input data/preprocessed/belebele_lowres.csv --output results/generations_lowres_<gpu>.jsonl` on the Pod.

To simulate routing on the low-resource set (its queries are already embedded in `data/features/`; `data/embed.py --input data/preprocessed/belebele_lowres.csv --append` re-adds them):

```bash
python -m experiments.run --router all --zone all \
    --results results/generations_lowres_NVIDIA-A100-SXM4-80GB.jsonl.gz \
    --queries data/preprocessed/belebele_lowres.csv --output-dir experiments/results/lowres/lambda_sweep/lambda_0.5
```

The language one-hot extends to every language in the training queries (the 8 main languages keep their order), so the low-resource languages get their own columns.

## Model pool

| Family | Models |
|---|---|
| Qwen 3.5 | 2B, 9B, 27B (thinking mode off) |
| Gemma 4 | E4B, 31B |
| Multilingual | Tiny Aya Global |

Defined in `config/models.yaml`. Greedy decoding; chat templates applied with thinking disabled.

## How it works

1. **Data generation (GPU, once).** Every model answers every query on one RunPod GPU type (`data/generate.py`). Each result row stores the output, accuracy, GPU energy (J), tokens, a `truncated` flag, the GPU name, data center and timestamp. Multiple-choice answers are scored on the first standalone letter, so an answer cut off after its letter still counts. An MGSM answer that hits `max_new_tokens` without writing an `Answer:` line scores 0: its last number is usually an intermediate step, and the energy was spent without producing an answer. Energy depends on the model, query and hardware, not on when or where it ran, so no carbon is computed here.
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
python scripts/preflight.py --download       # GPU exclusive, energy counter, HF access, disk; downloads weights
python data/generate.py --items-per-dataset 5 \
    --output results/pilot_runpod.jsonl      # pilot: all 6 models x 8 languages, 720 generations
python scripts/summarize_generations.py results/pilot_runpod.jsonl --project   # check outputs, accuracy, energy; projected run time
tmux new -s gen
python data/generate.py 2>&1 | tee -a gen.log                # full sweep: 6,000 queries x 6 models
#   The A100 full run stopped MGSM at 100 items (4,800 queries x 6 models); see "Benchmarks and languages"
#   -> results/generations_<gpu>.jsonl; resumable: re-run the same command after a restart
#   Subsets: --models, --datasets, --languages (all append to the same file)
#   Parallel: one Pod per model group, same GPU type, distinct --output files
python scripts/measure_encoder_energy.py     # router encoder energy, same GPU -> results/encoder_energy_<gpu>.json
python scripts/summarize_generations.py results/generations_<gpu>.jsonl   # accuracy, energy, truncation, sample errors
```

Copy `results/*.jsonl` and `results/encoder_energy_*.json` back to your machine (`scp`, or commit them).

### 3. Simulate routing (local)

```bash
python -m experiments.run --router lang_carbon --zone DE --results results/generations_*.jsonl
python -m experiments.run --router all --zone all --results results/generations_*.jsonl
python -m experiments.run --router lang_carbon carbon_onehot --holdout-language th --results results/generations_*.jsonl
```

Options: `--algorithm`, `--lambda`, `--pue`, `--runs`, `--models`, `--hardware`, `--seed`, `--pca-dim`, `--queries-per-hour`. Results go to `experiments/results/<timestamp>/`:

| File | Contents |
|---|---|
| `summary.csv` | per zone × router × strategy × phase: reward, cumulative regret, accuracy, grams CO₂, energy, accuracy per language, worst language and gap (mean and std over runs) |
| `choices.csv` | share of each model per language |
| `steps.csv.gz` | every decision (skip with `--no-steps`) |
| `config.json` | everything needed to reproduce the run |

`--queries-per-hour` sets the simulation clock: on the A100 full run (3,344 training and 1,456 test queries) the default 250 gives about 13 hours of training and the 6 hours after for test; 25 gives about 5.5 days of training and 2.5 days of test, so the router sees several full day/night cycles and most of a week. Reporting both shows whether conclusions depend on how much grid variation the router saw.

`--pca-dim` sets the embedding size (default 32 in `config/feature_extraction.yaml`). At 16 dimensions only 26% of translated queries still have their English version as nearest neighbour under multilingual-e5 (97% with the full embedding), so the router would mostly see benchmark and language, which it already gets from the one-hots; 32 recovers 68%. Sweep it (e.g. 8, 16, 32, 64), choosing by training-phase reward.

`--holdout-language` removes a language from training entirely (its one-hot becomes all zeros and it never shapes PCA or clusters), to test whether embeddings generalize to an unseen language.

### 4. Analyze

```bash
python -m experiments.analyze_per_lambda experiments/results/lambda_sweep/lambda_<λ>/<timestamp>
```

Writes `analysis/` inside the run folder (needs `steps.csv.gz`, so don't use `--no-steps`):

| File | Contents |
|---|---|
| `report.md` | the tables below in markdown, for slides |
| `headline.csv` | test phase per zone and averaged over zones: accuracy, worst-language accuracy, gCO₂ per 1,000 queries, J per query (mean and std over runs) |
| `by_language.csv` | test accuracy per strategy × language |
| `by_benchmark.csv` | test accuracy, gCO₂ per 1,000 queries and J per query per strategy × benchmark, plus carbon as % of always using the largest model and each benchmark's share of total carbon. Pooled carbon in `headline.csv` is almost entirely MGSM (an MGSM answer uses about 100× the energy of an XNLI or Belebele one), so read this table for XNLI and Belebele |
| `comparisons.csv` | paired differences (e.g. `lang_carbon` vs `largest`, vs each ablation): accuracy in points and carbon in %, with 95% bootstrap CIs over test items, per zone and pooled |
| `tradeoff.png` | accuracy vs carbon per zone, routers against baselines and the oracle |
| `language_accuracy.png` | accuracy heatmap, strategy × language |
| `model_share.png` | which model each router picks for each language |
| `carbon_awareness.png` | energy of the chosen model vs grid intensity |
| `learning_curve.png` | regret during training |

The bootstrap resamples items (one question in all 8 languages), not single queries, because the translations of one item and repeated runs over the same items aren't independent.

Routers that land at different carbon levels can't be compared fairly at a single λ. A λ sweep is just `run.py` at several λ, each into its own folder, then `analyze` on each run and `lambda_compare` over all of them. These commands regenerate every folder of the stored main-set sweep in `experiments/results/lambda_sweep/`:

```bash
S=experiments/results/lambda_sweep
DATA="--results results/generations_NVIDIA-A100-SXM4-80GB.jsonl"
BASE="greenserv energy_pq carbon carbon_no_flesch carbon_en_emb carbon_onehot carbon_ml_emb lang_carbon"
for l in 0.3 0.5 0.7 0.9; do
    python -m experiments.run --router $BASE                         --zone all --lambda $l $DATA --output-dir $S/lambda_$l
    python -m experiments.run --router carbon_pt --zone all --lambda $l $DATA --output-dir $S/carbon_pt/lambda_$l
done
for run in $S/lambda_*/*/ $S/*/lambda_*/*/; do python -m experiments.analyze_per_lambda $run; done
python -m experiments.lambda_compare $S/comparison \
    $(for sub in "" carbon_pt/; do for l in 0.3 0.5 0.7 0.9; do echo $l=$(ls -d $S/${sub}lambda_$l/*/); done; done) \
    --levels 20 30 40 50 60
```

For the low-resource sweep, set `S=experiments/results/lowres/lambda_sweep` and `DATA="--results results/generations_lowres_NVIDIA-A100-SXM4-80GB.jsonl.gz --queries data/preprocessed/belebele_lowres.csv"`, and drop `--levels` (it uses the default levels). Everything else (LinUCB, 5 runs, seed 40, 250 queries per hour) is the default.

`carbon_pt` has its own folder only because it was added after the first sweep. A router's results don't depend on which other routers run alongside it, so `$BASE carbon_pt` in one run gives the same numbers in one folder (`--router all` would also add the floor extension routers). `lambda_compare` keeps the first run listed for each strategy at a λ, so list the base runs first, as above.

The per-language floor extension (`carbon_pt_lang`, `carbon_pt_floor`) is kept apart in `experiments/results/extensions/floor/{main,lowres}/`, with a comparison that adds it to the main curves:

```bash
E=experiments/results/extensions/floor/main   # or .../floor/lowres, with the low-resource DATA and S
for l in 0.3 0.5 0.7 0.9; do
    python -m experiments.run --router carbon_pt_lang carbon_pt_floor --zone all --lambda $l $DATA --output-dir $E/lambda_$l
done
for run in $E/lambda_*/*/; do python -m experiments.analyze_per_lambda $run; done
python -m experiments.lambda_compare $E/comparison \
    $(for d in $S $S/carbon_pt $E; do for l in 0.3 0.5 0.7 0.9; do echo $l=$(ls -d $d/lambda_$l/*/); done; done) \
    --levels 20 30 40 50 60
```

Each λ gives every router one (carbon, accuracy) point; `matched_carbon.csv` reads each router's curve at common carbon levels by linear interpolation between neighbouring λ runs, and `lambda_tradeoff.png` plots the curves. `ablation.csv` lists the feature ablation chain (greenserv → carbon_pt, greenserv → energy_pq → carbon → carbon_no_flesch → carbon_en_emb → carbon_ml_emb → lang_carbon, plus carbon_onehot) at those levels, one change per step, with worst-language accuracy. `model_mix.csv` and `model_mix_by_zone.csv` give each router's test-phase share of queries per model at every λ.

Finally, the headline figures:

```bash
python -m experiments.main_analysis          # -> results/figures/main_analysis/fig1–fig4
```

It reads only the outputs above (`lambda_headline.csv`, `model_mix*.csv` and each run's `headline.csv`) for both sets. GreenServ and `carbon_pt` are compared at the pair of λ where their accuracy is closest, chosen from the curves (currently 0.3 vs 0.7 on the main set, 0.3 vs 0.5 on the low-resource set): model mix by zone, carbon vs accuracy, the per-zone change, and how language features change the model mix.

## Results so far

All runs use LinUCB, 5 runs per zone, 6 grid zones; numbers are test-phase averages over zones. Full tables and figures are in each run's `analysis/report.md`.

| Run | Folder |
|---|---|
| Main 8 languages, all routers at λ = 0.3, 0.5, 0.7, 0.9 (`lambda_<λ>/`), and the matched-carbon comparison (`comparison/`) | `experiments/results/lambda_sweep/` |
| 12 low-resource languages + en/sw on Belebele, same layout | `experiments/results/lowres/lambda_sweep/` |
| `carbon_pt` alone at λ = 0.3, 0.5, 0.7, 0.9 (added later; merged into both comparisons) | `lambda_sweep/carbon_pt/`, `lowres/lambda_sweep/carbon_pt/` |
| *Extension:* `carbon_pt_lang` and `carbon_pt_floor` at λ = 0.3, 0.5, 0.7, 0.9, with their own comparisons | `experiments/results/extensions/floor/main/`, `.../floor/lowres/` |
| *Extension:* agreement cascade on stored answers, paired with the λ = 0.5 test streams | `experiments/results/extensions/cascade/main/`, `.../cascade/lowres/` |

- **vs always using the largest model:** `lang_carbon` uses 16% less carbon for 1.2 points of accuracy on the main set. On the low-resource set it saves 14% but loses 4.4 points.
- **Grid awareness beats GreenServ at matched carbon once the cost unit is held fixed.** `carbon_pt` (GreenServ + grid, carbon per token) beats `greenserv` by 3.2 points at 20 g per 1k and 2.0 at 30 g on the main set (weakest language +3.9 and +2.4), and by 1.6–5.3 points at 4–7 g on the low-resource set. It sends queries to the largest model on clean grids (France, Sweden) and to small models on dirty ones; GreenServ's mix is identical in every zone. At 30 g it is also 1.6 points above `best_fixed`, the only router above it at any compared level. On the main set the per-token cost unit beats per query (`carbon_pt` over `carbon` by 2–4 points, `greenserv` over `energy_pq` by about 7); on the low-resource set per query is slightly better (`carbon` 0.777 vs `carbon_pt` 0.765 at 5 g).
- **Extension, not part of the main experiment: per-language floors help a little on the main set and hurt on the low-resource set.** On the main set `carbon_pt_floor` is 0.5–0.7 points above `carbon_pt` at 40–50 g per 1k, and has the best weakest-language accuracy of any strategy at 40 g (0.799, vs 0.783 for `best_fixed`). Floors also stop accuracy collapsing at high λ (0.836 at λ = 0.9 vs 0.776). On the low-resource set it is below `carbon_pt` at 6 g (0.780 vs 0.789; weakest language 0.494 vs 0.544). The language one-hot it needs to act per language overfits with 175 training queries per language: the control without floors (`carbon_pt_lang`) loses about 7 points on the weakest language. Only 75 test items per low-resource language, so weakest-language differences under about 5 points are within noise.
- **Extension, not part of the main experiment: the agreement cascade loses on both sets** (`experiments/extensions/cascade.py`). Two cheap models answer; if they agree, keep the answer, otherwise escalate. When qwen3.5-2b and tiny-aya agree on the main set they are right 87% of the time (gemma-e4b + tiny-aya: 93%), but pairs disagree on 37–39% of main-set queries and 38–53% of low-resource ones, and running two models costs too much: on MGSM, which is about 96% of carbon, the pair uses 2,300 J against 3,160 J for qwen3.5-9b. Every cascade is below `carbon_pt` at the same carbon (best: 0.841 at 46 g vs 0.855), and on the low-resource set every cascade uses more carbon than always using the largest model. Sending clean-grid queries straight to the largest model (`(grid)` variants) helps a little but not enough.
- **Language features** (`ablation.csv`): on the main set the gain over `carbon_no_flesch` (about 1.5–2 points) comes from replacing the topic clusters with the full embedding; the English encoder does as well as the multilingual one and the language one-hot adds nothing on top. On the low-resource set every step lowers accuracy slightly, and the one-hot alone hurts the weakest language.
- **The best single model chosen on training data (`best_fixed`) is hard to beat.** On the low-resource set it beats every router at every compared carbon level (3–6 g per 1k); at λ = 0.5 it is simply the largest model. On the main set its curve spans only 30–40 g per 1k: at 40 g it beats every router (0.864 vs 0.851 for `carbon_pt`, the best router), and at 30 g only `carbon_pt` is above it (0.839 vs 0.823). The language features don't help there even at matched carbon (`lang_carbon` is 0.9 points below `carbon_no_flesch` at 5 and 6 g per 1k), and the one-hot router does worst on Wolof (0.46 vs 0.60 at λ = 0.5).
- **Pooled carbon is about 96% MGSM**, so `by_benchmark.csv` is the table to read for XNLI and Belebele.
- Offline checks suggest which model gets a question right depends mostly on the specific question, not its language. When the two small models agree, qwen3.5-2b is right 92% of the time vs 56% when they disagree, a stronger routing signal than anything in the question text.

## Removed GreenServ code

GreenServ ran a live routing API and replayed results from Postgres; this project collects results once on RunPod and simulates routing locally, so the following were removed. They remain in [the upstream repository](https://github.com/TZData1/llm-inference-router) for reference.

| Removed | Why | Replaced by |
|---|---|---|
| `experiments/X1_algorithm_comparison/`, `X2_feature_ablation/`, `experiments/config/` (`experiments.yaml`, `baselines.yaml`, `mab.yaml`, copies of `config/`) | GreenServ's experiment runners and their config: English datasets, GreenServ's model pool, energy-only reward, Postgres input | `experiments/run.py` with `config/routers.yaml`; the bandit factory moved to `src/bandit/factory.py` |
| `experiments/shared/` data loader, baseline selectors, results handler, plot utils, config loader | Used only by those runners | `experiments/simulation/data.py`, baselines inside `experiments/run.py` |
| `src/api/`, `src/services/orchestrator.py`, `router_service.py`, `feature_service.py`, `src/models/registry.py`, `src/queue/` and the Redis worker loop in `inference_service.py` | Live routing API and Redis task queue | `data/generate.py` calls `InferenceService` directly |
| `src/feature_extractor/task_type.py` and the `task_classification` config | Classifier over GreenServ's five English task types, needing a pickled model | The `dataset` one-hot, read from the query's benchmark |
| `src/feature_extractor/semantic_cluster.py` and the `semantic_clustering` config | Online k-means on live queries | k-means fit on training items in `experiments/simulation/features.py` |
| `src/metrics/normalizer.py`, `config/metrics.yaml` | Fixed energy bounds measured on GreenServ's datasets and hardware | Bounds from the training items of the results being simulated (`TrainBounds`) |
| `config/explore_dataset.py`, the Makefile's `exp01-*` targets, the API/Redis requirements | Exploration script and entry points for the removed code | |
| `db/` (Postgres schema, connection, Docker Compose), `data/ingest.py`, `config/infrastructure.yaml`, the Makefile's database targets | Optional Postgres copy of queries and results; nothing in the pipeline read it | `experiments/run.py` reads the results JSONL directly |

## Repository structure

```
config/                  # datasets, models, features, router profiles, grid zones, low-resource languages
data/
├── process.py           # item selection and prompt formatting (main 8 languages)
├── process_lowres.py    # Belebele queries for the extra low-resource languages
├── split.py             # item-level train/test split
├── embed.py             # cached router embeddings (--append adds new queries)
├── fetch_grid.py        # Electricity Maps hourly intensity
├── generate.py          # GPU data generation (accuracy + energy per query x model)
├── helper.py, load.py   # benchmark loading and preprocessing used by process*.py
├── preprocessed/        # selected queries and splits (committed)
├── features/            # cached embeddings for all 9,000 queries (committed)
└── grid/                # hourly intensity per zone and global bounds
experiments/
├── run.py               # routing simulation (--router, --zone, --lambda, ...)
├── analyze_per_lambda.py # tables, paired comparisons and figures for one run (one λ)
├── lambda_compare.py    # accuracy-vs-carbon curves and matched-carbon comparison across λ
├── main_analysis.py     # headline figures (GreenServ vs carbon_pt) from analyze + lambda_compare outputs
├── simulation/          # data.py (results loading), features.py (router context), rewards.py
├── extensions/          # side experiments, not part of the main result: cascade.py (agreement cascade)
└── results/             # lambda_sweep/, lowres/lambda_sweep/, extensions/ (cascade, floor)
results/                 # RunPod outputs: generations (main + low-resource), encoder energy; figures/main_analysis/
scripts/                 # RunPod setup, preflight checks, encoder energy, results summary
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

### Installation

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt        # local: data prep, features, simulation
# On the Pod instead: pip install -r requirements-gpu.txt (via scripts/runpod_setup.sh)
export HF_TOKEN=...
export ELECTRICITYMAPS_TOKEN=...
```

Keep tokens and API keys in environment variables set from your home-directory shell profile (`~/.zshrc`), not in files inside the repo. `.gitignore` excludes `.zshrc`, `.bashrc` and `.env` files as a safety net.
