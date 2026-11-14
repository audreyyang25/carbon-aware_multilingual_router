# Routing results: 20261114_133247

- Hardware: NVIDIA A100-SXM4-80GB; models: gemma-4-31b, gemma-4-e4b, qwen3.5-27b, qwen3.5-2b, qwen3.5-9b, tiny-aya-global
- Algorithm: linucb, lambda = 0.9, 5 runs, 250 queries/hour
- Zones: FR, SE-SE3, DE, US-CAL-CISO, US-NE-ISNE, PL

## Test phase, averaged over zones

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.569 | 0.333 | 3.386 | 41.362 |
| energy_pq | 0.599 | 0.301 | 2.091 | 25.531 |
| carbon | 0.697 | 0.408 | 2.405 | 48.071 |
| carbon_no_flesch | 0.775 | 0.516 | 4.349 | 69.698 |
| carbon_en_emb | 0.685 | 0.395 | 2.422 | 45.998 |
| carbon_onehot | 0.697 | 0.403 | 2.346 | 47.162 |
| carbon_ml_emb | 0.674 | 0.394 | 2.444 | 45.700 |
| lang_carbon | 0.670 | 0.384 | 2.466 | 46.022 |
| random | 0.661 | 0.413 | 4.548 | 55.549 |
| smallest | 0.449 | 0.293 | 1.944 | 23.741 |
| largest | 0.827 | 0.600 | 6.927 | 84.600 |
| best_fixed | 0.701 | 0.387 | 2.370 | 46.227 |
| oracle | 0.905 | 0.751 | 2.177 | 28.269 |

## Paired comparisons (all zones)

Router minus reference on the same queries. Accuracy in points, carbon in % of the reference. 95% bootstrap CI over test items; * = CI excludes 0.

| comparison | question | accuracy (pp) | carbon (%) |
|---|---|---|---|
| lang_carbon vs largest | Savings vs always using the largest model | -15.7 [-18.5, -13.1] * | -64.4% [-65.3, -63.4] * |
| lang_carbon vs best_fixed | vs the best single model in hindsight | -3.1 [-4.7, -1.7] * | +4.1% [+2.7, +5.5] * |
| lang_carbon vs greenserv | vs GreenServ (energy-per-token cost, English features) | +10.1 [+6.4, +13.9] * | -27.2% [-29.9, -24.1] * |
| lang_carbon vs carbon_no_flesch | Do language + multilingual embedding help? | -10.5 [-12.4, -8.8] * | -43.3% [-44.4, -42.1] * |
| lang_carbon vs carbon_onehot | Does the embedding add beyond the language label? | -2.7 [-3.7, -1.7] * | +5.2% [+4.1, +6.2] * |
| lang_carbon vs carbon_ml_emb | Does the language label add beyond the embedding? | -0.4 [-1.0, +0.1] | +0.9% [+0.2, +1.6] * |
| carbon_ml_emb vs carbon_en_emb | Multilingual vs English encoder | -1.1 [-1.9, -0.3] * | +0.9% [-0.0, +1.9] |
| carbon vs energy_pq | Does seeing the grid help? (carbon vs energy cost) | +9.8 [+7.9, +11.7] * | +15.0% [+14.4, +15.6] * |
| carbon vs carbon_no_flesch | Does Flesch complexity help? | -7.8 [-9.3, -6.4] * | -44.7% [-45.5, -43.9] * |
| carbon vs greenserv | Carbon cost vs GreenServ's energy-per-token cost | +12.9 [+8.9, +16.9] * | -29.0% [-31.8, -25.8] * |

## Test results by benchmark (all zones)

Pooled carbon above is a mean over all test queries, so it is almost entirely MGSM (an MGSM answer uses about 100x the energy of an XNLI or Belebele one). Here each benchmark is on its own; `% of largest` puts carbon on a common scale (always using the largest model = 100), and its benchmark average weights the three equally.

| strategy | acc belebele | gCO2/1k belebele | % of largest belebele | % of largest, benchmarks averaged |
|---|---|---|---|---|
| greenserv | 0.569 | 3.386 | 48.883 | 48.883 |
| energy_pq | 0.599 | 2.091 | 30.185 | 30.185 |
| carbon | 0.697 | 2.405 | 34.716 | 34.716 |
| carbon_no_flesch | 0.775 | 4.349 | 62.781 | 62.781 |
| carbon_en_emb | 0.685 | 2.422 | 34.961 | 34.961 |
| carbon_onehot | 0.697 | 2.346 | 33.862 | 33.862 |
| carbon_ml_emb | 0.674 | 2.444 | 35.284 | 35.284 |
| lang_carbon | 0.670 | 2.466 | 35.606 | 35.606 |
| random | 0.661 | 4.548 | 65.665 | 65.665 |
| smallest | 0.449 | 1.944 | 28.063 | 28.063 |
| largest | 0.827 | 6.927 | 100.000 | 100.000 |
| best_fixed | 0.701 | 2.370 | 34.219 | 34.219 |
| oracle | 0.905 | 2.177 | 31.434 | 31.434 |

