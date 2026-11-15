# Routing results: 20261115_142315

- Hardware: NVIDIA A100-SXM4-80GB; models: gemma-4-31b, gemma-4-e4b, qwen3.5-27b, qwen3.5-2b, qwen3.5-9b, tiny-aya-global
- Algorithm: linucb, lambda = 0.5, 5 runs, 250 queries/hour
- Zones: FR, SE-SE3, DE, US-CAL-CISO, US-NE-ISNE, PL

## Test phase, averaged over zones

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.786 | 0.487 | 6.115 | 80.175 |
| carbon_pt_floor | 0.783 | 0.503 | 6.065 | 79.326 |
| random | 0.661 | 0.413 | 4.548 | 55.549 |
| smallest | 0.449 | 0.293 | 1.944 | 23.741 |
| largest | 0.827 | 0.600 | 6.927 | 84.600 |
| best_fixed | 0.809 | 0.570 | 6.019 | 80.091 |
| oracle | 0.929 | 0.787 | 2.817 | 34.415 |

## Paired comparisons (all zones)

Router minus reference on the same queries. Accuracy in points, carbon in % of the reference. 95% bootstrap CI over test items; * = CI excludes 0.

## Test results by benchmark (all zones)

Pooled carbon above is a mean over all test queries, so it is almost entirely MGSM (an MGSM answer uses about 100x the energy of an XNLI or Belebele one). Here each benchmark is on its own; `% of largest` puts carbon on a common scale (always using the largest model = 100), and its benchmark average weights the three equally.

| strategy | acc belebele | gCO2/1k belebele | % of largest belebele | % of largest, benchmarks averaged |
|---|---|---|---|---|
| carbon_pt_lang | 0.786 | 6.115 | 88.277 | 88.277 |
| carbon_pt_floor | 0.783 | 6.065 | 87.566 | 87.566 |
| random | 0.661 | 4.548 | 65.665 | 65.665 |
| smallest | 0.449 | 1.944 | 28.063 | 28.063 |
| largest | 0.827 | 6.927 | 100.000 | 100.000 |
| best_fixed | 0.809 | 6.019 | 86.899 | 86.899 |
| oracle | 0.929 | 2.817 | 40.673 | 40.673 |

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
| carbon_pt_lang | 0.947 | 0.905 | 0.819 | 0.733 | 0.779 | 0.677 | 0.858 | 0.789 | 0.876 | 0.819 | 0.912 | 0.501 | 0.627 | 0.754 | 0.501 |
| carbon_pt_floor | 0.942 | 0.888 | 0.772 | 0.739 | 0.774 | 0.689 | 0.864 | 0.784 | 0.856 | 0.809 | 0.929 | 0.527 | 0.621 | 0.767 | 0.527 |
| random | 0.917 | 0.789 | 0.659 | 0.528 | 0.573 | 0.592 | 0.736 | 0.725 | 0.771 | 0.693 | 0.741 | 0.413 | 0.507 | 0.613 | 0.413 |
| smallest | 0.827 | 0.493 | 0.453 | 0.293 | 0.373 | 0.413 | 0.507 | 0.413 | 0.547 | 0.427 | 0.507 | 0.320 | 0.347 | 0.360 | 0.293 |
| largest | 0.987 | 0.920 | 0.880 | 0.773 | 0.800 | 0.747 | 0.907 | 0.813 | 0.880 | 0.893 | 0.960 | 0.600 | 0.627 | 0.787 | 0.600 |
| best_fixed | 0.983 | 0.904 | 0.853 | 0.736 | 0.773 | 0.727 | 0.894 | 0.812 | 0.876 | 0.879 | 0.940 | 0.570 | 0.618 | 0.765 | 0.570 |
| oracle | 1.000 | 0.987 | 0.920 | 0.920 | 0.920 | 0.933 | 0.987 | 0.907 | 0.960 | 0.933 | 0.987 | 0.787 | 0.827 | 0.933 | 0.787 |

## FR

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.799 | 0.509 | 0.890 | 86.731 |
| carbon_pt_floor | 0.800 | 0.448 | 0.885 | 87.120 |
| random | 0.661 | 0.413 | 0.578 | 55.549 |
| smallest | 0.449 | 0.293 | 0.247 | 23.741 |
| largest | 0.827 | 0.600 | 0.879 | 84.600 |
| best_fixed | 0.827 | 0.600 | 0.879 | 84.600 |
| oracle | 0.929 | 0.787 | 0.358 | 34.415 |

## SE-SE3

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.802 | 0.512 | 0.522 | 88.095 |
| carbon_pt_floor | 0.806 | 0.528 | 0.512 | 86.265 |
| random | 0.661 | 0.413 | 0.328 | 55.549 |
| smallest | 0.449 | 0.293 | 0.140 | 23.741 |
| largest | 0.827 | 0.600 | 0.500 | 84.600 |
| best_fixed | 0.827 | 0.600 | 0.500 | 84.600 |
| oracle | 0.929 | 0.787 | 0.203 | 34.415 |

## DE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.780 | 0.480 | 9.148 | 72.749 |
| carbon_pt_floor | 0.765 | 0.499 | 9.113 | 72.857 |
| random | 0.661 | 0.413 | 6.925 | 55.549 |
| smallest | 0.449 | 0.293 | 2.960 | 23.741 |
| largest | 0.827 | 0.600 | 10.546 | 84.600 |
| best_fixed | 0.827 | 0.600 | 10.546 | 84.600 |
| oracle | 0.929 | 0.787 | 4.289 | 34.415 |

## US-CAL-CISO

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.793 | 0.507 | 5.961 | 83.921 |
| carbon_pt_floor | 0.797 | 0.581 | 5.837 | 81.615 |
| random | 0.661 | 0.413 | 3.990 | 55.549 |
| smallest | 0.449 | 0.293 | 1.705 | 23.741 |
| largest | 0.827 | 0.600 | 6.080 | 84.600 |
| best_fixed | 0.827 | 0.600 | 6.080 | 84.600 |
| oracle | 0.929 | 0.787 | 2.472 | 34.415 |

## US-NE-ISNE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.788 | 0.475 | 7.000 | 82.229 |
| carbon_pt_floor | 0.788 | 0.509 | 6.838 | 80.513 |
| random | 0.661 | 0.413 | 4.725 | 55.549 |
| smallest | 0.449 | 0.293 | 2.021 | 23.741 |
| largest | 0.827 | 0.600 | 7.200 | 84.600 |
| best_fixed | 0.827 | 0.600 | 7.200 | 84.600 |
| oracle | 0.929 | 0.787 | 2.930 | 34.415 |

## PL

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.750 | 0.440 | 13.168 | 67.322 |
| carbon_pt_floor | 0.742 | 0.451 | 13.206 | 67.584 |
| random | 0.661 | 0.413 | 10.744 | 55.549 |
| smallest | 0.449 | 0.293 | 4.591 | 23.741 |
| largest | 0.827 | 0.600 | 16.355 | 84.600 |
| best_fixed | 0.723 | 0.419 | 10.910 | 57.545 |
| oracle | 0.929 | 0.787 | 6.652 | 34.415 |
