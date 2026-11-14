# Routing results: 20261114_133247

- Hardware: NVIDIA A100-SXM4-80GB; models: gemma-4-31b, gemma-4-e4b, qwen3.5-27b, qwen3.5-2b, qwen3.5-9b, tiny-aya-global
- Algorithm: linucb, lambda = 0.7, 5 runs, 250 queries/hour
- Zones: FR, SE-SE3, DE, US-CAL-CISO, US-NE-ISNE, PL

## Test phase, averaged over zones

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.626 | 0.325 | 2.919 | 35.704 |
| energy_pq | 0.627 | 0.312 | 2.765 | 33.827 |
| carbon | 0.762 | 0.509 | 4.247 | 68.405 |
| carbon_no_flesch | 0.771 | 0.502 | 4.979 | 69.865 |
| carbon_en_emb | 0.755 | 0.487 | 4.426 | 67.043 |
| carbon_onehot | 0.756 | 0.420 | 4.343 | 67.758 |
| carbon_ml_emb | 0.751 | 0.496 | 4.222 | 66.750 |
| lang_carbon | 0.748 | 0.477 | 4.305 | 66.719 |
| random | 0.661 | 0.413 | 4.548 | 55.549 |
| smallest | 0.449 | 0.293 | 1.944 | 23.741 |
| largest | 0.827 | 0.600 | 6.927 | 84.600 |
| best_fixed | 0.770 | 0.504 | 4.117 | 67.332 |
| oracle | 0.929 | 0.787 | 2.455 | 29.985 |

## Paired comparisons (all zones)

Router minus reference on the same queries. Accuracy in points, carbon in % of the reference. 95% bootstrap CI over test items; * = CI excludes 0.

| comparison | question | accuracy (pp) | carbon (%) |
|---|---|---|---|
| lang_carbon vs largest | Savings vs always using the largest model | -7.9 [-9.6, -6.3] * | -37.9% [-39.2, -36.5] * |
| lang_carbon vs best_fixed | vs the best single model in hindsight | -2.3 [-3.3, -1.2] * | +4.5% [+2.7, +6.4] * |
| lang_carbon vs greenserv | vs GreenServ (energy-per-token cost, English features) | +12.1 [+10.2, +14.3] * | +47.5% [+44.5, +50.4] * |
| lang_carbon vs carbon_no_flesch | Do language + multilingual embedding help? | -2.3 [-3.2, -1.4] * | -13.5% [-15.2, -11.9] * |
| lang_carbon vs carbon_onehot | Does the embedding add beyond the language label? | -0.9 [-1.6, -0.2] * | -0.9% [-2.7, +1.0] |
| lang_carbon vs carbon_ml_emb | Does the language label add beyond the embedding? | -0.3 [-0.9, +0.2] | +2.0% [+0.5, +3.4] * |
| carbon_ml_emb vs carbon_en_emb | Multilingual vs English encoder | -0.4 [-1.2, +0.3] | -4.6% [-6.3, -2.7] * |
| carbon vs energy_pq | Does seeing the grid help? (carbon vs energy cost) | +13.5 [+11.3, +15.8] * | +53.6% [+51.9, +55.3] * |
| carbon vs carbon_no_flesch | Does Flesch complexity help? | -0.9 [-1.4, -0.3] * | -14.7% [-15.1, -14.3] * |
| carbon vs greenserv | Carbon cost vs GreenServ's energy-per-token cost | +13.5 [+11.4, +15.8] * | +45.5% [+43.1, +47.9] * |

## Test results by benchmark (all zones)

Pooled carbon above is a mean over all test queries, so it is almost entirely MGSM (an MGSM answer uses about 100x the energy of an XNLI or Belebele one). Here each benchmark is on its own; `% of largest` puts carbon on a common scale (always using the largest model = 100), and its benchmark average weights the three equally.

