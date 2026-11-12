# Routing results: 20261112_102950

- Hardware: NVIDIA A100-SXM4-80GB; models: gemma-4-31b, gemma-4-e4b, qwen3.5-27b, qwen3.5-2b, qwen3.5-9b, tiny-aya-global
- Algorithm: linucb, lambda = 0.5, 5 runs, 250 queries/hour
- Zones: FR, SE-SE3, DE, US-CAL-CISO, US-NE-ISNE, PL

## Test phase, averaged over zones

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.757 | 0.691 | 18.445 | 303.243 |
| energy_pq | 0.815 | 0.736 | 46.760 | 774.927 |
| carbon | 0.844 | 0.777 | 51.837 | 1043.261 |
| carbon_no_flesch | 0.866 | 0.806 | 60.699 | 1048.107 |
| carbon_en_emb | 0.857 | 0.799 | 50.130 | 910.470 |
| carbon_onehot | 0.855 | 0.790 | 53.981 | 928.836 |
| carbon_ml_emb | 0.852 | 0.796 | 55.440 | 973.593 |
| lang_carbon | 0.858 | 0.803 | 52.802 | 945.092 |
| random | 0.788 | 0.710 | 40.137 | 656.132 |
| smallest | 0.652 | 0.451 | 16.137 | 263.968 |
| largest | 0.871 | 0.813 | 62.913 | 1029.025 |
| best_fixed | 0.862 | 0.773 | 35.701 | 722.598 |
| oracle | 0.975 | 0.956 | 14.481 | 236.962 |

## Paired comparisons (all zones)

Router minus reference on the same queries. Accuracy in points, carbon in % of the reference. 95% bootstrap CI over test items; * = CI excludes 0.

| comparison | question | accuracy (pp) | carbon (%) |
|---|---|---|---|
| lang_carbon vs largest | Savings vs always using the largest model | -1.2 [-2.4, +0.0] | -16.1% [-18.8, -13.6] * |
| lang_carbon vs best_fixed | vs the best single model in hindsight | -0.4 [-1.1, +0.3] | +47.9% [+42.0, +54.0] * |
| lang_carbon vs greenserv | vs GreenServ (energy-per-token cost, English features) | +10.1 [+6.3, +14.2] * | +186.3% [+170.2, +203.9] * |
| lang_carbon vs carbon_no_flesch | Do language + multilingual embedding help? | -0.8 [-1.3, -0.3] * | -13.0% [-15.2, -10.9] * |
| lang_carbon vs carbon_onehot | Does the embedding add beyond the language label? | +0.3 [-0.1, +0.8] | -2.2% [-4.6, +0.2] |
| lang_carbon vs carbon_ml_emb | Does the language label add beyond the embedding? | +0.6 [+0.2, +1.0] * | -4.8% [-6.7, -2.6] * |
| carbon_ml_emb vs carbon_en_emb | Multilingual vs English encoder | -0.4 [-0.9, +0.0] | +10.6% [+6.5, +14.7] * |
| carbon vs energy_pq | Does seeing the grid help? (carbon vs energy cost) | +2.9 [+1.6, +4.3] * | +10.9% [+8.0, +13.7] * |
| carbon vs carbon_no_flesch | Does Flesch complexity help? | -2.2 [-2.9, -1.4] * | -14.6% [-16.0, -13.2] * |
| carbon vs greenserv | Carbon cost vs GreenServ's energy-per-token cost | +8.7 [+4.8, +13.1] * | +181.0% [+164.6, +197.5] * |

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
| greenserv | 0.757 | 0.691 | 1.966 | 303.243 |
| energy_pq | 0.815 | 0.736 | 4.797 | 774.927 |
| carbon | 0.856 | 0.801 | 7.707 | 1235.336 |
| carbon_no_flesch | 0.872 | 0.818 | 6.857 | 1093.823 |
| carbon_en_emb | 0.865 | 0.812 | 6.664 | 1051.913 |
| carbon_onehot | 0.861 | 0.795 | 6.282 | 995.421 |
| carbon_ml_emb | 0.863 | 0.805 | 6.830 | 1091.156 |
| lang_carbon | 0.861 | 0.805 | 6.602 | 1050.406 |
| random | 0.788 | 0.710 | 4.121 | 656.132 |
| smallest | 0.652 | 0.451 | 1.661 | 263.968 |
| largest | 0.871 | 0.813 | 6.474 | 1029.025 |
| best_fixed | 0.871 | 0.813 | 6.474 | 1029.025 |
| oracle | 0.975 | 0.956 | 1.488 | 236.962 |

