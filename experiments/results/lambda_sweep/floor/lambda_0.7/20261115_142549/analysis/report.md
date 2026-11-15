# Routing results: 20261115_142549

- Hardware: NVIDIA A100-SXM4-80GB; models: gemma-4-31b, gemma-4-e4b, qwen3.5-27b, qwen3.5-2b, qwen3.5-9b, tiny-aya-global
- Algorithm: linucb, lambda = 0.7, 5 runs, 250 queries/hour
- Zones: FR, SE-SE3, DE, US-CAL-CISO, US-NE-ISNE, PL

## Test phase, averaged over zones

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.829 | 0.755 | 27.130 | 656.423 |
| carbon_pt_floor | 0.856 | 0.795 | 37.520 | 751.250 |
| random | 0.788 | 0.710 | 40.137 | 656.132 |
| smallest | 0.652 | 0.451 | 16.137 | 263.968 |
| largest | 0.871 | 0.813 | 62.913 | 1029.025 |
| best_fixed | 0.816 | 0.742 | 21.835 | 604.261 |
| oracle | 0.975 | 0.956 | 14.977 | 246.797 |

## Paired comparisons (all zones)

Router minus reference on the same queries. Accuracy in points, carbon in % of the reference. 95% bootstrap CI over test items; * = CI excludes 0.

## Test results by benchmark (all zones)

Pooled carbon above is a mean over all test queries, so it is almost entirely MGSM (an MGSM answer uses about 100x the energy of an XNLI or Belebele one). Here each benchmark is on its own; `% of largest` puts carbon on a common scale (always using the largest model = 100), and its benchmark average weights the three equally.

| strategy | acc belebele | acc mgsm | acc xnli | gCO2/1k belebele | gCO2/1k mgsm | gCO2/1k xnli | % of largest belebele | % of largest mgsm | % of largest xnli | % of largest, benchmarks averaged |
|---|---|---|---|---|---|---|---|---|---|---|
| carbon_pt_lang | 0.904 | 0.873 | 0.735 | 2.298 | 145.010 | 1.666 | 53.659 | 42.542 | 56.481 | 50.894 |
| carbon_pt_floor | 0.924 | 0.920 | 0.759 | 2.919 | 202.197 | 1.858 | 68.157 | 59.318 | 63.004 | 63.493 |
| random | 0.860 | 0.825 | 0.700 | 2.437 | 218.092 | 1.908 | 56.918 | 63.982 | 64.697 | 61.865 |
| smallest | 0.730 | 0.609 | 0.593 | 0.951 | 87.642 | 0.813 | 22.211 | 25.712 | 27.565 | 25.162 |
| largest | 0.945 | 0.945 | 0.765 | 4.282 | 340.867 | 2.950 | 100.000 | 100.000 | 100.000 | 100.000 |
| best_fixed | 0.877 | 0.837 | 0.746 | 1.895 | 115.722 | 1.716 | 44.253 | 33.949 | 58.182 | 45.461 |
| oracle | 0.973 | 0.976 | 0.977 | 1.292 | 78.881 | 1.396 | 30.183 | 23.141 | 47.327 | 33.550 |

Share of each strategy's total carbon spent on each benchmark:

| strategy | share of carbon belebele | share of carbon mgsm | share of carbon xnli |
|---|---|---|---|
| carbon_pt_lang | 0.033 | 0.944 | 0.023 |
| carbon_pt_floor | 0.030 | 0.951 | 0.020 |
| random | 0.025 | 0.955 | 0.020 |
| smallest | 0.024 | 0.955 | 0.021 |
| largest | 0.028 | 0.953 | 0.019 |
| best_fixed | 0.037 | 0.930 | 0.033 |
| oracle | 0.035 | 0.927 | 0.038 |

## Test accuracy by language (all zones)

