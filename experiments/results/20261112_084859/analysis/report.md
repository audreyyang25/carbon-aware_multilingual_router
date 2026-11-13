# Routing results: 20261112_084859

- Hardware: NVIDIA A100-SXM4-80GB; models: gemma-4-31b, gemma-4-e4b, qwen3.5-27b, qwen3.5-2b, qwen3.5-9b, tiny-aya-global
- Algorithm: linucb, lambda = 0.5, 5 runs, 250 queries/hour
- Zones: FR, SE-SE3, DE, US-CAL-CISO, US-NE-ISNE, PL

## Test phase, averaged over zones

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.757 | 0.691 | 18.415 | 302.742 |
| energy_pq | 0.815 | 0.736 | 46.730 | 774.426 |
| carbon | 0.844 | 0.777 | 51.807 | 1042.760 |
| carbon_no_flesch | 0.866 | 0.806 | 60.669 | 1047.606 |
| carbon_en_emb | 0.857 | 0.799 | 50.099 | 909.969 |
| carbon_onehot | 0.855 | 0.790 | 53.950 | 928.335 |
| carbon_ml_emb | 0.852 | 0.796 | 55.389 | 972.768 |
| lang_carbon | 0.858 | 0.803 | 52.751 | 944.266 |
| random | 0.788 | 0.710 | 40.137 | 656.132 |
| smallest | 0.652 | 0.451 | 16.137 | 263.968 |
| largest | 0.871 | 0.813 | 62.913 | 1029.025 |
| best_fixed | 0.862 | 0.773 | 35.701 | 722.598 |
| oracle | 0.975 | 0.956 | 14.481 | 236.962 |

## Paired comparisons (all zones)

Router minus reference on the same queries. Accuracy in points, carbon in % of the reference. 95% bootstrap CI over test items; * = CI excludes 0.

| comparison | question | accuracy (pp) | carbon (%) |
|---|---|---|---|
| lang_carbon vs largest | Savings vs always using the largest model | -1.2 [-2.4, +0.0] | -16.2% [-18.9, -13.7] * |
| lang_carbon vs best_fixed | vs the best single model in hindsight | -0.4 [-1.1, +0.3] | +47.8% [+41.8, +53.9] * |
| lang_carbon vs greenserv | vs GreenServ (energy-per-token cost, English features) | +10.1 [+6.3, +14.2] * | +186.5% [+170.4, +204.2] * |
| lang_carbon vs carbon_no_flesch | Do language + multilingual embedding help? | -0.8 [-1.3, -0.3] * | -13.1% [-15.3, -11.0] * |
| lang_carbon vs carbon_onehot | Does the embedding add beyond the language label? | +0.3 [-0.1, +0.8] | -2.2% [-4.7, +0.2] |
| lang_carbon vs carbon_ml_emb | Does the language label add beyond the embedding? | +0.6 [+0.2, +1.0] * | -4.8% [-6.7, -2.6] * |
| carbon_ml_emb vs carbon_en_emb | Multilingual vs English encoder | -0.4 [-0.9, +0.0] | +10.6% [+6.5, +14.7] * |
| carbon vs energy_pq | Does seeing the grid help? (carbon vs energy cost) | +2.9 [+1.6, +4.3] * | +10.9% [+8.0, +13.7] * |
| carbon vs carbon_no_flesch | Does Flesch complexity help? | -2.2 [-2.9, -1.4] * | -14.6% [-16.0, -13.2] * |
| carbon vs greenserv | Carbon cost vs GreenServ's energy-per-token cost | +8.7 [+4.8, +13.1] * | +181.3% [+164.9, +197.8] * |

## Test results by benchmark (all zones)

Pooled carbon above is a mean over all test queries, so it is almost entirely MGSM (an MGSM answer uses about 100x the energy of an XNLI or Belebele one). Here each benchmark is on its own; `% of largest` puts carbon on a common scale (always using the largest model = 100), and its benchmark average weights the three equally.

