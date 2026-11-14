# Routing results: 20261114_133247

- Hardware: NVIDIA A100-SXM4-80GB; models: gemma-4-31b, gemma-4-e4b, qwen3.5-27b, qwen3.5-2b, qwen3.5-9b, tiny-aya-global
- Algorithm: linucb, lambda = 0.3, 5 runs, 250 queries/hour
- Zones: FR, SE-SE3, DE, US-CAL-CISO, US-NE-ISNE, PL

## Test phase, averaged over zones

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.802 | 0.565 | 7.677 | 93.711 |
| energy_pq | 0.795 | 0.541 | 6.617 | 80.843 |
| carbon | 0.808 | 0.573 | 6.885 | 87.040 |
| carbon_no_flesch | 0.807 | 0.578 | 6.886 | 86.809 |
| carbon_en_emb | 0.793 | 0.540 | 6.561 | 84.542 |
| carbon_onehot | 0.800 | 0.540 | 6.580 | 83.956 |
| carbon_ml_emb | 0.798 | 0.568 | 6.719 | 85.862 |
| lang_carbon | 0.791 | 0.533 | 6.474 | 83.221 |
| random | 0.661 | 0.413 | 4.548 | 55.549 |
| smallest | 0.449 | 0.293 | 1.944 | 23.741 |
| largest | 0.827 | 0.600 | 6.927 | 84.600 |
| best_fixed | 0.827 | 0.600 | 6.927 | 84.600 |
| oracle | 0.929 | 0.787 | 2.455 | 29.985 |

## Paired comparisons (all zones)

Router minus reference on the same queries. Accuracy in points, carbon in % of the reference. 95% bootstrap CI over test items; * = CI excludes 0.

| comparison | question | accuracy (pp) | carbon (%) |
|---|---|---|---|
| lang_carbon vs largest | Savings vs always using the largest model | -3.5 [-4.7, -2.4] * | -6.5% [-7.6, -5.4] * |
| lang_carbon vs best_fixed | vs the best single model in hindsight | -3.5 [-4.7, -2.4] * | -6.5% [-7.6, -5.4] * |
| lang_carbon vs greenserv | vs GreenServ (energy-per-token cost, English features) | -1.1 [-1.8, -0.3] * | -15.7% [-16.9, -14.5] * |
| lang_carbon vs carbon_no_flesch | Do language + multilingual embedding help? | -1.6 [-2.1, -1.1] * | -6.0% [-7.1, -4.9] * |
| lang_carbon vs carbon_onehot | Does the embedding add beyond the language label? | -0.8 [-1.3, -0.4] * | -1.6% [-2.7, -0.5] * |
| lang_carbon vs carbon_ml_emb | Does the language label add beyond the embedding? | -0.7 [-1.1, -0.2] * | -3.6% [-4.6, -2.6] * |
| carbon_ml_emb vs carbon_en_emb | Multilingual vs English encoder | +0.5 [+0.0, +1.0] * | +2.4% [+1.0, +4.0] * |
| carbon vs energy_pq | Does seeing the grid help? (carbon vs energy cost) | +1.3 [+0.7, +1.9] * | +4.1% [+3.7, +4.4] * |
| carbon vs carbon_no_flesch | Does Flesch complexity help? | +0.1 [-0.1, +0.3] | -0.0% [-0.2, +0.2] |
| carbon vs greenserv | Carbon cost vs GreenServ's energy-per-token cost | +0.6 [+0.0, +1.2] * | -10.3% [-10.9, -9.7] * |

## Test results by benchmark (all zones)

Pooled carbon above is a mean over all test queries, so it is almost entirely MGSM (an MGSM answer uses about 100x the energy of an XNLI or Belebele one). Here each benchmark is on its own; `% of largest` puts carbon on a common scale (always using the largest model = 100), and its benchmark average weights the three equally.

