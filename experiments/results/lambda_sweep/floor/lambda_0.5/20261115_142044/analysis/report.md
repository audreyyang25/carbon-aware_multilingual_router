# Routing results: 20261115_142044

- Hardware: NVIDIA A100-SXM4-80GB; models: gemma-4-31b, gemma-4-e4b, qwen3.5-27b, qwen3.5-2b, qwen3.5-9b, tiny-aya-global
- Algorithm: linucb, lambda = 0.5, 5 runs, 250 queries/hour
- Zones: FR, SE-SE3, DE, US-CAL-CISO, US-NE-ISNE, PL

## Test phase, averaged over zones

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.858 | 0.795 | 42.285 | 850.944 |
| carbon_pt_floor | 0.863 | 0.808 | 45.045 | 870.110 |
| random | 0.788 | 0.710 | 40.137 | 656.132 |
| smallest | 0.652 | 0.451 | 16.137 | 263.968 |
| largest | 0.871 | 0.813 | 62.913 | 1029.025 |
| best_fixed | 0.862 | 0.773 | 35.701 | 722.598 |
| oracle | 0.975 | 0.956 | 15.133 | 247.624 |

## Paired comparisons (all zones)

Router minus reference on the same queries. Accuracy in points, carbon in % of the reference. 95% bootstrap CI over test items; * = CI excludes 0.

## Test results by benchmark (all zones)

Pooled carbon above is a mean over all test queries, so it is almost entirely MGSM (an MGSM answer uses about 100x the energy of an XNLI or Belebele one). Here each benchmark is on its own; `% of largest` puts carbon on a common scale (always using the largest model = 100), and its benchmark average weights the three equally.

| strategy | acc belebele | acc mgsm | acc xnli | gCO2/1k belebele | gCO2/1k mgsm | gCO2/1k xnli | % of largest belebele | % of largest mgsm | % of largest xnli | % of largest, benchmarks averaged |
|---|---|---|---|---|---|---|---|---|---|---|
| carbon_pt_lang | 0.929 | 0.917 | 0.761 | 3.253 | 228.126 | 2.024 | 75.975 | 66.925 | 68.606 | 70.502 |
| carbon_pt_floor | 0.929 | 0.921 | 0.773 | 3.070 | 243.844 | 2.198 | 71.696 | 71.536 | 74.526 | 72.586 |
| random | 0.860 | 0.825 | 0.700 | 2.437 | 218.092 | 1.908 | 56.918 | 63.982 | 64.697 | 61.865 |
| smallest | 0.730 | 0.609 | 0.593 | 0.951 | 87.642 | 0.813 | 22.211 | 25.712 | 27.565 | 25.162 |
| largest | 0.945 | 0.945 | 0.765 | 4.282 | 340.867 | 2.950 | 100.000 | 100.000 | 100.000 | 100.000 |
| best_fixed | 0.919 | 0.909 | 0.785 | 2.237 | 193.439 | 1.863 | 52.244 | 56.749 | 63.165 | 57.386 |
| oracle | 0.973 | 0.977 | 0.977 | 1.292 | 79.766 | 1.396 | 30.183 | 23.401 | 47.332 | 33.638 |

Share of each strategy's total carbon spent on each benchmark:

| strategy | share of carbon belebele | share of carbon mgsm | share of carbon xnli |
|---|---|---|---|
| carbon_pt_lang | 0.030 | 0.951 | 0.019 |
| carbon_pt_floor | 0.028 | 0.953 | 0.020 |
| random | 0.025 | 0.955 | 0.020 |
| smallest | 0.024 | 0.955 | 0.021 |
| largest | 0.028 | 0.953 | 0.019 |
| best_fixed | 0.026 | 0.953 | 0.021 |
| oracle | 0.035 | 0.927 | 0.038 |

## Test accuracy by language (all zones)