## SE-SE3

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.757 | 0.691 | 1.609 | 303.243 |
| energy_pq | 0.815 | 0.736 | 4.012 | 774.927 |
| carbon | 0.866 | 0.814 | 7.024 | 1351.386 |
| carbon_no_flesch | 0.873 | 0.818 | 5.749 | 1097.920 |
| carbon_en_emb | 0.864 | 0.819 | 5.496 | 1045.889 |
| carbon_onehot | 0.862 | 0.795 | 5.424 | 1019.253 |
| carbon_ml_emb | 0.858 | 0.804 | 5.623 | 1072.799 |
| lang_carbon | 0.861 | 0.809 | 5.236 | 1006.338 |
| random | 0.788 | 0.710 | 3.423 | 656.132 |
| smallest | 0.652 | 0.451 | 1.370 | 263.968 |
| largest | 0.871 | 0.813 | 5.343 | 1029.025 |
| best_fixed | 0.871 | 0.813 | 5.343 | 1029.025 |
| oracle | 0.975 | 0.956 | 1.231 | 236.962 |

## DE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.757 | 0.691 | 15.731 | 303.243 |
| energy_pq | 0.815 | 0.736 | 36.060 | 774.927 |
| carbon | 0.854 | 0.788 | 54.211 | 1128.201 |
| carbon_no_flesch | 0.872 | 0.810 | 48.520 | 1005.087 |
| carbon_en_emb | 0.861 | 0.805 | 43.970 | 879.014 |
| carbon_onehot | 0.864 | 0.808 | 50.145 | 1024.113 |
| carbon_ml_emb | 0.861 | 0.812 | 44.521 | 975.834 |
| lang_carbon | 0.861 | 0.810 | 47.488 | 989.238 |
| random | 0.788 | 0.710 | 31.908 | 656.132 |
| smallest | 0.652 | 0.451 | 12.861 | 263.968 |
| largest | 0.871 | 0.813 | 50.171 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 27.762 | 569.385 |
| oracle | 0.975 | 0.956 | 11.549 | 236.962 |

## US-CAL-CISO

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.757 | 0.691 | 20.410 | 303.243 |
| energy_pq | 0.815 | 0.736 | 51.210 | 774.927 |
| carbon | 0.845 | 0.770 | 56.653 | 908.770 |
| carbon_no_flesch | 0.868 | 0.816 | 77.720 | 1182.624 |
| carbon_en_emb | 0.862 | 0.800 | 52.956 | 834.109 |
| carbon_onehot | 0.863 | 0.804 | 59.236 | 854.819 |
| carbon_ml_emb | 0.861 | 0.797 | 68.177 | 990.685 |
| lang_carbon | 0.868 | 0.809 | 63.185 | 945.760 |
| random | 0.788 | 0.710 | 44.790 | 656.132 |
| smallest | 0.652 | 0.451 | 17.832 | 263.968 |
| largest | 0.871 | 0.813 | 69.453 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 38.519 | 569.385 |
| oracle | 0.975 | 0.956 | 15.957 | 236.962 |

## US-NE-ISNE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.757 | 0.691 | 27.610 | 303.243 |
| energy_pq | 0.815 | 0.736 | 73.837 | 774.927 |
| carbon | 0.826 | 0.754 | 85.058 | 915.267 |
| carbon_no_flesch | 0.872 | 0.814 | 91.986 | 1007.564 |
| carbon_en_emb | 0.862 | 0.796 | 87.331 | 948.567 |
| carbon_onehot | 0.858 | 0.784 | 78.585 | 840.839 |
| carbon_ml_emb | 0.842 | 0.786 | 79.006 | 847.069 |
| lang_carbon | 0.857 | 0.810 | 86.244 | 927.722 |
| random | 0.788 | 0.710 | 61.015 | 656.132 |
| smallest | 0.652 | 0.451 | 24.534 | 263.968 |
| largest | 0.871 | 0.813 | 95.650 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 52.914 | 569.385 |
| oracle | 0.975 | 0.956 | 22.022 | 236.962 |

## PL

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.757 | 0.691 | 43.344 | 303.243 |
| energy_pq | 0.815 | 0.736 | 110.646 | 774.927 |
| carbon | 0.821 | 0.732 | 100.372 | 720.608 |
| carbon_no_flesch | 0.841 | 0.758 | 133.364 | 901.626 |
| carbon_en_emb | 0.828 | 0.759 | 104.361 | 703.330 |
| carbon_onehot | 0.822 | 0.754 | 124.214 | 838.569 |
| carbon_ml_emb | 0.830 | 0.770 | 128.483 | 864.018 |
| lang_carbon | 0.842 | 0.776 | 108.054 | 751.086 |
| random | 0.788 | 0.710 | 95.564 | 656.132 |
| smallest | 0.652 | 0.451 | 38.561 | 263.968 |
| largest | 0.871 | 0.813 | 150.386 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 83.193 | 569.385 |
| oracle | 0.975 | 0.956 | 34.636 | 236.962 |