| strategy | acc belebele | acc mgsm | acc xnli | gCO2/1k belebele | gCO2/1k mgsm | gCO2/1k xnli | % of largest belebele | % of largest mgsm | % of largest xnli | % of largest, benchmarks averaged |
|---|---|---|---|---|---|---|---|---|---|---|
| greenserv | 0.822 | 0.757 | 0.693 | 1.621 | 97.103 | 1.635 | 37.851 | 28.487 | 55.421 | 40.586 |
| energy_pq | 0.889 | 0.935 | 0.690 | 1.895 | 258.167 | 1.351 | 44.255 | 75.738 | 45.800 | 55.264 |
| carbon | 0.919 | 0.919 | 0.738 | 2.720 | 283.994 | 1.827 | 63.514 | 83.315 | 61.938 | 69.589 |
| carbon_no_flesch | 0.932 | 0.935 | 0.771 | 3.115 | 332.248 | 2.348 | 72.743 | 97.471 | 79.613 | 83.276 |
| carbon_en_emb | 0.918 | 0.924 | 0.767 | 2.753 | 274.052 | 1.892 | 64.281 | 80.398 | 64.145 | 69.608 |
| carbon_onehot | 0.924 | 0.923 | 0.757 | 2.789 | 295.841 | 1.905 | 65.127 | 86.791 | 64.593 | 72.170 |
| carbon_ml_emb | 0.914 | 0.926 | 0.760 | 2.877 | 303.936 | 1.855 | 67.195 | 89.165 | 62.893 | 73.085 |
| lang_carbon | 0.917 | 0.920 | 0.774 | 2.990 | 288.439 | 1.952 | 69.824 | 84.619 | 66.181 | 73.541 |
| random | 0.860 | 0.825 | 0.700 | 2.437 | 218.092 | 1.908 | 56.918 | 63.982 | 64.697 | 61.865 |
| smallest | 0.730 | 0.609 | 0.593 | 0.951 | 87.642 | 0.813 | 22.211 | 25.712 | 27.565 | 25.162 |
| largest | 0.945 | 0.945 | 0.765 | 4.282 | 340.867 | 2.950 | 100.000 | 100.000 | 100.000 | 100.000 |
| best_fixed | 0.919 | 0.909 | 0.785 | 2.237 | 193.439 | 1.863 | 52.244 | 56.749 | 63.165 | 57.386 |
| oracle | 0.973 | 0.977 | 0.977 | 0.997 | 77.904 | 0.903 | 23.294 | 22.855 | 30.609 | 25.586 |

Share of each strategy's total carbon spent on each benchmark:

| strategy | share of carbon belebele | share of carbon mgsm | share of carbon xnli |
|---|---|---|---|
| greenserv | 0.045 | 0.911 | 0.044 |
| energy_pq | 0.018 | 0.968 | 0.013 |
| carbon | 0.022 | 0.964 | 0.014 |
| carbon_no_flesch | 0.025 | 0.958 | 0.017 |
| carbon_en_emb | 0.023 | 0.960 | 0.016 |
| carbon_onehot | 0.024 | 0.960 | 0.016 |
| carbon_ml_emb | 0.022 | 0.962 | 0.015 |
| lang_carbon | 0.023 | 0.961 | 0.016 |
| random | 0.025 | 0.955 | 0.020 |
| smallest | 0.024 | 0.955 | 0.021 |
| largest | 0.028 | 0.953 | 0.019 |
| best_fixed | 0.026 | 0.953 | 0.021 |
| oracle | 0.028 | 0.946 | 0.026 |

## Test accuracy by language (all zones)