Share of each strategy's total carbon spent on each benchmark:

| strategy | share of carbon belebele |
|---|---|
| greenserv | 1.000 |
| energy_pq | 1.000 |
| carbon | 1.000 |
| carbon_no_flesch | 1.000 |
| carbon_en_emb | 1.000 |
| carbon_onehot | 1.000 |
| carbon_ml_emb | 1.000 |
| lang_carbon | 1.000 |
| random | 1.000 |
| smallest | 1.000 |
| largest | 1.000 |
| best_fixed | 1.000 |
| oracle | 1.000 |

## Test accuracy by language (all zones)

| strategy | en | sw | am | gn | ha | ig | km | lo | my | ne | si | wo | yo | zu | worst |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| greenserv | 0.827 | 0.760 | 0.613 | 0.387 | 0.533 | 0.467 | 0.680 | 0.640 | 0.627 | 0.640 | 0.333 | 0.333 | 0.520 | 0.600 | 0.333 |
| energy_pq | 0.885 | 0.616 | 0.640 | 0.352 | 0.443 | 0.427 | 0.787 | 0.720 | 0.880 | 0.760 | 0.800 | 0.315 | 0.352 | 0.411 | 0.315 |
| carbon | 0.925 | 0.808 | 0.728 | 0.537 | 0.633 | 0.552 | 0.831 | 0.754 | 0.880 | 0.798 | 0.850 | 0.411 | 0.459 | 0.595 | 0.411 |
| carbon_no_flesch | 0.962 | 0.883 | 0.816 | 0.676 | 0.747 | 0.669 | 0.875 | 0.788 | 0.880 | 0.858 | 0.917 | 0.516 | 0.557 | 0.712 | 0.516 |
| carbon_en_emb | 0.900 | 0.820 | 0.697 | 0.501 | 0.636 | 0.572 | 0.808 | 0.738 | 0.864 | 0.763 | 0.832 | 0.397 | 0.467 | 0.600 | 0.397 |
| carbon_onehot | 0.906 | 0.839 | 0.721 | 0.501 | 0.653 | 0.547 | 0.827 | 0.743 | 0.880 | 0.804 | 0.856 | 0.413 | 0.458 | 0.611 | 0.413 |
| carbon_ml_emb | 0.916 | 0.828 | 0.686 | 0.491 | 0.625 | 0.528 | 0.791 | 0.722 | 0.856 | 0.723 | 0.809 | 0.402 | 0.461 | 0.599 | 0.402 |
| lang_carbon | 0.912 | 0.809 | 0.697 | 0.478 | 0.612 | 0.541 | 0.778 | 0.732 | 0.821 | 0.729 | 0.815 | 0.389 | 0.466 | 0.599 | 0.389 |
| random | 0.917 | 0.789 | 0.659 | 0.528 | 0.573 | 0.592 | 0.736 | 0.725 | 0.771 | 0.693 | 0.741 | 0.413 | 0.507 | 0.613 | 0.413 |
| smallest | 0.827 | 0.493 | 0.453 | 0.293 | 0.373 | 0.413 | 0.507 | 0.413 | 0.547 | 0.427 | 0.507 | 0.320 | 0.347 | 0.360 | 0.293 |
| largest | 0.987 | 0.920 | 0.880 | 0.773 | 0.800 | 0.747 | 0.907 | 0.813 | 0.880 | 0.893 | 0.960 | 0.600 | 0.627 | 0.787 | 0.600 |
| best_fixed | 0.924 | 0.840 | 0.720 | 0.533 | 0.676 | 0.551 | 0.827 | 0.751 | 0.880 | 0.804 | 0.853 | 0.387 | 0.458 | 0.609 | 0.387 |
| oracle | 0.996 | 0.976 | 0.899 | 0.870 | 0.887 | 0.880 | 0.980 | 0.900 | 0.959 | 0.928 | 0.972 | 0.751 | 0.789 | 0.892 | 0.751 |

## FR

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.569 | 0.333 | 0.430 | 41.362 |
| energy_pq | 0.599 | 0.301 | 0.266 | 25.531 |
| carbon | 0.827 | 0.600 | 0.884 | 85.101 |
| carbon_no_flesch | 0.827 | 0.600 | 0.884 | 85.101 |
| carbon_en_emb | 0.786 | 0.536 | 0.769 | 77.074 |
| carbon_onehot | 0.827 | 0.600 | 0.884 | 85.101 |
| carbon_ml_emb | 0.773 | 0.549 | 0.787 | 76.985 |
| lang_carbon | 0.770 | 0.496 | 0.745 | 73.924 |
| random | 0.661 | 0.413 | 0.578 | 55.549 |
| smallest | 0.449 | 0.293 | 0.247 | 23.741 |
| largest | 0.827 | 0.600 | 0.879 | 84.600 |
| best_fixed | 0.827 | 0.600 | 0.879 | 84.600 |
| oracle | 0.929 | 0.787 | 0.312 | 29.985 |

