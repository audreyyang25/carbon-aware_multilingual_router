# Routing results: 20261115_135114

- Hardware: NVIDIA A100-SXM4-80GB; models: gemma-4-31b, gemma-4-e4b, qwen3.5-27b, qwen3.5-2b, qwen3.5-9b, tiny-aya-global
- Algorithm: linucb, lambda = 0.5, 5 runs, 250 queries/hour
- Zones: FR, SE-SE3, DE, US-CAL-CISO, US-NE-ISNE, PL

## Test phase, averaged over zones

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt | 0.851 | 0.792 | 39.688 | 881.009 |
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
| carbon_pt | 0.923 | 0.908 | 0.754 | 3.182 | 213.413 | 2.071 | 74.315 | 62.609 | 70.210 | 69.044 |
| random | 0.860 | 0.825 | 0.700 | 2.437 | 218.092 | 1.908 | 56.918 | 63.982 | 64.697 | 61.865 |
| smallest | 0.730 | 0.609 | 0.593 | 0.951 | 87.642 | 0.813 | 22.211 | 25.712 | 27.565 | 25.162 |
| largest | 0.945 | 0.945 | 0.765 | 4.282 | 340.867 | 2.950 | 100.000 | 100.000 | 100.000 | 100.000 |
| best_fixed | 0.919 | 0.909 | 0.785 | 2.237 | 193.439 | 1.863 | 52.244 | 56.749 | 63.165 | 57.386 |
| oracle | 0.973 | 0.977 | 0.977 | 1.292 | 79.766 | 1.396 | 30.183 | 23.401 | 47.332 | 33.638 |

Share of each strategy's total carbon spent on each benchmark:

| strategy | share of carbon belebele | share of carbon mgsm | share of carbon xnli |
|---|---|---|---|
| carbon_pt | 0.031 | 0.948 | 0.020 |
| random | 0.025 | 0.955 | 0.020 |
| smallest | 0.024 | 0.955 | 0.021 |
| largest | 0.028 | 0.953 | 0.019 |
| best_fixed | 0.026 | 0.953 | 0.021 |
| oracle | 0.035 | 0.927 | 0.038 |

## Test accuracy by language (all zones)

| strategy | en | de | es | fr | ru | zh | th | sw | worst |
|---|---|---|---|---|---|---|---|---|---|
| carbon_pt | 0.919 | 0.852 | 0.882 | 0.867 | 0.841 | 0.834 | 0.812 | 0.799 | 0.799 |
| random | 0.854 | 0.816 | 0.792 | 0.811 | 0.785 | 0.776 | 0.758 | 0.710 | 0.710 |
| smallest | 0.753 | 0.687 | 0.659 | 0.703 | 0.670 | 0.659 | 0.637 | 0.451 | 0.451 |
| largest | 0.940 | 0.879 | 0.901 | 0.890 | 0.852 | 0.863 | 0.830 | 0.813 | 0.813 |
| best_fixed | 0.940 | 0.861 | 0.905 | 0.883 | 0.852 | 0.855 | 0.830 | 0.773 | 0.773 |
| oracle | 0.995 | 0.973 | 0.973 | 0.973 | 0.978 | 0.956 | 0.967 | 0.989 | 0.956 |

## FR

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt | 0.870 | 0.815 | 7.361 | 1179.201 |
| random | 0.788 | 0.710 | 4.121 | 656.132 |
| smallest | 0.652 | 0.451 | 1.661 | 263.968 |
| largest | 0.871 | 0.813 | 6.474 | 1029.025 |
| best_fixed | 0.871 | 0.813 | 6.474 | 1029.025 |
| oracle | 0.975 | 0.956 | 1.556 | 247.624 |

## SE-SE3

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt | 0.869 | 0.821 | 6.526 | 1233.044 |
| random | 0.788 | 0.710 | 3.423 | 656.132 |
| smallest | 0.652 | 0.451 | 1.370 | 263.968 |
| largest | 0.871 | 0.813 | 5.343 | 1029.025 |
| best_fixed | 0.871 | 0.813 | 5.343 | 1029.025 |
| oracle | 0.975 | 0.956 | 1.286 | 247.624 |

## DE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt | 0.852 | 0.797 | 42.533 | 960.989 |
| random | 0.788 | 0.710 | 31.908 | 656.132 |
| smallest | 0.652 | 0.451 | 12.861 | 263.968 |
| largest | 0.871 | 0.813 | 50.171 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 27.762 | 569.385 |
| oracle | 0.975 | 0.956 | 12.073 | 247.624 |

## US-CAL-CISO

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt | 0.858 | 0.799 | 62.592 | 893.225 |
| random | 0.788 | 0.710 | 44.790 | 656.132 |
| smallest | 0.652 | 0.451 | 17.832 | 263.968 |
| largest | 0.871 | 0.813 | 69.453 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 38.519 | 569.385 |
| oracle | 0.975 | 0.956 | 16.669 | 247.624 |

## US-NE-ISNE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt | 0.857 | 0.796 | 53.609 | 575.528 |
| random | 0.788 | 0.710 | 61.015 | 656.132 |
| smallest | 0.652 | 0.451 | 24.534 | 263.968 |
| largest | 0.871 | 0.813 | 95.650 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 52.914 | 569.385 |
| oracle | 0.975 | 0.956 | 23.012 | 247.624 |

## PL

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt | 0.799 | 0.722 | 65.506 | 444.064 |
| random | 0.788 | 0.710 | 95.564 | 656.132 |
| smallest | 0.652 | 0.451 | 38.561 | 263.968 |
| largest | 0.871 | 0.813 | 150.386 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 83.193 | 569.385 |
| oracle | 0.975 | 0.956 | 36.201 | 247.624 |