| strategy | acc belebele | gCO2/1k belebele | % of largest belebele | % of largest, benchmarks averaged |
|---|---|---|---|---|
| greenserv | 0.802 | 7.677 | 110.826 | 110.826 |
| energy_pq | 0.795 | 6.617 | 95.525 | 95.525 |
| carbon | 0.808 | 6.885 | 99.395 | 99.395 |
| carbon_no_flesch | 0.807 | 6.886 | 99.410 | 99.410 |
| carbon_en_emb | 0.793 | 6.561 | 94.718 | 94.718 |
| carbon_onehot | 0.800 | 6.580 | 94.993 | 94.993 |
| carbon_ml_emb | 0.798 | 6.719 | 97.006 | 97.006 |
| lang_carbon | 0.791 | 6.474 | 93.466 | 93.466 |
| random | 0.661 | 4.548 | 65.665 | 65.665 |
| smallest | 0.449 | 1.944 | 28.063 | 28.063 |
| largest | 0.827 | 6.927 | 100.000 | 100.000 |
| best_fixed | 0.827 | 6.927 | 100.000 | 100.000 |
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
| greenserv | 0.957 | 0.907 | 0.808 | 0.709 | 0.779 | 0.765 | 0.875 | 0.811 | 0.875 | 0.845 | 0.923 | 0.581 | 0.651 | 0.741 | 0.581 |
| energy_pq | 0.976 | 0.899 | 0.821 | 0.712 | 0.755 | 0.723 | 0.875 | 0.795 | 0.880 | 0.859 | 0.928 | 0.549 | 0.621 | 0.741 | 0.549 |
| carbon | 0.979 | 0.916 | 0.819 | 0.740 | 0.782 | 0.756 | 0.876 | 0.797 | 0.879 | 0.849 | 0.925 | 0.580 | 0.643 | 0.772 | 0.580 |
| carbon_no_flesch | 0.982 | 0.922 | 0.802 | 0.756 | 0.783 | 0.749 | 0.867 | 0.799 | 0.876 | 0.848 | 0.924 | 0.578 | 0.636 | 0.778 | 0.578 |
| carbon_en_emb | 0.960 | 0.903 | 0.815 | 0.732 | 0.771 | 0.736 | 0.853 | 0.788 | 0.866 | 0.836 | 0.921 | 0.540 | 0.622 | 0.761 | 0.540 |
| carbon_onehot | 0.978 | 0.918 | 0.796 | 0.750 | 0.752 | 0.736 | 0.864 | 0.786 | 0.876 | 0.856 | 0.938 | 0.544 | 0.625 | 0.777 | 0.544 |
| carbon_ml_emb | 0.968 | 0.897 | 0.821 | 0.744 | 0.782 | 0.722 | 0.872 | 0.797 | 0.872 | 0.846 | 0.909 | 0.570 | 0.619 | 0.753 | 0.570 |
| lang_carbon | 0.972 | 0.898 | 0.828 | 0.743 | 0.773 | 0.724 | 0.856 | 0.779 | 0.859 | 0.837 | 0.909 | 0.535 | 0.618 | 0.748 | 0.535 |
| random | 0.917 | 0.789 | 0.659 | 0.528 | 0.573 | 0.592 | 0.736 | 0.725 | 0.771 | 0.693 | 0.741 | 0.413 | 0.507 | 0.613 | 0.413 |
| smallest | 0.827 | 0.493 | 0.453 | 0.293 | 0.373 | 0.413 | 0.507 | 0.413 | 0.547 | 0.427 | 0.507 | 0.320 | 0.347 | 0.360 | 0.293 |
| largest | 0.987 | 0.920 | 0.880 | 0.773 | 0.800 | 0.747 | 0.907 | 0.813 | 0.880 | 0.893 | 0.960 | 0.600 | 0.627 | 0.787 | 0.600 |
| best_fixed | 0.987 | 0.920 | 0.880 | 0.773 | 0.800 | 0.747 | 0.907 | 0.813 | 0.880 | 0.893 | 0.960 | 0.600 | 0.627 | 0.787 | 0.600 |
| oracle | 1.000 | 0.987 | 0.920 | 0.920 | 0.920 | 0.933 | 0.987 | 0.907 | 0.960 | 0.933 | 0.987 | 0.787 | 0.827 | 0.933 | 0.787 |

## FR

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.802 | 0.565 | 0.941 | 93.711 |
| energy_pq | 0.795 | 0.541 | 0.902 | 80.843 |
| carbon | 0.804 | 0.579 | 0.957 | 88.254 |
| carbon_no_flesch | 0.815 | 0.589 | 0.885 | 89.172 |
| carbon_en_emb | 0.806 | 0.571 | 0.942 | 92.684 |
| carbon_onehot | 0.808 | 0.539 | 0.935 | 89.984 |
| carbon_ml_emb | 0.810 | 0.587 | 0.931 | 89.622 |
| lang_carbon | 0.803 | 0.541 | 0.944 | 88.539 |
| random | 0.661 | 0.413 | 0.578 | 55.549 |
| smallest | 0.449 | 0.293 | 0.247 | 23.741 |
| largest | 0.827 | 0.600 | 0.879 | 84.600 |
| best_fixed | 0.827 | 0.600 | 0.879 | 84.600 |
| oracle | 0.929 | 0.787 | 0.312 | 29.985 |

