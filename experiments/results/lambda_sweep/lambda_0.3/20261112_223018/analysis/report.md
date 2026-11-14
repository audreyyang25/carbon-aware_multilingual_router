# Routing results: 20261112_223018

- Hardware: NVIDIA A100-SXM4-80GB; models: gemma-4-31b, gemma-4-e4b, qwen3.5-27b, qwen3.5-2b, qwen3.5-9b, tiny-aya-global
- Algorithm: linucb, lambda = 0.3, 5 runs, 250 queries/hour
- Zones: FR, SE-SE3, DE, US-CAL-CISO, US-NE-ISNE, PL

## Test phase, averaged over zones

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.828 | 0.764 | 31.528 | 514.133 |
| energy_pq | 0.857 | 0.776 | 64.885 | 1041.201 |
| carbon | 0.867 | 0.812 | 72.449 | 1212.760 |
| carbon_no_flesch | 0.867 | 0.814 | 67.935 | 1158.990 |
| carbon_en_emb | 0.861 | 0.807 | 57.190 | 1002.516 |
| carbon_onehot | 0.865 | 0.806 | 67.001 | 1117.207 |
| carbon_ml_emb | 0.862 | 0.809 | 55.272 | 922.085 |
| lang_carbon | 0.858 | 0.797 | 57.259 | 983.591 |
| random | 0.788 | 0.710 | 40.137 | 656.132 |
| smallest | 0.652 | 0.451 | 16.137 | 263.968 |
| largest | 0.871 | 0.813 | 62.913 | 1029.025 |
| best_fixed | 0.866 | 0.791 | 43.720 | 860.490 |
| oracle | 0.975 | 0.956 | 14.481 | 236.962 |

## Paired comparisons (all zones)

Router minus reference on the same queries. Accuracy in points, carbon in % of the reference. 95% bootstrap CI over test items; * = CI excludes 0.

| comparison | question | accuracy (pp) | carbon (%) |
|---|---|---|---|
| lang_carbon vs largest | Savings vs always using the largest model | -1.3 [-2.6, -0.1] * | -9.0% [-12.2, -6.0] * |
| lang_carbon vs best_fixed | vs the best single model in hindsight | -0.9 [-1.7, -0.0] * | +31.0% [+27.1, +34.9] * |
| lang_carbon vs greenserv | vs GreenServ (energy-per-token cost, English features) | +3.0 [+0.4, +5.7] * | +81.6% [+71.1, +93.8] * |
| lang_carbon vs carbon_no_flesch | Do language + multilingual embedding help? | -0.9 [-1.6, -0.2] * | -15.7% [-17.9, -13.7] * |
| lang_carbon vs carbon_onehot | Does the embedding add beyond the language label? | -0.8 [-1.4, -0.2] * | -14.5% [-16.7, -12.6] * |
| lang_carbon vs carbon_ml_emb | Does the language label add beyond the embedding? | -0.5 [-0.8, -0.1] * | +3.6% [+1.4, +5.8] * |
| carbon_ml_emb vs carbon_en_emb | Multilingual vs English encoder | +0.1 [-0.3, +0.5] | -3.4% [-5.7, -0.7] * |
| carbon vs energy_pq | Does seeing the grid help? (carbon vs energy cost) | +1.0 [+0.3, +1.8] * | +11.7% [+10.0, +13.5] * |
| carbon vs carbon_no_flesch | Does Flesch complexity help? | +0.1 [-0.4, +0.5] | +6.6% [+5.6, +7.6] * |
| carbon vs greenserv | Carbon cost vs GreenServ's energy-per-token cost | +4.0 [+1.4, +6.7] * | +129.8% [+114.8, +146.9] * |

## Test results by benchmark (all zones)

Pooled carbon above is a mean over all test queries, so it is almost entirely MGSM (an MGSM answer uses about 100x the energy of an XNLI or Belebele one). Here each benchmark is on its own; `% of largest` puts carbon on a common scale (always using the largest model = 100), and its benchmark average weights the three equally.

