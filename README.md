# Carbon-Aware Multilingual LLM Router

Contextual multi-armed bandit routing for LLM inference that trades off **multilingual accuracy** against **carbon emissions**. For each query, the router picks one model from a pool of open-weight LLMs, using the query's language, task and content along with the current grid carbon intensity.

Every model answered every query once on one GPU (RunPod A100), with its accuracy and energy recorded. Routing is then simulated offline on those stored answers, across six grid zones and a full year of hourly carbon intensity. All files needed to rerun the simulations and rebuild every table and figure are committed; see [Reproducing the results](#reproducing-the-results).

**Main findings:** making the router carbon-aware changes which models it picks: it uses the largest model on clean grids and small models on dirty ones. Against GreenServ's energy-only router at about the same overall accuracy, it uses 12% less carbon on the main set and 14% less on the low-resource set. In clean-grid zones (France, Sweden) it spends a few extra grams for 4–5 more points of accuracy; in the dirtiest zone (Poland) it cuts carbon by 44% at an accuracy cost. Language features (language label, multilingual encoder) barely change accuracy or model choice. See [Results](#results).

## Contents

- [Acknowledgement](#acknowledgement)
- [What changes from GreenServ](#what-changes-from-greenserv)
- [Experimental design](#experimental-design)
- [Reproducing the results](#reproducing-the-results)
- [Results](#results)
- [Extensions (not part of the main experiment)](#extensions-not-part-of-the-main-experiment)
- [Repository structure](#repository-structure)
- [Removed GreenServ code](#removed-greenserv-code)
- [Setup](#setup)

## Acknowledgement

This project builds on the code for **GreenServ** ([TZData1/llm-inference-router](https://github.com/TZData1/llm-inference-router)), a contextual-bandit router that balances accuracy against energy. The bandit algorithms, reward, complexity and semantic-cluster features, energy measurement and inference service come from that repository. GreenServ's code that this project does not use was removed (see [Removed GreenServ code](#removed-greenserv-code)); a few unused GreenServ functions and files remain and are marked as leftovers in a comment. Its commit history was squashed on import to remove a credential that appears in the upstream history. If you use this code, please cite:

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
| Accuracy signal | English benchmarks (MMLU, GSM8K, HellaSwag, Winogrande, CNN/DM) | Multilingual benchmarks (XNLI, Belebele, MGSM) in 8 languages, plus 12 low-resource languages on Belebele |
| Cost term | Energy per token | Carbon emissions = energy × grid carbon intensity × PUE (per query or per token) |
| Context | Task type, semantic cluster, complexity | + grid carbon intensity, + language one-hot, + multilingual embeddings |
| Evaluation | Online regret on one stream, one λ | Online learning on training items, frozen evaluation on held-out items, across six grid zones, compared at matched carbon across a λ sweep |

## Experimental design

### Benchmarks and languages

- **XNLI**: natural language inference (3-way)
- **Belebele**: reading comprehension (4-way multiple choice)
- **MGSM**: grade-school math (numeric answer)

Languages: **en, de, es, fr, ru, zh, th, sw** (the overlap of all three benchmarks). 250 items per benchmark are chosen once on English and used in every language. The selection is balanced by answer label (XNLI) and input length (`sampling_strata` in `data/process.py`); MGSM has exactly 250 items, so it uses all of them. Instructions are in English and the content is in the target language. Items are split 70/30 into train/test **by item**, so all language versions of an item fall on the same side (`data/preprocessed/splits.csv`).

**What was actually run (A100):** all 250 XNLI and 250 Belebele items, but only the first 100 MGSM items (`mgsm_0000`–`mgsm_0099`): 600 items × 8 languages = **4,800 queries** per model, 28,800 generations (`runpod_generations/generations_NVIDIA-A100-SXM4-80GB.jsonl`). The simulation uses exactly the queries in the results file, so this is the setup every experiment runs on. `data/preprocessed/` still lists all 250 MGSM items; leave it as is so item IDs keep matching the results.

| Benchmark | Items | Train | Test |
|---|---|---|---|
| XNLI | 250 | 175 | 75 |
| Belebele | 250 | 175 | 75 |
| MGSM | 100 | 68 | 32 |
| **Total** | **600** (4,800 queries) | 418 (3,344) | 182 (1,456) |

**Low-resource set (Belebele only):** the 8 languages above leave out most low-resource languages. Belebele alone covers 122 language variants (XNLI 15, MGSM 11), so a second run adds 12 low-resource languages on Belebele: Yoruba, Hausa, Igbo, Amharic, Zulu, Wolof, Nepali, Sinhala, Khmer, Lao, Burmese and Guarani (`config/lowres_languages.yaml`), plus en and sw re-run as anchors. It uses the same 250 Belebele items (same `item_id`, so `splits.csv` applies), prompts and models: 14 languages × 250 items × 6 models = 21,000 generations, kept in its own file (`runpod_generations/generations_lowres_NVIDIA-A100-SXM4-80GB.jsonl.gz`). The anchors reproduce the main run's answers exactly; energy on that Pod reads 2–18% higher, so scale by the anchors before comparing energy across files. Accuracy per language and model, and caveats: `runpod_generations/lowres_summary.md`.

### Model pool

| Family | Models |
|---|---|
| Qwen 3.5 | 2B, 9B, 27B |
| Gemma 4 | E4B, 31B |
| Multilingual | Tiny Aya Global |

Defined in `config/models.yaml`. Greedy decoding; chat templates applied with thinking disabled. All models ran on the same GPU type (A100-SXM4-80GB), so energy is comparable across models.

### Scoring and energy

- **Accuracy.** Multiple-choice answers (XNLI, Belebele) are scored on the first standalone A–D letter, so an answer cut off after its letter still counts. MGSM is scored on the number after `Answer:`. An MGSM answer that hits `max_new_tokens` without writing an `Answer:` line scores 0: its last number is usually an intermediate step, and the energy was spent without producing an answer.
- **Energy.** GPU energy per generation, read with Zeus over the whole generation (idle power included). 105 tiny-aya-global answers (74 Belebele, 31 XNLI, each about 90 ms) read 0 J because the energy counter missed them; at load time the simulation replaces any 0 J reading with the median energy of the same model, benchmark and language and logs how many it replaced (`impute_missing_energy` in `experiments/simulation/data.py`).
- **Router overhead.** Routers that embed the query are charged their encoder's energy per query, measured on the same GPU (`runpod_generations/encoder_energy_<gpu>.json`). It is added to reported energy and carbon but not to the reward, since it is the same whichever model is picked.
- **Carbon.** Hourly carbon intensity for 2025 in six zones (`config/grid.yaml`): France, Sweden (SE-SE3), Germany, California (US-CAL-CISO), New England (US-NE-ISNE) and Poland. Carbon = energy × intensity × PUE (PUE 1.0; a constant PUE only scales grams).

### Reward

```
reward = (1 − λ) · accuracy + λ · (1 − cost_norm)
```

`cost_norm` is energy per token (GreenServ), energy per query, carbon per query or carbon per token, min-max scaled to [0, 1]. Energy bounds are per benchmark (an MGSM answer uses about 100× the energy of an XNLI or Belebele one), taken from the training items only. Carbon also uses **global** intensity bounds shared by all zones (`data/grid/bounds.yaml`), so a dirty hour costs more than a clean one in every zone. Routers with the same cost term get the same reward and differ only in what they can see.

### Routers

Profiles live in `config/routers.yaml`; each is a cost term plus a feature list. All use LinUCB (`alpha` 0.1, `regularization` 0.05, GreenServ's values).

| Router | Cost | Context |
|---|---|---|
| `greenserv` | energy per token | benchmark, complexity, semantic cluster (English MiniLM) |
| `carbon_pt` | carbon per token | same + carbon intensity |
| `energy_pq` | energy per query | same as greenserv |
| `carbon` | carbon per query | same + carbon intensity |
| `carbon_no_flesch` | carbon per query | `carbon` without complexity |
| `carbon_en_emb` | carbon per query | benchmark, English embedding (PCA), carbon intensity |
| `carbon_onehot` | carbon per query | `carbon_no_flesch` + language one-hot |
| `carbon_ml_emb` | carbon per query | benchmark, multilingual embedding (PCA), carbon intensity |
| `lang_carbon` | carbon per query | benchmark, multilingual embedding, language one-hot, carbon intensity |

The comparisons are built so each step changes one thing:

- **Grid awareness:** `greenserv → carbon_pt` adds only the grid (same per-token cost unit and features, priced in carbon). `greenserv → energy_pq → carbon` isolates per-query cost and then carbon awareness.
- **Language features:** starting from `carbon_no_flesch`, the chain adds the full English embedding (`carbon_en_emb`), swaps in a multilingual encoder (`carbon_ml_emb`) and adds the language label (`lang_carbon`). `carbon_onehot` adds the language label alone, without an embedding.

**Why our routers drop complexity:** GreenServ's complexity feature is a Flesch reading-ease bin, an English formula. On our queries, the same item lands in a different bin depending on its language. Only 46% of Russian queries share their English version's bin, because the formula can't count syllables in Cyrillic, and 94% of Russian queries fall in the easiest bin. Chinese and Thai, written without spaces, also look easy. The feature mostly separates benchmarks (already a one-hot) and leaks a rough language signal. There is no multilingual Flesch: textstat's per-language formulas don't cover zh, th or sw and aren't on a common scale. It stays in the three GreenServ-faithful routers; `carbon` vs `carbon_no_flesch` measures its effect.

**Baselines**, run on the same stream as every router: `random`, `smallest`, `largest`, `best_fixed` (the best single model on the training stream, in hindsight). The **oracle** picks the best model for every query and defines regret.

### Simulation

For each zone, router and run (5 runs, seed 40 + run), `experiments/run.py`:

1. shuffles the training items (all languages) into a stream and starts the clock at a random hour of the zone's 2025 series, with 250 queries per hour of grid time;
2. lets the router pick a model for each query, gives it that model's stored accuracy and energy (turned into carbon at that hour) as its reward, and updates it;
3. freezes the policy (no exploration, no updates) and evaluates it on the test items;
4. runs every baseline and the oracle on the same stream and hours, so every comparison is paired.

A router's results don't depend on which other routers run alongside it. Embedding PCA (32 dimensions), the 3 semantic clusters and energy bounds are fit on training items only.

### Evaluation

- **Per run** (`analyze_per_lambda.py`): test-phase accuracy, worst-language accuracy, gCO₂ per 1,000 queries and J per query, per zone and averaged over zones; paired differences with 95% bootstrap CIs. The bootstrap resamples items (one question in all languages), not single queries, because translations of one item aren't independent.
- **Across λ** (`lambda_compare.py`): λ is a preference, not something to tune, and the same λ lands routers with different cost terms at different carbon levels. So each router runs at λ = 0.3, 0.5, 0.7 and 0.9, each λ gives one (carbon, accuracy) point, and routers are compared by reading their curves at the same carbon level (linear interpolation between neighbouring λ). This is **accuracy at matched carbon**.
- **Headline figures** (`main_analysis.py`): GreenServ and `carbon_pt` at the λ pair where their accuracy is closest, i.e. **carbon saved at matched accuracy**.

## Reproducing the results

Three levels, depending on how far back you want to go. Levels 1 and 2 run on a laptop from committed files and need no GPU or API token. Run everything from the repository root.

| Level | Starts from | Needs | Rebuilds |
|---|---|---|---|
| 1. Figures | stored comparisons in `experiments/results/` | nothing | the main figures and most appendix figures |
| 2. Simulation | committed generations, queries, embeddings and grid data | CPU | every run, analysis, comparison and figure |
| 3. Full pipeline | Hugging Face datasets | RunPod GPU, HF token, Electricity Maps access | everything, including the generations |

### Level 1: main figures

```bash
python -m experiments.main_analysis     # -> experiments/results/figures/main_analysis/fig1–fig4
```

Reads `lambda_headline.csv` and `model_mix*.csv` from each set's `comparison/`, and each run's `analysis/headline.csv`.

```bash
python -m experiments.appendix_analysis # -> experiments/results/figures/appendix/figA1–figA5
```

figA3–figA5 read committed files only. figA1 and figA2 need the per-decision `steps.csv.gz` of the GreenServ and `carbon_pt` runs in the figure pair, which are not committed; without them the script skips those two and says which run to re-run (Level 2).

### Level 2: simulations and analysis

`steps.csv.gz` (every decision) is too large to commit, so `analyze_per_lambda` can only run on a stored run after re-running its simulation. Re-running reproduces the stored numbers: results depend only on the seed, the stored generations and the committed data.

**Main set (8 languages)**, all routers at λ = 0.3, 0.5, 0.7, 0.9:

```bash
S=experiments/results/lambda_sweep
DATA="--results runpod_generations/generations_NVIDIA-A100-SXM4-80GB.jsonl"
BASE="greenserv energy_pq carbon carbon_no_flesch carbon_en_emb carbon_onehot carbon_ml_emb lang_carbon"
for l in 0.3 0.5 0.7 0.9; do
    python -m experiments.run --router $BASE     --zone all --lambda $l $DATA --output-dir $S/lambda_$l
    python -m experiments.run --router carbon_pt --zone all --lambda $l $DATA --output-dir $S/carbon_pt/lambda_$l
done
for run in $S/lambda_*/*/ $S/*/lambda_*/*/; do python -m experiments.analyze_per_lambda $run; done
python -m experiments.lambda_compare $S/comparison \
    $(for sub in "" carbon_pt/; do for l in 0.3 0.5 0.7 0.9; do echo $l=$(ls -d $S/${sub}lambda_$l/*/); done; done) \
    --levels 20 30 40 50 60
```

**Low-resource set** (Belebele, 14 languages), same routers and λ:

```bash
S=experiments/results/lowres/lambda_sweep
DATA="--results runpod_generations/generations_lowres_NVIDIA-A100-SXM4-80GB.jsonl.gz --queries data/preprocessed/belebele_lowres.csv"
# then the same two loops and lambda_compare call as above, without --levels (it uses its default levels)
```

Then rebuild the figures with Level 1. Each `run.py` call writes a new `<timestamp>/` folder inside its `--output-dir`; if you re-run into the stored folders, remove the old timestamp folders first so `ls -d` finds one run per λ.

Notes:

- `carbon_pt` has its own folder only because it was added after the first sweep. `--router $BASE carbon_pt` in one run gives the same numbers. Avoid `--router all` for the main sweep: it also runs the floor extension routers.
- `lambda_compare` keeps the first run listed for each strategy at a λ (baselines appear in every run), so list the base runs first, as above.
- The low-resource language one-hot extends to every language in the training queries (the 8 main languages keep their order), so the low-resource languages get their own columns.

Other `run.py` options: `--algorithm`, `--pue`, `--runs`, `--models`, `--hardware`, `--seed`, `--pca-dim`, `--queries-per-hour`, `--holdout-language`.

- `--queries-per-hour` sets the simulation clock. On the main set (3,344 training and 1,456 test queries) the default 250 gives about 13 hours of training and the following 6 hours for test; 25 gives about 5.5 days of training and 2.5 days of test, so the router sees several day/night cycles.
- `--pca-dim` sets the embedding size (default 32, `config/feature_extraction.yaml`). At 16 dimensions only 26% of translated queries still have their English version as nearest neighbour under multilingual-e5 (97% with the full embedding); 32 recovers 68%.
- `--holdout-language` removes a language from training entirely (its one-hot becomes all zeros and it never shapes PCA or clusters), to test whether embeddings generalize to an unseen language. No stored result uses it.

### Level 3: full pipeline

**1. Prepare data (local).** Outputs are committed, so this is only needed to rebuild them.

```bash
python data/process.py            # select items -> data/preprocessed/*.csv (250/benchmark, 8 languages)
python data/split.py              # item-level train/test split -> data/preprocessed/splits.csv
python data/process_lowres.py     # Belebele queries for the low-resource languages -> data/preprocessed/belebele_lowres.csv
python data/embed.py              # router encoder embeddings -> data/features/
python data/embed.py --input data/preprocessed/belebele_lowres.csv --append
export ELECTRICITYMAPS_TOKEN=...  # keep in your shell profile, not in files
python data/fetch_grid.py         # hourly intensity per zone in config/grid.yaml -> data/grid/
#   No historical API access on your plan? Download Electricity Maps' yearly hourly CSVs and run
#   python data/fetch_grid.py --from-csv DE=path/to/DE_2025_hourly.csv FR=...
```

The selection is deterministic: re-running `process.py` gives the same items. `--samples N` selects a smaller balanced subset (the first N of the full selection) but overwrites the CSVs. `python data/load.py --datasets mgsm --languages en sw` downloads benchmark splits without processing them.

**2. Generate answers and energy (RunPod).**

```bash
# Pod: PyTorch template, one 80 GB GPU (same type for every model), >=250 GB volume at /workspace
cd /workspace && git clone https://github.com/audreyyang25/carbon-aware_multilingual_router.git && cd carbon-aware_multilingual_router
export HF_TOKEN=...                          # accept the Tiny Aya and Gemma 4 licenses on HF first
bash scripts/runpod_setup.sh                 # model cache on the volume, deps, tmux, GPU check
python scripts/preflight.py --download       # GPU exclusive, energy counter, HF access, disk; downloads weights
python data/generate.py --items-per-dataset 5 --output runpod_generations/pilot_runpod.jsonl   # pilot: 720 generations
python scripts/summarize_generations.py runpod_generations/pilot_runpod.jsonl --project       # sanity checks; projected run time
tmux new -s gen
python data/generate.py 2>&1 | tee -a gen.log                # full run -> runpod_generations/generations_<gpu>.jsonl
python data/generate.py --input data/preprocessed/belebele_lowres.csv \
    --output runpod_generations/generations_lowres_<gpu>.jsonl          # low-resource set
python scripts/measure_encoder_energy.py     # router encoder energy, same GPU -> runpod_generations/encoder_energy_<gpu>.json
python scripts/summarize_generations.py runpod_generations/generations_<gpu>.jsonl   # accuracy, energy, truncation, sample errors
```

`generate.py` is resumable (re-run the same command after a restart) and takes `--models`, `--datasets` and `--languages` to run subsets, which append to the same file. To parallelize, use one Pod per model group, the same GPU type, and distinct `--output` files. The stored A100 run stopped MGSM at 100 items (see [Benchmarks and languages](#benchmarks-and-languages)). Copy `runpod_generations/` back to your machine (`scp`, or commit it), then continue with Level 2.

## Results

All runs use LinUCB, 5 runs per zone, 6 grid zones; numbers are test-phase averages over zones.

### Main figures

From `python -m experiments.main_analysis`, in `experiments/results/figures/main_analysis/`. GreenServ and `carbon_pt` are compared at the λ pair with the closest accuracy (main set 0.3 vs 0.7, low-resource set 0.3 vs 0.5).

| Figure | Shows |
|---|---|
| `fig1_model_mix_by_zone.png` | Model share on test queries: GreenServ (the same in every zone) vs `carbon_pt` per zone |
| `fig2_carbon_vs_accuracy.png` | Carbon vs accuracy for the chosen pair on both sets, other λ faint |
| `fig3_zones.png` | Per zone, the change from GreenServ to `carbon_pt` in carbon and accuracy |
| `fig4_language_mix.png` | Model share of the carbon routers with and without language features (λ = 0.7) |

### Appendix figures

From `python -m experiments.appendix_analysis`, in `experiments/results/figures/appendix/`, for both sets and the same λ pair as the main figures.

| Figure | Shows | Supports |
|---|---|---|
| `figA1_mechanism.png` | Share of test queries sent to the two largest models vs grid intensity at decision time: GreenServ flat, `carbon_pt` falling as the grid gets dirtier | carbon awareness changes model choice |
| `figA2_zone_differences.png` (+ `.csv`) | `carbon_pt` minus GreenServ per zone, accuracy (points) and carbon (g per 1k; % in the CSV), with 95% paired bootstrap CIs over items | gains in clean zones, carbon cuts in dirty ones |
| `figA3_language_ablation.png` | Accuracy and worst-language accuracy along the language-feature chain at each matched carbon level | language features barely matter |
| `figA4_item_vs_language.png` (+ `.csv`) | Each model's accuracy by language, and how much of its right/wrong pattern the item explains vs the language (adjusted η²) | why: on the main set the item explains 36–61%, the language under 4%; model rankings barely change across languages |
| `figA5_grid_zones.png` | Hourly carbon intensity per zone in 2025: distribution and average local day | context for clean vs dirty zones |

On the low-resource set the language explains more (5–16%) because every model degrades sharply in the hardest languages, but the strongest models stay strongest almost everywhere, so a language label still has little to route on.

### Findings

- **Grid awareness beats GreenServ at matched carbon once the cost unit is held fixed.** `carbon_pt` (GreenServ + grid, carbon per token) beats `greenserv` by 3.2 points at 20 g per 1k and 2.0 at 30 g on the main set (weakest language +3.9 and +2.4), and by 1.6–5.3 points at 4–7 g on the low-resource set. It sends queries to the largest model on clean grids (France, Sweden) and to small models on dirty ones; GreenServ's mix is identical in every zone. At 30 g it is also 1.6 points above `best_fixed`, the only router above it at any compared level. On the main set the per-token cost unit beats per query (`carbon_pt` over `carbon` by 2–4 points, `greenserv` over `energy_pq` by about 7); on the low-resource set per query is slightly better (`carbon` 0.777 vs `carbon_pt` 0.765 at 5 g).
- **vs always using the largest model:** `lang_carbon` uses 16% less carbon for 1.2 points of accuracy on the main set. On the low-resource set it saves 14% but loses 4.4 points.
- **Language features** (`ablation.csv`): on the main set the gain over `carbon_no_flesch` (about 1.5–2 points) comes from replacing the topic clusters with the full embedding; the English encoder does as well as the multilingual one and the language one-hot adds nothing on top. On the low-resource set every step lowers accuracy slightly, and the one-hot alone hurts the weakest language.
- **The best single model chosen on training data (`best_fixed`) is hard to beat.** On the low-resource set it beats every router at every compared carbon level (3–6 g per 1k); at λ = 0.5 it is simply the largest model. On the main set its curve spans only 30–40 g per 1k: at 40 g it beats every router (0.864 vs 0.851 for `carbon_pt`, the best router), and at 30 g only `carbon_pt` is above it (0.839 vs 0.823). The language features don't help on the low-resource set even at matched carbon (`lang_carbon` is 0.9 points below `carbon_no_flesch` at 5 and 6 g per 1k), and the one-hot router does worst on Wolof (0.46 vs 0.60 at λ = 0.5).
- **Pooled carbon is about 96% MGSM**, so each run's `analysis/by_benchmark.csv` is the table to read for XNLI and Belebele.
- Offline checks suggest which model gets a question right depends mostly on the specific question, not its language. When the two small models agree, qwen3.5-2b is right 92% of the time vs 56% when they disagree, a stronger routing signal than anything in the question text.

### Where the numbers are

| What | Folder |
|---|---|
| Main set: every router at λ = 0.3, 0.5, 0.7, 0.9 (`lambda_<λ>/`, `carbon_pt/lambda_<λ>/`) and the matched-carbon comparison (`comparison/`) | `experiments/results/lambda_sweep/` |
| Low-resource set, same layout | `experiments/results/lowres/lambda_sweep/` |
| Main and appendix figures | `experiments/results/figures/main_analysis/`, `.../figures/appendix/` |

Each run folder holds `summary.csv` (per zone × router × strategy × phase, mean and std over runs), `choices.csv` (model share per language), `config.json` (every argument and setting) and `analysis/`:

| File | Contents |
|---|---|
| `report.md` | the tables below in markdown |
| `headline.csv` | test phase per zone and averaged over zones: accuracy, worst-language accuracy, gCO₂ per 1,000 queries, J per query (mean and std over runs) |
| `by_language.csv` | test accuracy per strategy × language |
| `by_benchmark.csv` | test accuracy, gCO₂ per 1,000 queries and J per query per strategy × benchmark, plus carbon as % of always using the largest model and each benchmark's share of total carbon |
| `comparisons.csv` | paired differences (e.g. `lang_carbon` vs `largest`, vs each ablation): accuracy in points and carbon in %, with 95% bootstrap CIs over test items, per zone and pooled |
| `tradeoff.png`, `language_accuracy.png`, `model_share.png`, `carbon_awareness.png`, `learning_curve.png` | accuracy vs carbon per zone; accuracy heatmap; model share per language; chosen model's energy vs grid intensity; regret during training |

Each `comparison/` folder holds `lambda_headline.csv` (one row per router × λ), `by_lambda_*.csv`, `matched_carbon.csv` (accuracy and worst-language accuracy at common carbon levels), `ablation.csv` (the feature chains above at those levels), `model_mix.csv` and `model_mix_by_zone.csv` (test-phase model share per router and λ) and `lambda_tradeoff.png`.

## Extensions (not part of the main experiment)

Two ideas were tried and kept apart from the main results, in `experiments/results/extensions/`.

**Per-language accuracy floors** (`carbon_pt_lang`, `carbon_pt_floor`; results in `extensions/floor/{main,lowres}/`). `carbon_pt_floor` learns from reward + μ_l · (1 − λ) · accuracy, where each language's multiplier μ_l is tuned on the training stream by dual ascent: each pass trains a fresh bandit with μ fixed, scores its frozen policy on the training items, and raises μ_l by `step` × (floor_l − accuracy_l). The floor is `ratio` × the best single model's training accuracy in that language (`floor:` in `config/routers.yaml`). `carbon_pt_lang` is the same router without floors, as a control.

- **Finding:** floors help a little on the main set and hurt on the low-resource set. On the main set `carbon_pt_floor` is 0.5–0.7 points above `carbon_pt` at 40–50 g per 1k, and has the best weakest-language accuracy of any strategy at 40 g (0.799, vs 0.783 for `best_fixed`). Floors also stop accuracy collapsing at high λ (0.836 at λ = 0.9 vs 0.776). On the low-resource set it is below `carbon_pt` at 6 g (0.780 vs 0.789; weakest language 0.494 vs 0.544). The language one-hot it needs overfits with 175 training queries per language: `carbon_pt_lang` loses about 7 points on the weakest language. Only 75 test items per low-resource language, so weakest-language differences under about 5 points are within noise.

```bash
E=experiments/results/extensions/floor/main   # with S and DATA from the main-set block in Level 2
for l in 0.3 0.5 0.7 0.9; do
    python -m experiments.run --router carbon_pt_lang carbon_pt_floor --zone all --lambda $l $DATA --output-dir $E/lambda_$l
done
for run in $E/lambda_*/*/; do python -m experiments.analyze_per_lambda $run; done
python -m experiments.lambda_compare $E/comparison \
    $(for d in $S $S/carbon_pt $E; do for l in 0.3 0.5 0.7 0.9; do echo $l=$(ls -d $d/lambda_$l/*/); done; done) \
    --levels 20 30 40 50 60
```

**Agreement cascade** (`experiments/extensions/cascade.py`; results in `extensions/cascade/{main,lowres}/`). Two cheap models answer; if they agree, keep the answer, otherwise escalate to a larger model. Evaluated offline on the stored answers, with carbon paired to the routers' λ = 0.5 test streams (it reads that run's `steps.csv.gz`, so re-run the λ = 0.5 simulation first).

- **Finding:** the cascade loses on both sets. When qwen3.5-2b and tiny-aya agree on the main set they are right 87% of the time (gemma-e4b + tiny-aya: 93%), but pairs disagree on 37–39% of main-set queries and 38–53% of low-resource ones, and running two models costs too much: on MGSM, which is about 96% of carbon, the pair uses 2,300 J against 3,160 J for qwen3.5-9b. Every cascade is below `carbon_pt` at the same carbon (best: 0.841 at 46 g vs 0.855), and on the low-resource set every cascade uses more carbon than always using the largest model. Sending clean-grid queries straight to the largest model (`(grid)` variants) helps a little but not enough.

```bash
python -m experiments.extensions.cascade experiments/results/extensions/cascade/main \
    --run-dir experiments/results/lambda_sweep/lambda_0.5/<timestamp> \
    --results runpod_generations/generations_NVIDIA-A100-SXM4-80GB.jsonl \
    --comparison experiments/results/extensions/floor/main/comparison
```

## Repository structure

```
config/                      # datasets, models, features, router profiles, grid zones, low-resource languages
data/
├── load.py, helper.py       # download benchmark splits from Hugging Face and restructure them
├── process.py               # item selection (sampling strata) and prompt formatting, main 8 languages
├── process_lowres.py        # Belebele queries for the low-resource languages
├── split.py                 # item-level train/test split
├── embed.py                 # cached router embeddings (--append adds new queries)
├── fetch_grid.py            # Electricity Maps hourly intensity
├── generate.py              # GPU generation: accuracy + energy per query × model
├── preprocessed/            # selected queries and splits (committed)
├── features/                # cached embeddings for all 9,000 queries (committed)
└── grid/                    # hourly intensity per zone and global bounds (committed)
runpod_generations/          # RunPod outputs (committed): generations (main + low-resource), encoder energy,
                             #   low-resource summary
experiments/
├── run.py                   # routing simulation (--router, --zone, --lambda, ...)
├── simulation/              # data.py (load generations, splits, energy bounds), features.py (router context),
│                            #   rewards.py (cost functions and reward)
├── analyze_per_lambda.py    # tables, paired comparisons and figures for one run
├── lambda_compare.py        # accuracy-vs-carbon curves and matched-carbon comparison across λ
├── main_analysis.py         # main figures, from analyze_per_lambda and lambda_compare outputs
├── appendix_analysis.py     # appendix figures backing the two main claims
├── extensions/              # side experiments: cascade.py
└── results/
    ├── lambda_sweep/        # main set: lambda_<λ>/, carbon_pt/lambda_<λ>/, comparison/
    ├── lowres/lambda_sweep/ # low-resource set, same layout
    ├── extensions/          # cascade/{main,lowres}/, floor/{main,lowres}/
    └── figures/             # main_analysis/, appendix/
scripts/
├── runpod_setup.sh          # Pod setup: model cache, dependencies, GPU check
├── preflight.py             # GPU, energy counter, HF access and disk checks; downloads weights
├── measure_encoder_energy.py # router encoder energy per query on the generation GPU
└── summarize_generations.py # sanity checks on a generate.py output file
src/
├── bandit/                  # LinUCB (used), factory; epsilon_greedy.py and thompson_sampling.py are GreenServ leftovers
├── feature_extractor/       # complexity (Flesch), language one-hot, sentence-embedding encoder
├── metrics/                 # answer extraction, accuracy, energy, carbon, grid intensity
└── services/                # inference (generation) and answer evaluation
```

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

Still in the code but unused, each marked with a comment: the ε-greedy and Thompson sampling bandits (every run uses LinUCB), F1/ROUGE scoring and the regex/raw answer extractors (every benchmark uses exact match with the multiple-choice or numeric extractor), and the bandits' `get_state`/`set_state`/`add_model` (GreenServ's live service used them).

## Setup

### Prerequisites

- Python 3.10+ (on Apple silicon, use a native arm64 Python such as Homebrew's; an Intel/Rosetta build caps PyTorch at 2.2)
- Levels 1–2: nothing else
- Level 3: a GPU for generation (RunPod; ~80 GB VRAM for the 27B/31B models in bf16), a Hugging Face account and token (Tiny Aya and Gemma 4 are gated), and an Electricity Maps API token or its downloadable hourly datasets

### Installation

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt        # local: data prep, features, simulation, analysis
# On the Pod instead: pip install -r requirements-gpu.txt (via scripts/runpod_setup.sh)
export HF_TOKEN=...                    # Level 3 only
export ELECTRICITYMAPS_TOKEN=...       # Level 3 only
```

Keep tokens and API keys in environment variables set from your home-directory shell profile (`~/.zshrc`), not in files inside the repo. `.gitignore` excludes `.zshrc`, `.bashrc` and `.env` files as a safety net.