## SE-SE3

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.802 | 0.565 | 0.564 | 93.711 |
| energy_pq | 0.795 | 0.541 | 0.480 | 80.843 |
| carbon | 0.804 | 0.579 | 0.520 | 88.254 |
| carbon_no_flesch | 0.815 | 0.589 | 0.527 | 89.172 |
| carbon_en_emb | 0.807 | 0.560 | 0.539 | 90.521 |
| carbon_onehot | 0.807 | 0.539 | 0.513 | 87.141 |
| carbon_ml_emb | 0.798 | 0.555 | 0.547 | 92.774 |
| lang_carbon | 0.802 | 0.544 | 0.519 | 87.343 |
| random | 0.661 | 0.413 | 0.328 | 55.549 |
| smallest | 0.449 | 0.293 | 0.140 | 23.741 |
| largest | 0.827 | 0.600 | 0.500 | 84.600 |
| best_fixed | 0.827 | 0.600 | 0.500 | 84.600 |
| oracle | 0.929 | 0.787 | 0.177 | 29.985 |

## DE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.802 | 0.565 | 11.615 | 93.711 |
| energy_pq | 0.795 | 0.541 | 10.210 | 80.843 |
| carbon | 0.817 | 0.584 | 10.681 | 85.970 |
| carbon_no_flesch | 0.809 | 0.589 | 10.472 | 84.461 |
| carbon_en_emb | 0.790 | 0.523 | 10.230 | 81.251 |
| carbon_onehot | 0.793 | 0.528 | 10.099 | 80.570 |
| carbon_ml_emb | 0.798 | 0.555 | 10.696 | 85.019 |
| lang_carbon | 0.801 | 0.544 | 10.449 | 83.075 |
| random | 0.661 | 0.413 | 6.925 | 55.549 |
| smallest | 0.449 | 0.293 | 2.960 | 23.741 |
| largest | 0.827 | 0.600 | 10.546 | 84.600 |
| best_fixed | 0.827 | 0.600 | 10.546 | 84.600 |
| oracle | 0.929 | 0.787 | 3.738 | 29.985 |

## US-CAL-CISO

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.802 | 0.565 | 6.848 | 93.711 |
| energy_pq | 0.795 | 0.541 | 5.561 | 80.843 |
| carbon | 0.823 | 0.584 | 6.866 | 95.169 |
| carbon_no_flesch | 0.814 | 0.584 | 6.849 | 93.340 |
| carbon_en_emb | 0.806 | 0.552 | 6.434 | 87.367 |
| carbon_onehot | 0.805 | 0.549 | 6.315 | 87.849 |
| carbon_ml_emb | 0.814 | 0.595 | 6.567 | 88.729 |
| lang_carbon | 0.807 | 0.579 | 6.256 | 87.444 |
| random | 0.661 | 0.413 | 3.990 | 55.549 |
| smallest | 0.449 | 0.293 | 1.705 | 23.741 |
| largest | 0.827 | 0.600 | 6.080 | 84.600 |
| best_fixed | 0.827 | 0.600 | 6.080 | 84.600 |
| oracle | 0.929 | 0.787 | 2.155 | 29.985 |

## US-NE-ISNE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.802 | 0.565 | 7.987 | 93.711 |
| energy_pq | 0.795 | 0.541 | 6.891 | 80.843 |
| carbon | 0.815 | 0.584 | 7.472 | 87.779 |
| carbon_no_flesch | 0.803 | 0.584 | 7.498 | 88.279 |
| carbon_en_emb | 0.793 | 0.528 | 7.114 | 83.619 |
| carbon_onehot | 0.804 | 0.539 | 7.244 | 85.160 |
| carbon_ml_emb | 0.807 | 0.597 | 7.378 | 86.538 |
| lang_carbon | 0.794 | 0.552 | 7.297 | 85.619 |
| random | 0.661 | 0.413 | 4.725 | 55.549 |
| smallest | 0.449 | 0.293 | 2.021 | 23.741 |
| largest | 0.827 | 0.600 | 7.200 | 84.600 |
| best_fixed | 0.827 | 0.600 | 7.200 | 84.600 |
| oracle | 0.929 | 0.787 | 2.552 | 29.985 |

## PL

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.802 | 0.565 | 18.104 | 93.711 |
| energy_pq | 0.795 | 0.541 | 15.657 | 80.843 |
| carbon | 0.785 | 0.528 | 14.813 | 76.817 |
| carbon_no_flesch | 0.786 | 0.533 | 15.084 | 76.429 |
| carbon_en_emb | 0.756 | 0.507 | 14.105 | 71.807 |
| carbon_onehot | 0.781 | 0.549 | 14.374 | 73.035 |
| carbon_ml_emb | 0.762 | 0.517 | 14.198 | 72.492 |
| lang_carbon | 0.742 | 0.437 | 13.380 | 67.308 |
| random | 0.661 | 0.413 | 10.744 | 55.549 |
| smallest | 0.449 | 0.293 | 4.591 | 23.741 |
| largest | 0.827 | 0.600 | 16.355 | 84.600 |
| best_fixed | 0.827 | 0.600 | 16.355 | 84.600 |
| oracle | 0.929 | 0.787 | 5.798 | 29.985 |