| strategy | acc belebele | acc mgsm | acc xnli | gCO2/1k belebele | gCO2/1k mgsm | gCO2/1k xnli | % of largest belebele | % of largest mgsm | % of largest xnli | % of largest, benchmarks averaged |
|---|---|---|---|---|---|---|---|---|---|---|
| greenserv | 0.915 | 0.873 | 0.721 | 2.695 | 168.959 | 1.723 | 62.934 | 49.567 | 58.428 | 56.977 |
| energy_pq | 0.906 | 0.911 | 0.786 | 2.238 | 358.859 | 2.103 | 52.256 | 105.278 | 71.288 | 76.274 |
| carbon | 0.933 | 0.923 | 0.778 | 3.591 | 398.458 | 2.209 | 83.865 | 116.895 | 74.894 | 91.885 |
| carbon_no_flesch | 0.939 | 0.928 | 0.769 | 3.787 | 371.593 | 2.523 | 88.433 | 109.014 | 85.547 | 94.331 |
| carbon_en_emb | 0.924 | 0.922 | 0.772 | 3.273 | 312.105 | 2.343 | 76.430 | 91.562 | 79.431 | 82.474 |
| carbon_onehot | 0.936 | 0.928 | 0.768 | 3.776 | 366.628 | 2.385 | 88.177 | 107.557 | 80.868 | 92.201 |
| carbon_ml_emb | 0.921 | 0.930 | 0.774 | 3.278 | 301.463 | 2.224 | 76.546 | 88.440 | 75.394 | 80.127 |
| lang_carbon | 0.915 | 0.919 | 0.774 | 3.265 | 312.848 | 2.200 | 76.257 | 91.780 | 74.601 | 80.880 |
| random | 0.860 | 0.825 | 0.700 | 2.437 | 218.092 | 1.908 | 56.918 | 63.982 | 64.697 | 61.865 |
| smallest | 0.730 | 0.609 | 0.593 | 0.951 | 87.642 | 0.813 | 22.211 | 25.712 | 27.565 | 25.162 |
| largest | 0.945 | 0.945 | 0.765 | 4.282 | 340.867 | 2.950 | 100.000 | 100.000 | 100.000 | 100.000 |
| best_fixed | 0.931 | 0.925 | 0.776 | 2.837 | 236.893 | 2.183 | 66.250 | 69.497 | 74.006 | 69.918 |
| oracle | 0.973 | 0.977 | 0.977 | 0.997 | 77.904 | 0.903 | 23.294 | 22.855 | 30.609 | 25.586 |

Share of each strategy's total carbon spent on each benchmark:

| strategy | share of carbon belebele | share of carbon mgsm | share of carbon xnli |
|---|---|---|---|
| greenserv | 0.037 | 0.941 | 0.023 |
| energy_pq | 0.017 | 0.968 | 0.015 |
| carbon | 0.022 | 0.965 | 0.013 |
| carbon_no_flesch | 0.025 | 0.958 | 0.017 |
| carbon_en_emb | 0.023 | 0.959 | 0.017 |
| carbon_onehot | 0.024 | 0.961 | 0.015 |
| carbon_ml_emb | 0.025 | 0.957 | 0.018 |
| lang_carbon | 0.024 | 0.959 | 0.017 |
| random | 0.025 | 0.955 | 0.020 |
| smallest | 0.024 | 0.955 | 0.021 |
| largest | 0.028 | 0.953 | 0.019 |
| best_fixed | 0.027 | 0.953 | 0.020 |
| oracle | 0.028 | 0.946 | 0.026 |

## Test accuracy by language (all zones)

