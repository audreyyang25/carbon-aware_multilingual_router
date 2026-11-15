# Routing results: 20261115_135630

- Hardware: NVIDIA A100-SXM4-80GB; models: gemma-4-31b, gemma-4-e4b, qwen3.5-27b, qwen3.5-2b, qwen3.5-9b, tiny-aya-global
- Algorithm: linucb, lambda = 0.9, 5 runs, 250 queries/hour
- Zones: FR, SE-SE3, DE, US-CAL-CISO, US-NE-ISNE, PL

## Test phase, averaged over zones

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt | 0.682 | 0.417 | 3.050 | 52.189 |
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
| carbon_pt | 0.682 | 3.050 | 44.031 | 44.031 |
| random | 0.661 | 4.548 | 65.665 | 65.665 |
| smallest | 0.449 | 1.944 | 28.063 | 28.063 |
| largest | 0.827 | 6.927 | 100.000 | 100.000 |
| best_fixed | 0.662 | 3.379 | 48.779 | 48.779 |
| oracle | 0.904 | 2.558 | 36.932 | 36.932 |

Share of each strategy's total carbon spent on each benchmark:

| strategy | share of carbon belebele |
|---|---|
| carbon_pt | 1.000 |
| random | 1.000 |
| smallest | 1.000 |
| largest | 1.000 |
| best_fixed | 1.000 |
| oracle | 1.000 |

## Test accuracy by language (all zones)

| strategy | en | sw | am | gn | ha | ig | km | lo | my | ne | si | wo | yo | zu | worst |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| carbon_pt | 0.906 | 0.823 | 0.715 | 0.537 | 0.651 | 0.565 | 0.796 | 0.726 | 0.802 | 0.756 | 0.716 | 0.419 | 0.496 | 0.640 | 0.419 |
| random | 0.917 | 0.789 | 0.659 | 0.528 | 0.573 | 0.592 | 0.736 | 0.725 | 0.771 | 0.693 | 0.741 | 0.413 | 0.507 | 0.613 | 0.413 |
| smallest | 0.827 | 0.493 | 0.453 | 0.293 | 0.373 | 0.413 | 0.507 | 0.413 | 0.547 | 0.427 | 0.507 | 0.320 | 0.347 | 0.360 | 0.293 |
| largest | 0.987 | 0.920 | 0.880 | 0.773 | 0.800 | 0.747 | 0.907 | 0.813 | 0.880 | 0.893 | 0.960 | 0.600 | 0.627 | 0.787 | 0.600 |
| best_fixed | 0.887 | 0.817 | 0.705 | 0.518 | 0.630 | 0.559 | 0.766 | 0.706 | 0.736 | 0.736 | 0.589 | 0.417 | 0.541 | 0.654 | 0.417 |
| oracle | 0.979 | 0.964 | 0.903 | 0.867 | 0.874 | 0.886 | 0.985 | 0.900 | 0.960 | 0.919 | 0.974 | 0.732 | 0.807 | 0.900 | 0.732 |

## FR

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt | 0.827 | 0.600 | 0.884 | 85.101 |
| random | 0.661 | 0.413 | 0.578 | 55.549 |
| smallest | 0.449 | 0.293 | 0.247 | 23.741 |
| largest | 0.827 | 0.600 | 0.879 | 84.600 |
| best_fixed | 0.827 | 0.600 | 0.879 | 84.600 |
| oracle | 0.929 | 0.787 | 0.358 | 34.415 |

## SE-SE3

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt | 0.827 | 0.600 | 0.503 | 85.101 |
| random | 0.661 | 0.413 | 0.328 | 55.549 |
| smallest | 0.449 | 0.293 | 0.140 | 23.741 |
| largest | 0.827 | 0.600 | 0.500 | 84.600 |
| best_fixed | 0.827 | 0.600 | 0.500 | 84.600 |
| oracle | 0.929 | 0.787 | 0.203 | 34.415 |

## DE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt | 0.572 | 0.320 | 4.678 | 37.584 |
| random | 0.661 | 0.413 | 6.925 | 55.549 |
| smallest | 0.449 | 0.293 | 2.960 | 23.741 |
| largest | 0.827 | 0.600 | 10.546 | 84.600 |
| best_fixed | 0.569 | 0.333 | 5.092 | 40.848 |
| oracle | 0.883 | 0.672 | 3.907 | 31.558 |

## US-CAL-CISO

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt | 0.685 | 0.379 | 2.583 | 40.749 |
| random | 0.661 | 0.413 | 3.990 | 55.549 |
| smallest | 0.449 | 0.293 | 1.705 | 23.741 |
| largest | 0.827 | 0.600 | 6.080 | 84.600 |
| best_fixed | 0.610 | 0.301 | 2.430 | 32.564 |
| oracle | 0.922 | 0.768 | 2.438 | 34.048 |

## US-NE-ISNE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt | 0.638 | 0.280 | 2.344 | 27.542 |
| random | 0.661 | 0.413 | 4.725 | 55.549 |
| smallest | 0.449 | 0.293 | 2.021 | 23.741 |
| largest | 0.827 | 0.600 | 7.200 | 84.600 |
| best_fixed | 0.569 | 0.333 | 3.476 | 40.848 |
| oracle | 0.921 | 0.765 | 2.889 | 33.954 |

## PL

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt | 0.543 | 0.323 | 7.308 | 37.056 |
| random | 0.661 | 0.413 | 10.744 | 55.549 |
| smallest | 0.449 | 0.293 | 4.591 | 23.741 |
| largest | 0.827 | 0.600 | 16.355 | 84.600 |
| best_fixed | 0.569 | 0.333 | 7.896 | 40.848 |
| oracle | 0.839 | 0.616 | 5.553 | 28.831 |