## SE-SE3

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.569 | 0.333 | 0.244 | 41.362 |
| energy_pq | 0.599 | 0.301 | 0.151 | 25.531 |
| carbon | 0.827 | 0.600 | 0.503 | 85.101 |
| carbon_no_flesch | 0.827 | 0.600 | 0.503 | 85.101 |
| carbon_en_emb | 0.797 | 0.547 | 0.486 | 82.396 |
| carbon_onehot | 0.827 | 0.600 | 0.503 | 85.101 |
| carbon_ml_emb | 0.786 | 0.565 | 0.474 | 80.086 |
| lang_carbon | 0.793 | 0.557 | 0.486 | 82.748 |
| random | 0.661 | 0.413 | 0.328 | 55.549 |
| smallest | 0.449 | 0.293 | 0.140 | 23.741 |
| largest | 0.827 | 0.600 | 0.500 | 84.600 |
| best_fixed | 0.827 | 0.600 | 0.500 | 84.600 |
| oracle | 0.929 | 0.787 | 0.177 | 29.985 |

## DE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.569 | 0.333 | 5.156 | 41.362 |
| energy_pq | 0.599 | 0.301 | 3.187 | 25.531 |
| carbon | 0.615 | 0.309 | 3.251 | 26.164 |
| carbon_no_flesch | 0.714 | 0.408 | 6.095 | 50.566 |
| carbon_en_emb | 0.633 | 0.325 | 3.395 | 27.321 |
| carbon_onehot | 0.626 | 0.291 | 3.263 | 26.178 |
| carbon_ml_emb | 0.615 | 0.299 | 3.454 | 27.840 |
| lang_carbon | 0.598 | 0.296 | 3.448 | 27.847 |
| random | 0.661 | 0.413 | 6.925 | 55.549 |
| smallest | 0.449 | 0.293 | 2.960 | 23.741 |
| largest | 0.827 | 0.600 | 10.546 | 84.600 |
| best_fixed | 0.638 | 0.280 | 3.371 | 27.041 |
| oracle | 0.886 | 0.728 | 3.292 | 26.518 |

## US-CAL-CISO

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.569 | 0.333 | 2.971 | 41.362 |
| energy_pq | 0.599 | 0.301 | 1.832 | 25.531 |
| carbon | 0.676 | 0.344 | 2.523 | 39.054 |
| carbon_no_flesch | 0.827 | 0.600 | 6.116 | 85.101 |
| carbon_en_emb | 0.652 | 0.312 | 2.204 | 32.699 |
| carbon_onehot | 0.662 | 0.347 | 2.172 | 33.986 |
| carbon_ml_emb | 0.640 | 0.320 | 2.208 | 32.542 |
| lang_carbon | 0.632 | 0.341 | 2.252 | 33.542 |
| random | 0.661 | 0.413 | 3.990 | 55.549 |
| smallest | 0.449 | 0.293 | 1.705 | 23.741 |
| largest | 0.827 | 0.600 | 6.080 | 84.600 |
| best_fixed | 0.638 | 0.280 | 1.943 | 27.041 |
| oracle | 0.922 | 0.784 | 2.098 | 29.373 |

## US-NE-ISNE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.569 | 0.333 | 3.520 | 41.362 |
| energy_pq | 0.599 | 0.301 | 2.173 | 25.531 |
| carbon | 0.638 | 0.280 | 2.344 | 27.542 |
| carbon_no_flesch | 0.827 | 0.600 | 7.243 | 85.101 |
| carbon_en_emb | 0.637 | 0.341 | 2.502 | 29.416 |
| carbon_onehot | 0.633 | 0.285 | 2.282 | 26.827 |
| carbon_ml_emb | 0.626 | 0.320 | 2.496 | 29.411 |
| lang_carbon | 0.625 | 0.315 | 2.593 | 30.498 |
| random | 0.661 | 0.413 | 4.725 | 55.549 |
| smallest | 0.449 | 0.293 | 2.021 | 23.741 |
| largest | 0.827 | 0.600 | 7.200 | 84.600 |
| best_fixed | 0.638 | 0.280 | 2.302 | 27.041 |
| oracle | 0.923 | 0.787 | 2.504 | 29.424 |

## PL

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.569 | 0.333 | 7.995 | 41.362 |
| energy_pq | 0.599 | 0.301 | 4.936 | 25.531 |
| carbon | 0.602 | 0.315 | 4.923 | 25.466 |
| carbon_no_flesch | 0.632 | 0.285 | 5.252 | 27.220 |
| carbon_en_emb | 0.607 | 0.307 | 5.174 | 27.083 |
| carbon_onehot | 0.608 | 0.293 | 4.969 | 25.776 |
| carbon_ml_emb | 0.605 | 0.309 | 5.245 | 27.336 |
| lang_carbon | 0.601 | 0.299 | 5.275 | 27.572 |
| random | 0.661 | 0.413 | 10.744 | 55.549 |
| smallest | 0.449 | 0.293 | 4.591 | 23.741 |
| largest | 0.827 | 0.600 | 16.355 | 84.600 |
| best_fixed | 0.638 | 0.280 | 5.227 | 27.041 |
| oracle | 0.844 | 0.635 | 4.682 | 24.328 |