| strategy | acc belebele | gCO2/1k belebele | % of largest belebele | % of largest, benchmarks averaged |
|---|---|---|---|---|
| greenserv | 0.626 | 2.919 | 42.137 | 42.137 |
| energy_pq | 0.627 | 2.765 | 39.917 | 39.917 |
| carbon | 0.762 | 4.247 | 61.313 | 61.313 |
| carbon_no_flesch | 0.771 | 4.979 | 71.874 | 71.874 |
| carbon_en_emb | 0.755 | 4.426 | 63.901 | 63.901 |
| carbon_onehot | 0.756 | 4.343 | 62.692 | 62.692 |
| carbon_ml_emb | 0.751 | 4.222 | 60.951 | 60.951 |
| lang_carbon | 0.748 | 4.305 | 62.145 | 62.145 |
| random | 0.661 | 4.548 | 65.665 | 65.665 |
| smallest | 0.449 | 1.944 | 28.063 | 28.063 |
| largest | 0.827 | 6.927 | 100.000 | 100.000 |
| best_fixed | 0.770 | 4.117 | 59.442 | 59.442 |
| oracle | 0.929 | 2.455 | 35.446 | 35.446 |

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
| greenserv | 0.861 | 0.776 | 0.643 | 0.424 | 0.507 | 0.451 | 0.773 | 0.720 | 0.824 | 0.747 | 0.712 | 0.328 | 0.416 | 0.589 | 0.328 |
| energy_pq | 0.896 | 0.739 | 0.651 | 0.413 | 0.536 | 0.472 | 0.755 | 0.677 | 0.813 | 0.771 | 0.811 | 0.317 | 0.400 | 0.528 | 0.317 |
| carbon | 0.944 | 0.900 | 0.758 | 0.702 | 0.723 | 0.680 | 0.837 | 0.767 | 0.856 | 0.809 | 0.871 | 0.509 | 0.582 | 0.728 | 0.509 |
| carbon_no_flesch | 0.960 | 0.881 | 0.805 | 0.666 | 0.738 | 0.670 | 0.870 | 0.793 | 0.876 | 0.838 | 0.899 | 0.507 | 0.571 | 0.713 | 0.507 |
| carbon_en_emb | 0.933 | 0.876 | 0.773 | 0.673 | 0.741 | 0.658 | 0.843 | 0.764 | 0.870 | 0.806 | 0.885 | 0.489 | 0.560 | 0.700 | 0.489 |
| carbon_onehot | 0.954 | 0.876 | 0.782 | 0.693 | 0.731 | 0.679 | 0.832 | 0.760 | 0.859 | 0.811 | 0.880 | 0.434 | 0.571 | 0.726 | 0.434 |
| carbon_ml_emb | 0.951 | 0.864 | 0.761 | 0.652 | 0.723 | 0.654 | 0.835 | 0.757 | 0.856 | 0.809 | 0.858 | 0.500 | 0.574 | 0.717 | 0.500 |
| lang_carbon | 0.944 | 0.864 | 0.755 | 0.682 | 0.728 | 0.651 | 0.817 | 0.757 | 0.849 | 0.801 | 0.859 | 0.482 | 0.572 | 0.705 | 0.482 |
| random | 0.917 | 0.789 | 0.659 | 0.528 | 0.573 | 0.592 | 0.736 | 0.725 | 0.771 | 0.693 | 0.741 | 0.413 | 0.507 | 0.613 | 0.413 |
| smallest | 0.827 | 0.493 | 0.453 | 0.293 | 0.373 | 0.413 | 0.507 | 0.413 | 0.547 | 0.427 | 0.507 | 0.320 | 0.347 | 0.360 | 0.293 |
| largest | 0.987 | 0.920 | 0.880 | 0.773 | 0.800 | 0.747 | 0.907 | 0.813 | 0.880 | 0.893 | 0.960 | 0.600 | 0.627 | 0.787 | 0.600 |
| best_fixed | 0.959 | 0.884 | 0.808 | 0.665 | 0.744 | 0.659 | 0.871 | 0.785 | 0.880 | 0.853 | 0.912 | 0.504 | 0.551 | 0.707 | 0.504 |
| oracle | 1.000 | 0.987 | 0.920 | 0.920 | 0.920 | 0.933 | 0.987 | 0.907 | 0.960 | 0.933 | 0.987 | 0.787 | 0.827 | 0.933 | 0.787 |

## FR

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.626 | 0.325 | 0.375 | 35.704 |
| energy_pq | 0.627 | 0.312 | 0.332 | 33.827 |
| carbon | 0.824 | 0.589 | 0.914 | 89.121 |
| carbon_no_flesch | 0.794 | 0.536 | 0.700 | 75.721 |
| carbon_en_emb | 0.803 | 0.565 | 0.866 | 83.220 |
| carbon_onehot | 0.805 | 0.555 | 0.894 | 85.915 |
| carbon_ml_emb | 0.804 | 0.555 | 0.912 | 87.565 |
| lang_carbon | 0.798 | 0.576 | 0.908 | 87.236 |
| random | 0.661 | 0.413 | 0.578 | 55.549 |
| smallest | 0.449 | 0.293 | 0.247 | 23.741 |
| largest | 0.827 | 0.600 | 0.879 | 84.600 |
| best_fixed | 0.827 | 0.600 | 0.879 | 84.600 |
| oracle | 0.929 | 0.787 | 0.312 | 29.985 |