| strategy | en | de | es | fr | ru | zh | th | sw | worst |
|---|---|---|---|---|---|---|---|---|---|
| carbon_pt_lang | 0.932 | 0.859 | 0.889 | 0.871 | 0.848 | 0.842 | 0.816 | 0.803 | 0.803 |
| carbon_pt_floor | 0.930 | 0.858 | 0.895 | 0.880 | 0.850 | 0.853 | 0.826 | 0.813 | 0.813 |
| random | 0.854 | 0.816 | 0.792 | 0.811 | 0.785 | 0.776 | 0.758 | 0.710 | 0.710 |
| smallest | 0.753 | 0.687 | 0.659 | 0.703 | 0.670 | 0.659 | 0.637 | 0.451 | 0.451 |
| largest | 0.940 | 0.879 | 0.901 | 0.890 | 0.852 | 0.863 | 0.830 | 0.813 | 0.813 |
| best_fixed | 0.940 | 0.861 | 0.905 | 0.883 | 0.852 | 0.855 | 0.830 | 0.773 | 0.773 |
| oracle | 0.995 | 0.973 | 0.973 | 0.973 | 0.978 | 0.956 | 0.967 | 0.989 | 0.956 |

## FR

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.867 | 0.805 | 7.063 | 1122.987 |
| carbon_pt_floor | 0.866 | 0.802 | 6.983 | 1109.438 |
| random | 0.788 | 0.710 | 4.121 | 656.132 |
| smallest | 0.652 | 0.451 | 1.661 | 263.968 |
| largest | 0.871 | 0.813 | 6.474 | 1029.025 |
| best_fixed | 0.871 | 0.813 | 6.474 | 1029.025 |
| oracle | 0.975 | 0.956 | 1.556 | 247.624 |

## SE-SE3

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.868 | 0.804 | 5.522 | 1069.028 |
| carbon_pt_floor | 0.869 | 0.814 | 5.653 | 1091.780 |
| random | 0.788 | 0.710 | 3.423 | 656.132 |
| smallest | 0.652 | 0.451 | 1.370 | 263.968 |
| largest | 0.871 | 0.813 | 5.343 | 1029.025 |
| best_fixed | 0.871 | 0.813 | 5.343 | 1029.025 |
| oracle | 0.975 | 0.956 | 1.286 | 247.624 |

## DE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.864 | 0.796 | 36.632 | 785.476 |
| carbon_pt_floor | 0.862 | 0.802 | 35.997 | 762.591 |
| random | 0.788 | 0.710 | 31.908 | 656.132 |
| smallest | 0.652 | 0.451 | 12.861 | 263.968 |
| largest | 0.871 | 0.813 | 50.171 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 27.762 | 569.385 |
| oracle | 0.975 | 0.956 | 12.073 | 247.624 |

## US-CAL-CISO

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.871 | 0.815 | 57.204 | 812.731 |
| carbon_pt_floor | 0.871 | 0.815 | 57.204 | 812.731 |
| random | 0.788 | 0.710 | 44.790 | 656.132 |
| smallest | 0.652 | 0.451 | 17.832 | 263.968 |
| largest | 0.871 | 0.813 | 69.453 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 38.519 | 569.385 |
| oracle | 0.975 | 0.956 | 16.669 | 247.624 |

## US-NE-ISNE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.857 | 0.799 | 73.862 | 802.440 |
| carbon_pt_floor | 0.865 | 0.818 | 79.618 | 863.697 |
| random | 0.788 | 0.710 | 61.015 | 656.132 |
| smallest | 0.652 | 0.451 | 24.534 | 263.968 |
| largest | 0.871 | 0.813 | 95.650 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 52.914 | 569.385 |
| oracle | 0.975 | 0.956 | 23.012 | 247.624 |

## PL

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.819 | 0.749 | 73.424 | 513.001 |
| carbon_pt_floor | 0.846 | 0.796 | 84.814 | 580.421 |
| random | 0.788 | 0.710 | 95.564 | 656.132 |
| smallest | 0.652 | 0.451 | 38.561 | 263.968 |
| largest | 0.871 | 0.813 | 150.386 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 83.193 | 569.385 |
| oracle | 0.975 | 0.956 | 36.201 | 247.624 |
