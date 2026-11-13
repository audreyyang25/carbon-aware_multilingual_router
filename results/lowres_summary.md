# Belebele low-resource run (A100 SXM4 80GB)

Follow-up to the TA feedback that the main run covers only the 8 languages shared by XNLI, Belebele and MGSM.
Belebele is the only one of the three with many more languages (122 variants; XNLI has 15, MGSM 11), so this run adds
12 low-resource languages on Belebele only, plus English and Swahili re-run as anchors.

- File: `results/generations_lowres_NVIDIA-A100-SXM4-80GB.jsonl.gz` (kept apart from the main `generations_NVIDIA-A100-SXM4-80GB.jsonl`)
- 21,000 rows = 14 languages × 250 items × 6 models; every (query, model) pair present once
- Same 250 Belebele items as the main run (same `item_id`, so `data/preprocessed/splits.csv` applies); same prompts, models and decoding
- Pod in RunPod `US-MD-1`, run 2026-11-12T15:58–2026-11-12T17:21 UTC (about 1.4 GPU hours)
- Built with `data/process_lowres.py` (languages in `config/lowres_languages.yaml`)

## Accuracy (share correct, 250 items each)

Sorted by the mean over models.

| Language | qwen3.5-2b | tiny-aya-global | gemma-4-e4b | qwen3.5-9b | qwen3.5-27b | gemma-4-31b | Mean |
|---|---|---|---|---|---|---|---|
| English (anchor) (`en`) | 0.82 | 0.82 | 0.90 | 0.96 | 0.98 | 0.97 | **0.91** |
| Swahili (anchor) (`sw`) | 0.47 | 0.74 | 0.81 | 0.84 | 0.94 | 0.95 | **0.79** |
| Burmese (`my`) | 0.54 | 0.67 | 0.80 | 0.83 | 0.88 | 0.90 | **0.77** |
| Nepali (`ne`) | 0.52 | 0.68 | 0.79 | 0.83 | 0.88 | 0.89 | **0.77** |
| Khmer (`km`) | 0.53 | 0.64 | 0.77 | 0.80 | 0.89 | 0.90 | **0.75** |
| Sinhala (`si`) | 0.51 | 0.38 | 0.80 | 0.82 | 0.93 | 0.92 | **0.73** |
| Lao (`lo`) | 0.46 | 0.64 | 0.74 | 0.80 | 0.84 | 0.85 | **0.72** |
| Amharic (`am`) | 0.39 | 0.60 | 0.68 | 0.72 | 0.85 | 0.89 | **0.69** |
| Hausa (`ha`) | 0.43 | 0.52 | 0.61 | 0.59 | 0.80 | 0.84 | **0.63** |
| Zulu (`zu`) | 0.37 | 0.54 | 0.52 | 0.64 | 0.78 | 0.78 | **0.60** |
| Igbo (`ig`) | 0.39 | 0.45 | 0.42 | 0.58 | 0.72 | 0.71 | **0.55** |
| Yoruba (`yo`) | 0.40 | 0.44 | 0.36 | 0.53 | 0.68 | 0.70 | **0.52** |
| Guarani (`gn`) | 0.36 | 0.33 | 0.38 | 0.50 | 0.73 | 0.75 | **0.51** |
| Wolof (`wo`) | 0.35 | 0.34 | 0.31 | 0.44 | 0.55 | 0.56 | **0.43** |

## Mean GPU energy per query (J)

| Language | qwen3.5-2b | tiny-aya-global | gemma-4-e4b | qwen3.5-9b | qwen3.5-27b | gemma-4-31b | Mean |
|---|---|---|---|---|---|---|---|
| Amharic (`am`) | 29 | 40 | 27 | 63 | 150 | 84 | **65** |
| English (anchor) (`en`) | 16 | 26 | 23 | 39 | 71 | 69 | **41** |
| Guarani (`gn`) | 20 | 48 | 27 | 45 | 90 | 85 | **53** |
| Hausa (`ha`) | 21 | 40 | 27 | 47 | 93 | 80 | **51** |
| Igbo (`ig`) | 23 | 41 | 28 | 48 | 102 | 88 | **55** |
| Khmer (`km`) | 30 | 41 | 30 | 68 | 164 | 100 | **72** |
| Lao (`lo`) | 30 | 38 | 29 | 65 | 155 | 99 | **69** |
| Burmese (`my`) | 27 | 40 | 29 | 56 | 126 | 94 | **62** |
| Nepali (`ne`) | 22 | 35 | 27 | 47 | 100 | 77 | **51** |
| Sinhala (`si`) | 27 | 62 | 29 | 58 | 132 | 94 | **67** |
| Swahili (anchor) (`sw`) | 20 | 32 | 26 | 43 | 87 | 79 | **48** |
| Wolof (`wo`) | 20 | 43 | 26 | 45 | 91 | 80 | **51** |
| Yoruba (`yo`) | 24 | 40 | 28 | 50 | 106 | 89 | **56** |
| Zulu (`zu`) | 22 | 38 | 26 | 46 | 97 | 85 | **52** |

## Caveats

- 45 rows read 0 J (the energy counter missed very short answers, as in the main run). They are left as 0 in the file and excluded from the energy table above; `impute_missing_energy` in `experiments/shared/simulation_data.py` fills them at load time.
- 1,893 rows hit the 8-token cap (tiny-aya-global: 1875, gemma-4-31b: 15, gemma-4-e4b: 3). Almost all are tiny-aya-global writing the letter followed by the option text (e.g. `C. Lọndọnu`); the letter is still extracted and scored.
- **Anchor check against the main run** (Belebele en + sw, 3,000 matched (query, model) pairs): the generated text is identical in 100% of pairs, so accuracy matches exactly. Energy is higher on this Pod: the median per model and language is 2–18% above the main run (e.g. qwen3.5-9b en 42.2 J vs 35.9 J). Compare energy across the two files only after scaling by the anchors, or compare within this file.