| strategy | en | de | es | fr | ru | zh | th | sw | worst |
|---|---|---|---|---|---|---|---|---|---|
| greenserv | 0.827 | 0.770 | 0.775 | 0.781 | 0.757 | 0.726 | 0.707 | 0.715 | 0.707 |
| energy_pq | 0.873 | 0.820 | 0.851 | 0.830 | 0.822 | 0.797 | 0.795 | 0.736 | 0.736 |
| carbon | 0.908 | 0.844 | 0.878 | 0.860 | 0.842 | 0.829 | 0.814 | 0.780 | 0.780 |
| carbon_no_flesch | 0.937 | 0.867 | 0.903 | 0.887 | 0.844 | 0.853 | 0.832 | 0.809 | 0.809 |
| carbon_en_emb | 0.920 | 0.854 | 0.895 | 0.870 | 0.838 | 0.847 | 0.828 | 0.803 | 0.803 |
| carbon_onehot | 0.927 | 0.844 | 0.898 | 0.865 | 0.842 | 0.847 | 0.814 | 0.804 | 0.804 |
| carbon_ml_emb | 0.924 | 0.844 | 0.887 | 0.870 | 0.836 | 0.838 | 0.821 | 0.800 | 0.800 |
| lang_carbon | 0.934 | 0.853 | 0.892 | 0.871 | 0.843 | 0.846 | 0.823 | 0.805 | 0.805 |
| random | 0.854 | 0.816 | 0.792 | 0.811 | 0.785 | 0.776 | 0.758 | 0.710 | 0.710 |
| smallest | 0.753 | 0.687 | 0.659 | 0.703 | 0.670 | 0.659 | 0.637 | 0.451 | 0.451 |
| largest | 0.940 | 0.879 | 0.901 | 0.890 | 0.852 | 0.863 | 0.830 | 0.813 | 0.813 |
| best_fixed | 0.940 | 0.861 | 0.905 | 0.883 | 0.852 | 0.855 | 0.830 | 0.773 | 0.773 |
| oracle | 0.995 | 0.973 | 0.973 | 0.973 | 0.978 | 0.956 | 0.967 | 0.989 | 0.956 |

## FR

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.757 | 0.691 | 1.963 | 302.742 |
| energy_pq | 0.815 | 0.736 | 4.794 | 774.426 |
| carbon | 0.856 | 0.801 | 7.704 | 1234.835 |
| carbon_no_flesch | 0.872 | 0.818 | 6.853 | 1093.322 |
| carbon_en_emb | 0.865 | 0.812 | 6.661 | 1051.412 |
| carbon_onehot | 0.861 | 0.795 | 6.279 | 994.920 |
| carbon_ml_emb | 0.863 | 0.805 | 6.825 | 1090.330 |
| lang_carbon | 0.861 | 0.805 | 6.597 | 1049.581 |
| random | 0.788 | 0.710 | 4.121 | 656.132 |
| smallest | 0.652 | 0.451 | 1.661 | 263.968 |
| largest | 0.871 | 0.813 | 6.474 | 1029.025 |
| best_fixed | 0.871 | 0.813 | 6.474 | 1029.025 |
| oracle | 0.975 | 0.956 | 1.488 | 236.962 |

## SE-SE3

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.757 | 0.691 | 1.607 | 302.742 |
| energy_pq | 0.815 | 0.736 | 4.010 | 774.426 |
| carbon | 0.866 | 0.814 | 7.021 | 1350.885 |
| carbon_no_flesch | 0.873 | 0.818 | 5.747 | 1097.419 |
| carbon_en_emb | 0.864 | 0.819 | 5.494 | 1045.388 |
| carbon_onehot | 0.862 | 0.795 | 5.421 | 1018.752 |
| carbon_ml_emb | 0.858 | 0.804 | 5.619 | 1071.974 |
| lang_carbon | 0.861 | 0.809 | 5.232 | 1005.513 |
| random | 0.788 | 0.710 | 3.423 | 656.132 |
| smallest | 0.652 | 0.451 | 1.370 | 263.968 |
| largest | 0.871 | 0.813 | 5.343 | 1029.025 |
| best_fixed | 0.871 | 0.813 | 5.343 | 1029.025 |
| oracle | 0.975 | 0.956 | 1.231 | 236.962 |

