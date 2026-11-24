# Routing results: 20261115_142821

- Hardware: NVIDIA A100-SXM4-80GB; models: gemma-4-31b, gemma-4-e4b, qwen3.5-27b, qwen3.5-2b, qwen3.5-9b, tiny-aya-global
- Algorithm: linucb, lambda = 0.7, 5 runs, 250 queries/hour
- Zones: FR, SE-SE3, DE, US-CAL-CISO, US-NE-ISNE, PL

## Test phase, averaged over zones

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.744 | 0.410 | 4.666 | 68.780 |
| carbon_pt_floor | 0.771 | 0.464 | 5.779 | 76.042 |
| random | 0.661 | 0.413 | 4.548 | 55.549 |
| smallest | 0.449 | 0.293 | 1.944 | 23.741 |
| largest | 0.827 | 0.600 | 6.927 | 84.600 |
| best_fixed | 0.763 | 0.489 | 4.198 | 66.780 |
| oracle | 0.929 | 0.787 | 2.817 | 34.415 |

## Paired comparisons (all zones)

Router minus reference on the same queries. Accuracy in points, carbon in % of the reference. 95% bootstrap CI over test items; * = CI excludes 0.

## Test results by benchmark (all zones)

Pooled carbon above is a mean over all test queries, so it is almost entirely MGSM (an MGSM answer uses about 100x the energy of an XNLI or Belebele one). Here each benchmark is on its own; `% of largest` puts carbon on a common scale (always using the largest model = 100), and its benchmark average weights the three equally.

| strategy | acc belebele | gCO2/1k belebele | % of largest belebele | % of largest, benchmarks averaged |
|---|---|---|---|---|
| carbon_pt_lang | 0.744 | 4.666 | 67.358 | 67.358 |
| carbon_pt_floor | 0.771 | 5.779 | 83.435 | 83.435 |
| random | 0.661 | 4.548 | 65.665 | 65.665 |
| smallest | 0.449 | 1.944 | 28.063 | 28.063 |
| largest | 0.827 | 6.927 | 100.000 | 100.000 |
| best_fixed | 0.763 | 4.198 | 60.607 | 60.607 |
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
| carbon_pt_lang | 0.913 | 0.862 | 0.767 | 0.688 | 0.741 | 0.571 | 0.823 | 0.783 | 0.857 | 0.788 | 0.881 | 0.438 | 0.589 | 0.715 | 0.438 |
| carbon_pt_floor | 0.932 | 0.877 | 0.785 | 0.727 | 0.751 | 0.631 | 0.858 | 0.777 | 0.861 | 0.823 | 0.908 | 0.494 | 0.615 | 0.756 | 0.494 |
| random | 0.917 | 0.789 | 0.659 | 0.528 | 0.573 | 0.592 | 0.736 | 0.725 | 0.771 | 0.693 | 0.741 | 0.413 | 0.507 | 0.613 | 0.413 |
| smallest | 0.827 | 0.493 | 0.453 | 0.293 | 0.373 | 0.413 | 0.507 | 0.413 | 0.547 | 0.427 | 0.507 | 0.320 | 0.347 | 0.360 | 0.293 |
| largest | 0.987 | 0.920 | 0.880 | 0.773 | 0.800 | 0.747 | 0.907 | 0.813 | 0.880 | 0.893 | 0.960 | 0.600 | 0.627 | 0.787 | 0.600 |
| best_fixed | 0.966 | 0.868 | 0.788 | 0.641 | 0.715 | 0.664 | 0.863 | 0.797 | 0.872 | 0.844 | 0.895 | 0.489 | 0.573 | 0.703 | 0.489 |
| oracle | 1.000 | 0.987 | 0.920 | 0.920 | 0.920 | 0.933 | 0.987 | 0.907 | 0.960 | 0.933 | 0.987 | 0.787 | 0.827 | 0.933 | 0.787 |

## FR

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.789 | 0.485 | 0.905 | 84.857 |
| carbon_pt_floor | 0.784 | 0.467 | 0.898 | 84.810 |
| random | 0.661 | 0.413 | 0.578 | 55.549 |
| smallest | 0.449 | 0.293 | 0.247 | 23.741 |
| largest | 0.827 | 0.600 | 0.879 | 84.600 |
| best_fixed | 0.827 | 0.600 | 0.879 | 84.600 |
| oracle | 0.929 | 0.787 | 0.358 | 34.415 |

## SE-SE3

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.792 | 0.477 | 0.481 | 82.025 |
| carbon_pt_floor | 0.793 | 0.456 | 0.509 | 85.417 |
| random | 0.661 | 0.413 | 0.328 | 55.549 |
| smallest | 0.449 | 0.293 | 0.140 | 23.741 |
| largest | 0.827 | 0.600 | 0.500 | 84.600 |
| best_fixed | 0.827 | 0.600 | 0.500 | 84.600 |
| oracle | 0.929 | 0.787 | 0.203 | 34.415 |

## DE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.702 | 0.347 | 6.457 | 52.177 |
| carbon_pt_floor | 0.754 | 0.435 | 8.343 | 66.536 |
| random | 0.661 | 0.413 | 6.925 | 55.549 |
| smallest | 0.449 | 0.293 | 2.960 | 23.741 |
| largest | 0.827 | 0.600 | 10.546 | 84.600 |
| best_fixed | 0.697 | 0.373 | 6.332 | 50.782 |
| oracle | 0.929 | 0.787 | 4.289 | 34.415 |

## US-CAL-CISO

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.771 | 0.411 | 5.419 | 76.942 |
| carbon_pt_floor | 0.772 | 0.464 | 5.136 | 74.135 |
| random | 0.661 | 0.413 | 3.990 | 55.549 |
| smallest | 0.449 | 0.293 | 1.705 | 23.741 |
| largest | 0.827 | 0.600 | 6.080 | 84.600 |
| best_fixed | 0.827 | 0.600 | 6.080 | 84.600 |
| oracle | 0.929 | 0.787 | 2.472 | 34.415 |

## US-NE-ISNE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.757 | 0.416 | 6.078 | 71.355 |
| carbon_pt_floor | 0.777 | 0.520 | 6.581 | 77.412 |
| random | 0.661 | 0.413 | 4.725 | 55.549 |
| smallest | 0.449 | 0.293 | 2.021 | 23.741 |
| largest | 0.827 | 0.600 | 7.200 | 84.600 |
| best_fixed | 0.749 | 0.464 | 5.406 | 64.309 |
| oracle | 0.929 | 0.787 | 2.930 | 34.415 |

## PL

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.654 | 0.325 | 8.653 | 45.326 |
| carbon_pt_floor | 0.745 | 0.440 | 13.209 | 67.938 |
| random | 0.661 | 0.413 | 10.744 | 55.549 |
| smallest | 0.449 | 0.293 | 4.591 | 23.741 |
| largest | 0.827 | 0.600 | 16.355 | 84.600 |
| best_fixed | 0.650 | 0.299 | 5.992 | 31.789 |
| oracle | 0.929 | 0.787 | 6.652 | 34.415 |