| strategy | en | de | es | fr | ru | zh | th | sw | worst |
|---|---|---|---|---|---|---|---|---|---|
| greenserv | 0.890 | 0.834 | 0.863 | 0.838 | 0.833 | 0.802 | 0.781 | 0.779 | 0.779 |
| energy_pq | 0.927 | 0.855 | 0.902 | 0.882 | 0.848 | 0.844 | 0.824 | 0.776 | 0.776 |
| carbon | 0.938 | 0.861 | 0.903 | 0.888 | 0.847 | 0.850 | 0.837 | 0.815 | 0.815 |
| carbon_no_flesch | 0.938 | 0.867 | 0.905 | 0.885 | 0.836 | 0.852 | 0.831 | 0.821 | 0.821 |
| carbon_en_emb | 0.929 | 0.858 | 0.897 | 0.873 | 0.842 | 0.851 | 0.830 | 0.810 | 0.810 |
| carbon_onehot | 0.937 | 0.859 | 0.900 | 0.884 | 0.850 | 0.851 | 0.829 | 0.814 | 0.814 |
| carbon_ml_emb | 0.929 | 0.859 | 0.900 | 0.875 | 0.845 | 0.851 | 0.827 | 0.810 | 0.810 |
| lang_carbon | 0.929 | 0.859 | 0.894 | 0.871 | 0.839 | 0.845 | 0.824 | 0.800 | 0.800 |
| random | 0.854 | 0.816 | 0.792 | 0.811 | 0.785 | 0.776 | 0.758 | 0.710 | 0.710 |
| smallest | 0.753 | 0.687 | 0.659 | 0.703 | 0.670 | 0.659 | 0.637 | 0.451 | 0.451 |
| largest | 0.940 | 0.879 | 0.901 | 0.890 | 0.852 | 0.863 | 0.830 | 0.813 | 0.813 |
| best_fixed | 0.940 | 0.869 | 0.903 | 0.886 | 0.852 | 0.859 | 0.830 | 0.791 | 0.791 |
| oracle | 0.995 | 0.973 | 0.973 | 0.973 | 0.978 | 0.956 | 0.967 | 0.989 | 0.956 |

## FR

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.828 | 0.764 | 3.224 | 514.133 |
| energy_pq | 0.857 | 0.776 | 6.608 | 1041.201 |
| carbon | 0.862 | 0.816 | 7.546 | 1190.413 |
| carbon_no_flesch | 0.870 | 0.821 | 7.422 | 1172.678 |
| carbon_en_emb | 0.863 | 0.810 | 6.573 | 1041.074 |
| carbon_onehot | 0.872 | 0.802 | 6.942 | 1109.319 |
| carbon_ml_emb | 0.863 | 0.819 | 5.996 | 962.402 |
| lang_carbon | 0.856 | 0.793 | 6.462 | 1026.737 |
| random | 0.788 | 0.710 | 4.121 | 656.132 |
| smallest | 0.652 | 0.451 | 1.661 | 263.968 |
| largest | 0.871 | 0.813 | 6.474 | 1029.025 |
| best_fixed | 0.871 | 0.813 | 6.474 | 1029.025 |
| oracle | 0.975 | 0.956 | 1.488 | 236.962 |

## SE-SE3

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.828 | 0.764 | 2.634 | 514.133 |
| energy_pq | 0.857 | 0.776 | 5.235 | 1041.201 |
| carbon | 0.867 | 0.815 | 6.862 | 1300.475 |
| carbon_no_flesch | 0.870 | 0.822 | 6.128 | 1172.700 |
| carbon_en_emb | 0.860 | 0.814 | 5.594 | 1067.720 |
| carbon_onehot | 0.872 | 0.816 | 6.019 | 1161.343 |
| carbon_ml_emb | 0.863 | 0.810 | 4.639 | 897.679 |
| lang_carbon | 0.854 | 0.798 | 5.770 | 1100.054 |
| random | 0.788 | 0.710 | 3.423 | 656.132 |
| smallest | 0.652 | 0.451 | 1.370 | 263.968 |
| largest | 0.871 | 0.813 | 5.343 | 1029.025 |
| best_fixed | 0.871 | 0.813 | 5.343 | 1029.025 |
| oracle | 0.975 | 0.956 | 1.231 | 236.962 |