| strategy | en | de | es | fr | ru | zh | th | sw | worst |
|---|---|---|---|---|---|---|---|---|---|
| carbon_pt_lang | 0.912 | 0.832 | 0.844 | 0.858 | 0.826 | 0.800 | 0.775 | 0.783 | 0.775 |
| carbon_pt_floor | 0.922 | 0.844 | 0.890 | 0.871 | 0.847 | 0.850 | 0.811 | 0.810 | 0.810 |
| random | 0.854 | 0.816 | 0.792 | 0.811 | 0.785 | 0.776 | 0.758 | 0.710 | 0.710 |
| smallest | 0.753 | 0.687 | 0.659 | 0.703 | 0.670 | 0.659 | 0.637 | 0.451 | 0.451 |
| largest | 0.940 | 0.879 | 0.901 | 0.890 | 0.852 | 0.863 | 0.830 | 0.813 | 0.813 |
| best_fixed | 0.890 | 0.820 | 0.840 | 0.842 | 0.809 | 0.799 | 0.775 | 0.751 | 0.751 |
| oracle | 0.995 | 0.973 | 0.973 | 0.972 | 0.978 | 0.956 | 0.967 | 0.988 | 0.956 |

## FR

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.868 | 0.814 | 6.519 | 1033.154 |
| carbon_pt_floor | 0.868 | 0.814 | 6.519 | 1033.154 |
| random | 0.788 | 0.710 | 4.121 | 656.132 |
| smallest | 0.652 | 0.451 | 1.661 | 263.968 |
| largest | 0.871 | 0.813 | 6.474 | 1029.025 |
| best_fixed | 0.871 | 0.813 | 6.474 | 1029.025 |
| oracle | 0.975 | 0.956 | 1.556 | 247.624 |

## SE-SE3

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.868 | 0.816 | 5.285 | 1026.206 |
| carbon_pt_floor | 0.868 | 0.816 | 5.285 | 1026.206 |
| random | 0.788 | 0.710 | 3.423 | 656.132 |
| smallest | 0.652 | 0.451 | 1.370 | 263.968 |
| largest | 0.871 | 0.813 | 5.343 | 1029.025 |
| best_fixed | 0.871 | 0.813 | 5.343 | 1029.025 |
| oracle | 0.975 | 0.956 | 1.286 | 247.624 |

## DE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.836 | 0.768 | 27.194 | 552.040 |
| carbon_pt_floor | 0.855 | 0.791 | 29.944 | 625.114 |
| random | 0.788 | 0.710 | 31.908 | 656.132 |
| smallest | 0.652 | 0.451 | 12.861 | 263.968 |
| largest | 0.871 | 0.813 | 50.171 | 1029.025 |
| best_fixed | 0.796 | 0.711 | 17.510 | 411.602 |
| oracle | 0.975 | 0.956 | 12.073 | 247.624 |

## US-CAL-CISO

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.830 | 0.747 | 33.783 | 533.573 |
| carbon_pt_floor | 0.858 | 0.788 | 41.864 | 637.499 |
| random | 0.788 | 0.710 | 44.790 | 656.132 |
| smallest | 0.652 | 0.451 | 17.832 | 263.968 |
| largest | 0.871 | 0.813 | 69.453 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 38.519 | 569.385 |
| oracle | 0.975 | 0.956 | 16.669 | 247.624 |

## US-NE-ISNE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.823 | 0.732 | 44.403 | 477.828 |
| carbon_pt_floor | 0.846 | 0.778 | 56.589 | 607.469 |
| random | 0.788 | 0.710 | 61.015 | 656.132 |
| smallest | 0.652 | 0.451 | 24.534 | 263.968 |
| largest | 0.871 | 0.813 | 95.650 | 1029.025 |
| best_fixed | 0.796 | 0.711 | 37.597 | 411.602 |
| oracle | 0.975 | 0.956 | 23.012 | 247.624 |

## PL

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.748 | 0.655 | 45.594 | 315.736 |
| carbon_pt_floor | 0.838 | 0.781 | 84.918 | 578.059 |
| random | 0.788 | 0.710 | 95.564 | 656.132 |
| smallest | 0.652 | 0.451 | 38.561 | 263.968 |
| largest | 0.871 | 0.813 | 150.386 | 1029.025 |
| best_fixed | 0.703 | 0.648 | 25.566 | 174.927 |
| oracle | 0.974 | 0.954 | 35.267 | 242.663 |