## DE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.757 | 0.691 | 15.707 | 302.742 |
| energy_pq | 0.815 | 0.736 | 36.035 | 774.426 |
| carbon | 0.854 | 0.788 | 54.186 | 1127.700 |
| carbon_no_flesch | 0.872 | 0.810 | 48.495 | 1004.586 |
| carbon_en_emb | 0.861 | 0.805 | 43.945 | 878.513 |
| carbon_onehot | 0.864 | 0.808 | 50.120 | 1023.612 |
| carbon_ml_emb | 0.861 | 0.812 | 44.480 | 975.008 |
| lang_carbon | 0.861 | 0.810 | 47.447 | 988.413 |
| random | 0.788 | 0.710 | 31.908 | 656.132 |
| smallest | 0.652 | 0.451 | 12.861 | 263.968 |
| largest | 0.871 | 0.813 | 50.171 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 27.762 | 569.385 |
| oracle | 0.975 | 0.956 | 11.549 | 236.962 |

## US-CAL-CISO

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.757 | 0.691 | 20.376 | 302.742 |
| energy_pq | 0.815 | 0.736 | 51.177 | 774.426 |
| carbon | 0.845 | 0.770 | 56.619 | 908.269 |
| carbon_no_flesch | 0.868 | 0.816 | 77.686 | 1182.123 |
| carbon_en_emb | 0.862 | 0.800 | 52.923 | 833.608 |
| carbon_onehot | 0.863 | 0.804 | 59.203 | 854.318 |
| carbon_ml_emb | 0.861 | 0.797 | 68.122 | 989.859 |
| lang_carbon | 0.868 | 0.809 | 63.130 | 944.935 |
| random | 0.788 | 0.710 | 44.790 | 656.132 |
| smallest | 0.652 | 0.451 | 17.832 | 263.968 |
| largest | 0.871 | 0.813 | 69.453 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 38.519 | 569.385 |
| oracle | 0.975 | 0.956 | 15.957 | 236.962 |

## US-NE-ISNE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.757 | 0.691 | 27.564 | 302.742 |
| energy_pq | 0.815 | 0.736 | 73.790 | 774.426 |
| carbon | 0.826 | 0.754 | 85.012 | 914.766 |
| carbon_no_flesch | 0.872 | 0.814 | 91.939 | 1007.063 |
| carbon_en_emb | 0.862 | 0.796 | 87.285 | 948.066 |
| carbon_onehot | 0.858 | 0.784 | 78.538 | 840.338 |
| carbon_ml_emb | 0.842 | 0.786 | 78.929 | 846.243 |
| lang_carbon | 0.857 | 0.810 | 86.168 | 926.897 |
| random | 0.788 | 0.710 | 61.015 | 656.132 |
| smallest | 0.652 | 0.451 | 24.534 | 263.968 |
| largest | 0.871 | 0.813 | 95.650 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 52.914 | 569.385 |
| oracle | 0.975 | 0.956 | 22.022 | 236.962 |

## PL

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.757 | 0.691 | 43.271 | 302.742 |
| energy_pq | 0.815 | 0.736 | 110.572 | 774.426 |
| carbon | 0.821 | 0.732 | 100.298 | 720.107 |
| carbon_no_flesch | 0.841 | 0.758 | 133.290 | 901.125 |
| carbon_en_emb | 0.828 | 0.759 | 104.287 | 702.829 |
| carbon_onehot | 0.822 | 0.754 | 124.140 | 838.068 |
| carbon_ml_emb | 0.830 | 0.770 | 128.361 | 863.193 |
| lang_carbon | 0.842 | 0.776 | 107.933 | 750.261 |
| random | 0.788 | 0.710 | 95.564 | 656.132 |
| smallest | 0.652 | 0.451 | 38.561 | 263.968 |
| largest | 0.871 | 0.813 | 150.386 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 83.193 | 569.385 |
| oracle | 0.975 | 0.956 | 34.636 | 236.962 |
