# Routing results: 20261115_143328

- Hardware: NVIDIA A100-SXM4-80GB; models: gemma-4-31b, gemma-4-e4b, qwen3.5-27b, qwen3.5-2b, qwen3.5-9b, tiny-aya-global
- Algorithm: linucb, lambda = 0.9, 5 runs, 250 queries/hour
- Zones: FR, SE-SE3, DE, US-CAL-CISO, US-NE-ISNE, PL

## Test phase, averaged over zones

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.671 | 0.360 | 3.062 | 54.230 |
| carbon_pt_floor | 0.763 | 0.455 | 5.134 | 72.745 |
| random | 0.661 | 0.413 | 4.548 | 55.549 |
| smallest | 0.449 | 0.293 | 1.944 | 23.741 |
| largest | 0.827 | 0.600 | 6.927 | 84.600 |
| best_fixed | 0.662 | 0.417 | 3.379 | 54.051 |
| oracle | 0.904 | 0.732 | 2.558 | 32.870 |

## Paired comparisons (all zones)

Router minus reference on the same queries. Accuracy in points, carbon in % of the reference. 95% bootstrap CI over test items; * = CI excludes 0.

## Test results by benchmark (all zones)

Pooled carbon above is a mean over all test queries, so it is almost entirely MGSM (an MGSM answer uses about 100x the energy of an XNLI or Belebele one). Here each benchmark is on its own; `% of largest` puts carbon on a common scale (always using the largest model = 100), and its benchmark average weights the three equally.

| strategy | acc belebele | gCO2/1k belebele | % of largest belebele | % of largest, benchmarks averaged |
|---|---|---|---|---|
| carbon_pt_lang | 0.671 | 3.062 | 44.205 | 44.205 |
| carbon_pt_floor | 0.763 | 5.134 | 74.114 | 74.114 |
| random | 0.661 | 4.548 | 65.665 | 65.665 |
| smallest | 0.449 | 1.944 | 28.063 | 28.063 |
| largest | 0.827 | 6.927 | 100.000 | 100.000 |
| best_fixed | 0.662 | 3.379 | 48.779 | 48.779 |
| oracle | 0.904 | 2.558 | 36.932 | 36.932 |

Share of each strategy's total carbon spent on each benchmark:

| strategy | share of carbon belebele |
|---|---|
| carbon_pt_lang | 1.000 |
| carbon_pt_floor | 1.000 |
| random | 1.000 |
| smallest | 1.000 |
| largest | 1.000 |
| best_fixed | 1.000 |
| oracle | 1.000 |

## Test accuracy by language (all zones)

| strategy | en | sw | am | gn | ha | ig | km | lo | my | ne | si | wo | yo | zu | worst |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| carbon_pt_lang | 0.864 | 0.809 | 0.687 | 0.464 | 0.612 | 0.583 | 0.787 | 0.745 | 0.783 | 0.708 | 0.798 | 0.388 | 0.526 | 0.643 | 0.388 |
| carbon_pt_floor | 0.915 | 0.869 | 0.781 | 0.727 | 0.758 | 0.664 | 0.849 | 0.782 | 0.853 | 0.812 | 0.880 | 0.465 | 0.596 | 0.738 | 0.465 |
| random | 0.917 | 0.789 | 0.659 | 0.528 | 0.573 | 0.592 | 0.736 | 0.725 | 0.771 | 0.693 | 0.741 | 0.413 | 0.507 | 0.613 | 0.413 |
| smallest | 0.827 | 0.493 | 0.453 | 0.293 | 0.373 | 0.413 | 0.507 | 0.413 | 0.547 | 0.427 | 0.507 | 0.320 | 0.347 | 0.360 | 0.293 |
| largest | 0.987 | 0.920 | 0.880 | 0.773 | 0.800 | 0.747 | 0.907 | 0.813 | 0.880 | 0.893 | 0.960 | 0.600 | 0.627 | 0.787 | 0.600 |
| best_fixed | 0.887 | 0.817 | 0.705 | 0.518 | 0.630 | 0.559 | 0.766 | 0.706 | 0.736 | 0.736 | 0.589 | 0.417 | 0.541 | 0.654 | 0.417 |
| oracle | 0.979 | 0.964 | 0.903 | 0.867 | 0.874 | 0.886 | 0.985 | 0.900 | 0.960 | 0.919 | 0.974 | 0.732 | 0.807 | 0.900 | 0.732 |

## FR

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.800 | 0.507 | 0.926 | 89.752 |
| carbon_pt_floor | 0.798 | 0.483 | 0.913 | 89.298 |
| random | 0.661 | 0.413 | 0.578 | 55.549 |
| smallest | 0.449 | 0.293 | 0.247 | 23.741 |
| largest | 0.827 | 0.600 | 0.879 | 84.600 |
| best_fixed | 0.827 | 0.600 | 0.879 | 84.600 |
| oracle | 0.929 | 0.787 | 0.358 | 34.415 |

## SE-SE3

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.801 | 0.507 | 0.530 | 89.648 |
| carbon_pt_floor | 0.808 | 0.528 | 0.547 | 91.451 |
| random | 0.661 | 0.413 | 0.328 | 55.549 |
| smallest | 0.449 | 0.293 | 0.140 | 23.741 |
| largest | 0.827 | 0.600 | 0.500 | 84.600 |
| best_fixed | 0.827 | 0.600 | 0.500 | 84.600 |
| oracle | 0.929 | 0.787 | 0.203 | 34.415 |

## DE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.604 | 0.296 | 4.266 | 34.210 |
| carbon_pt_floor | 0.757 | 0.512 | 7.798 | 62.647 |
| random | 0.661 | 0.413 | 6.925 | 55.549 |
| smallest | 0.449 | 0.293 | 2.960 | 23.741 |
| largest | 0.827 | 0.600 | 10.546 | 84.600 |
| best_fixed | 0.569 | 0.333 | 5.092 | 40.848 |
| oracle | 0.883 | 0.672 | 3.907 | 31.558 |

## US-CAL-CISO

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.639 | 0.299 | 2.831 | 41.093 |
| carbon_pt_floor | 0.755 | 0.421 | 4.971 | 67.932 |
| random | 0.661 | 0.413 | 3.990 | 55.549 |
| smallest | 0.449 | 0.293 | 1.705 | 23.741 |
| largest | 0.827 | 0.600 | 6.080 | 84.600 |
| best_fixed | 0.610 | 0.301 | 2.430 | 32.564 |
| oracle | 0.922 | 0.768 | 2.438 | 34.048 |

## US-NE-ISNE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.617 | 0.267 | 3.072 | 35.981 |
| carbon_pt_floor | 0.753 | 0.459 | 5.978 | 70.113 |
| random | 0.661 | 0.413 | 4.725 | 55.549 |
| smallest | 0.449 | 0.293 | 2.021 | 23.741 |
| largest | 0.827 | 0.600 | 7.200 | 84.600 |
| best_fixed | 0.569 | 0.333 | 3.476 | 40.848 |
| oracle | 0.921 | 0.765 | 2.889 | 33.954 |

## PL

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.565 | 0.285 | 6.747 | 34.697 |
| carbon_pt_floor | 0.710 | 0.325 | 10.595 | 55.027 |
| random | 0.661 | 0.413 | 10.744 | 55.549 |
| smallest | 0.449 | 0.293 | 4.591 | 23.741 |
| largest | 0.827 | 0.600 | 16.355 | 84.600 |
| best_fixed | 0.569 | 0.333 | 7.896 | 40.848 |
| oracle | 0.839 | 0.616 | 5.553 | 28.831 |