## DE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.828 | 0.764 | 25.118 | 514.133 |
| energy_pq | 0.857 | 0.776 | 53.023 | 1041.201 |
| carbon | 0.873 | 0.821 | 55.951 | 1132.949 |
| carbon_no_flesch | 0.853 | 0.803 | 59.230 | 1240.966 |
| carbon_en_emb | 0.863 | 0.815 | 52.966 | 1089.850 |
| carbon_onehot | 0.867 | 0.815 | 51.878 | 1119.630 |
| carbon_ml_emb | 0.865 | 0.816 | 42.045 | 884.678 |
| lang_carbon | 0.862 | 0.801 | 48.381 | 979.914 |
| random | 0.788 | 0.710 | 31.908 | 656.132 |
| smallest | 0.652 | 0.451 | 12.861 | 263.968 |
| largest | 0.871 | 0.813 | 50.171 | 1029.025 |
| best_fixed | 0.866 | 0.789 | 38.283 | 845.169 |
| oracle | 0.975 | 0.956 | 11.549 | 236.962 |

## US-CAL-CISO

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.828 | 0.764 | 34.452 | 514.133 |
| energy_pq | 0.857 | 0.776 | 68.607 | 1041.201 |
| carbon | 0.866 | 0.810 | 85.053 | 1273.271 |
| carbon_no_flesch | 0.867 | 0.821 | 83.839 | 1233.593 |
| carbon_en_emb | 0.868 | 0.813 | 72.994 | 1070.108 |
| carbon_onehot | 0.869 | 0.816 | 76.317 | 1131.035 |
| carbon_ml_emb | 0.871 | 0.811 | 68.697 | 1010.313 |
| lang_carbon | 0.860 | 0.804 | 64.786 | 966.320 |
| random | 0.788 | 0.710 | 44.790 | 656.132 |
| smallest | 0.652 | 0.451 | 17.832 | 263.968 |
| largest | 0.871 | 0.813 | 69.453 | 1029.025 |
| best_fixed | 0.871 | 0.813 | 69.453 | 1029.025 |
| oracle | 0.975 | 0.956 | 15.957 | 236.962 |

## US-NE-ISNE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.828 | 0.764 | 47.903 | 514.133 |
| energy_pq | 0.857 | 0.776 | 94.763 | 1041.201 |
| carbon | 0.872 | 0.812 | 111.859 | 1194.574 |
| carbon_no_flesch | 0.874 | 0.813 | 99.265 | 1058.097 |
| carbon_en_emb | 0.858 | 0.803 | 91.628 | 1000.395 |
| carbon_onehot | 0.865 | 0.809 | 99.409 | 1067.896 |
| carbon_ml_emb | 0.856 | 0.805 | 81.667 | 885.241 |
| lang_carbon | 0.862 | 0.798 | 79.647 | 862.210 |
| random | 0.788 | 0.710 | 61.015 | 656.132 |
| smallest | 0.652 | 0.451 | 24.534 | 263.968 |
| largest | 0.871 | 0.813 | 95.650 | 1029.025 |
| best_fixed | 0.860 | 0.765 | 59.574 | 661.313 |
| oracle | 0.975 | 0.956 | 22.022 | 236.962 |

## PL

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.828 | 0.764 | 75.836 | 514.133 |
| energy_pq | 0.857 | 0.776 | 161.073 | 1041.201 |
| carbon | 0.864 | 0.797 | 167.421 | 1184.879 |
| carbon_no_flesch | 0.867 | 0.801 | 151.727 | 1075.908 |
| carbon_en_emb | 0.856 | 0.784 | 113.383 | 745.946 |
| carbon_onehot | 0.846 | 0.776 | 161.440 | 1114.020 |
| carbon_ml_emb | 0.856 | 0.791 | 128.586 | 892.199 |
| lang_carbon | 0.850 | 0.790 | 138.505 | 966.311 |
| random | 0.788 | 0.710 | 95.564 | 656.132 |
| smallest | 0.652 | 0.451 | 38.561 | 263.968 |
| largest | 0.871 | 0.813 | 150.386 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 83.193 | 569.385 |
| oracle | 0.975 | 0.956 | 34.636 | 236.962 |