## SE-SE3

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.626 | 0.325 | 0.213 | 35.704 |
| energy_pq | 0.627 | 0.312 | 0.204 | 33.827 |
| carbon | 0.823 | 0.579 | 0.570 | 94.835 |
| carbon_no_flesch | 0.794 | 0.536 | 0.458 | 75.721 |
| carbon_en_emb | 0.801 | 0.528 | 0.492 | 83.840 |
| carbon_onehot | 0.809 | 0.541 | 0.531 | 90.163 |
| carbon_ml_emb | 0.804 | 0.576 | 0.519 | 88.077 |
| lang_carbon | 0.799 | 0.523 | 0.502 | 85.199 |
| random | 0.661 | 0.413 | 0.328 | 55.549 |
| smallest | 0.449 | 0.293 | 0.140 | 23.741 |
| largest | 0.827 | 0.600 | 0.500 | 84.600 |
| best_fixed | 0.827 | 0.600 | 0.500 | 84.600 |
| oracle | 0.929 | 0.787 | 0.177 | 29.985 |

## DE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.626 | 0.325 | 4.459 | 35.704 |
| energy_pq | 0.627 | 0.312 | 4.184 | 33.827 |
| carbon | 0.707 | 0.456 | 6.178 | 48.086 |
| carbon_no_flesch | 0.761 | 0.501 | 8.454 | 67.516 |
| carbon_en_emb | 0.716 | 0.440 | 6.444 | 52.410 |
| carbon_onehot | 0.726 | 0.392 | 6.654 | 53.570 |
| carbon_ml_emb | 0.707 | 0.445 | 5.944 | 48.460 |
| lang_carbon | 0.719 | 0.453 | 6.322 | 51.627 |
| random | 0.661 | 0.413 | 6.925 | 55.549 |
| smallest | 0.449 | 0.293 | 2.960 | 23.741 |
| largest | 0.827 | 0.600 | 10.546 | 84.600 |
| best_fixed | 0.676 | 0.344 | 4.818 | 38.553 |
| oracle | 0.929 | 0.787 | 3.738 | 29.985 |

## US-CAL-CISO

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.626 | 0.325 | 2.545 | 35.704 |
| energy_pq | 0.627 | 0.312 | 2.509 | 33.827 |
| carbon | 0.788 | 0.549 | 5.108 | 73.261 |
| carbon_no_flesch | 0.796 | 0.531 | 5.486 | 78.514 |
| carbon_en_emb | 0.780 | 0.509 | 5.428 | 75.123 |
| carbon_onehot | 0.782 | 0.395 | 5.333 | 74.986 |
| carbon_ml_emb | 0.770 | 0.528 | 5.164 | 71.749 |
| lang_carbon | 0.770 | 0.504 | 5.255 | 73.566 |
| random | 0.661 | 0.413 | 3.990 | 55.549 |
| smallest | 0.449 | 0.293 | 1.705 | 23.741 |
| largest | 0.827 | 0.600 | 6.080 | 84.600 |
| best_fixed | 0.827 | 0.600 | 6.080 | 84.600 |
| oracle | 0.929 | 0.787 | 2.155 | 29.985 |

## US-NE-ISNE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.626 | 0.325 | 3.043 | 35.704 |
| energy_pq | 0.627 | 0.312 | 2.880 | 33.827 |
| carbon | 0.782 | 0.547 | 5.814 | 68.409 |
| carbon_no_flesch | 0.795 | 0.531 | 6.737 | 79.320 |
| carbon_en_emb | 0.759 | 0.507 | 5.570 | 65.633 |
| carbon_onehot | 0.763 | 0.344 | 5.456 | 64.242 |
| carbon_ml_emb | 0.760 | 0.509 | 5.620 | 66.138 |
| lang_carbon | 0.742 | 0.469 | 5.456 | 63.951 |
| random | 0.661 | 0.413 | 4.725 | 55.549 |
| smallest | 0.449 | 0.293 | 2.021 | 23.741 |
| largest | 0.827 | 0.600 | 7.200 | 84.600 |
| best_fixed | 0.827 | 0.600 | 7.200 | 84.600 |
| oracle | 0.929 | 0.787 | 2.552 | 29.985 |

## PL

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.626 | 0.325 | 6.878 | 35.704 |
| energy_pq | 0.627 | 0.312 | 6.481 | 33.827 |
| carbon | 0.647 | 0.336 | 6.898 | 36.716 |
| carbon_no_flesch | 0.684 | 0.376 | 8.036 | 42.399 |
| carbon_en_emb | 0.671 | 0.371 | 7.757 | 42.033 |
| carbon_onehot | 0.654 | 0.296 | 7.186 | 37.673 |
| carbon_ml_emb | 0.660 | 0.360 | 7.172 | 38.509 |
| lang_carbon | 0.657 | 0.336 | 7.385 | 38.738 |
| random | 0.661 | 0.413 | 10.744 | 55.549 |
| smallest | 0.449 | 0.293 | 4.591 | 23.741 |
| largest | 0.827 | 0.600 | 16.355 | 84.600 |
| best_fixed | 0.638 | 0.280 | 5.227 | 27.041 |
| oracle | 0.929 | 0.787 | 5.798 | 29.985 |
