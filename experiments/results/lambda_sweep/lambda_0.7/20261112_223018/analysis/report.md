# Routing results: 20261112_223018

- Hardware: NVIDIA A100-SXM4-80GB; models: gemma-4-31b, gemma-4-e4b, qwen3.5-27b, qwen3.5-2b, qwen3.5-9b, tiny-aya-global
- Algorithm: linucb, lambda = 0.7, 5 runs, 250 queries/hour
- Zones: FR, SE-SE3, DE, US-CAL-CISO, US-NE-ISNE, PL

## Test phase, averaged over zones

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.721 | 0.662 | 11.049 | 180.458 |
| energy_pq | 0.744 | 0.679 | 28.866 | 468.445 |
| carbon | 0.823 | 0.758 | 40.060 | 844.536 |
| carbon_no_flesch | 0.816 | 0.752 | 41.797 | 819.045 |
| carbon_en_emb | 0.829 | 0.757 | 36.951 | 783.906 |
| carbon_onehot | 0.831 | 0.755 | 38.235 | 781.379 |
| carbon_ml_emb | 0.834 | 0.773 | 38.118 | 808.050 |
| lang_carbon | 0.826 | 0.762 | 37.386 | 792.239 |
| random | 0.788 | 0.710 | 40.137 | 656.132 |
| smallest | 0.652 | 0.451 | 16.137 | 263.968 |
| largest | 0.871 | 0.813 | 62.913 | 1029.025 |
| best_fixed | 0.829 | 0.755 | 30.890 | 680.271 |
| oracle | 0.975 | 0.956 | 14.481 | 236.962 |

## Paired comparisons (all zones)

Router minus reference on the same queries. Accuracy in points, carbon in % of the reference. 95% bootstrap CI over test items; * = CI excludes 0.

| comparison | question | accuracy (pp) | carbon (%) |
|---|---|---|---|
| lang_carbon vs largest | Savings vs always using the largest model | -4.5 [-6.4, -2.6] * | -40.6% [-43.6, -38.0] * |
| lang_carbon vs best_fixed | vs the best single model in hindsight | -0.3 [-1.1, +0.5] | +21.0% [+16.2, +25.9] * |
| lang_carbon vs greenserv | vs GreenServ (energy-per-token cost, English features) | +10.5 [+5.9, +15.7] * | +238.4% [+204.4, +268.8] * |
| lang_carbon vs carbon_no_flesch | Do language + multilingual embedding help? | +1.0 [-0.2, +2.4] | -10.6% [-14.0, -7.4] * |
| lang_carbon vs carbon_onehot | Does the embedding add beyond the language label? | -0.5 [-1.2, +0.2] | -2.2% [-5.8, +1.2] |
| lang_carbon vs carbon_ml_emb | Does the language label add beyond the embedding? | -0.8 [-1.3, -0.4] * | -1.9% [-4.8, +1.1] |
| carbon_ml_emb vs carbon_en_emb | Multilingual vs English encoder | +0.5 [-0.1, +1.2] | +3.2% [-0.6, +7.1] |
| carbon vs energy_pq | Does seeing the grid help? (carbon vs energy cost) | +8.0 [+5.9, +10.2] * | +38.8% [+35.4, +42.6] * |
| carbon vs carbon_no_flesch | Does Flesch complexity help? | +0.8 [+0.1, +1.5] * | -4.2% [-5.1, -3.2] * |
| carbon vs greenserv | Carbon cost vs GreenServ's energy-per-token cost | +10.2 [+5.4, +15.6] * | +262.6% [+229.0, +294.9] * |

## Test results by benchmark (all zones)

Pooled carbon above is a mean over all test queries, so it is almost entirely MGSM (an MGSM answer uses about 100x the energy of an XNLI or Belebele one). Here each benchmark is on its own; `% of largest` puts carbon on a common scale (always using the largest model = 100), and its benchmark average weights the three equally.

| strategy | acc belebele | acc mgsm | acc xnli | gCO2/1k belebele | gCO2/1k mgsm | gCO2/1k xnli | % of largest belebele | % of largest mgsm | % of largest xnli | % of largest, benchmarks averaged |
|---|---|---|---|---|---|---|---|---|---|---|
| greenserv | 0.814 | 0.652 | 0.657 | 1.694 | 55.180 | 1.575 | 39.570 | 16.188 | 53.404 | 36.387 |
| energy_pq | 0.833 | 0.871 | 0.599 | 1.290 | 158.884 | 0.968 | 30.134 | 46.612 | 32.826 | 36.524 |
| carbon | 0.898 | 0.925 | 0.705 | 1.753 | 220.741 | 1.276 | 40.948 | 64.759 | 43.248 | 49.651 |
| carbon_no_flesch | 0.908 | 0.935 | 0.672 | 2.073 | 229.823 | 1.297 | 48.407 | 67.423 | 43.956 | 53.262 |
| carbon_en_emb | 0.900 | 0.913 | 0.722 | 1.972 | 202.303 | 1.380 | 46.051 | 59.349 | 46.801 | 50.734 |
| carbon_onehot | 0.905 | 0.921 | 0.718 | 1.852 | 209.890 | 1.378 | 43.250 | 61.575 | 46.733 | 50.519 |
| carbon_ml_emb | 0.896 | 0.911 | 0.740 | 2.100 | 208.491 | 1.444 | 49.034 | 61.165 | 48.957 | 53.052 |
| lang_carbon | 0.889 | 0.908 | 0.728 | 1.959 | 204.790 | 1.386 | 45.745 | 60.079 | 47.004 | 50.943 |
| random | 0.860 | 0.825 | 0.700 | 2.437 | 218.092 | 1.908 | 56.918 | 63.982 | 64.697 | 61.865 |
| smallest | 0.730 | 0.609 | 0.593 | 0.951 | 87.642 | 0.813 | 22.211 | 25.712 | 27.565 | 25.162 |
| largest | 0.945 | 0.945 | 0.765 | 4.282 | 340.867 | 2.950 | 100.000 | 100.000 | 100.000 | 100.000 |
| best_fixed | 0.906 | 0.920 | 0.713 | 1.645 | 168.859 | 1.267 | 38.421 | 49.538 | 42.949 | 43.636 |
| oracle | 0.973 | 0.977 | 0.977 | 0.997 | 77.904 | 0.903 | 23.294 | 22.855 | 30.609 | 25.586 |

Share of each strategy's total carbon spent on each benchmark:

| strategy | share of carbon belebele | share of carbon mgsm | share of carbon xnli |
|---|---|---|---|
| greenserv | 0.062 | 0.879 | 0.059 |
| energy_pq | 0.019 | 0.967 | 0.014 |
| carbon | 0.021 | 0.964 | 0.015 |
| carbon_no_flesch | 0.024 | 0.961 | 0.015 |
| carbon_en_emb | 0.022 | 0.962 | 0.016 |
| carbon_onehot | 0.022 | 0.962 | 0.016 |
| carbon_ml_emb | 0.023 | 0.961 | 0.016 |
| lang_carbon | 0.021 | 0.963 | 0.016 |
| random | 0.025 | 0.955 | 0.020 |
| smallest | 0.024 | 0.955 | 0.021 |
| largest | 0.028 | 0.953 | 0.019 |
| best_fixed | 0.024 | 0.958 | 0.018 |
| oracle | 0.028 | 0.946 | 0.026 |

## Test accuracy by language (all zones)

| strategy | en | de | es | fr | ru | zh | th | sw | worst |
|---|---|---|---|---|---|---|---|---|---|
| greenserv | 0.785 | 0.734 | 0.716 | 0.756 | 0.737 | 0.692 | 0.669 | 0.678 | 0.669 |
| energy_pq | 0.792 | 0.759 | 0.786 | 0.760 | 0.736 | 0.720 | 0.711 | 0.684 | 0.684 |
| carbon | 0.881 | 0.826 | 0.853 | 0.840 | 0.823 | 0.808 | 0.797 | 0.758 | 0.758 |
| carbon_no_flesch | 0.869 | 0.827 | 0.846 | 0.834 | 0.806 | 0.800 | 0.790 | 0.752 | 0.752 |
| carbon_en_emb | 0.891 | 0.835 | 0.866 | 0.843 | 0.818 | 0.816 | 0.801 | 0.761 | 0.761 |
| carbon_onehot | 0.898 | 0.820 | 0.887 | 0.839 | 0.823 | 0.820 | 0.796 | 0.762 | 0.762 |
| carbon_ml_emb | 0.898 | 0.831 | 0.867 | 0.846 | 0.822 | 0.825 | 0.810 | 0.775 | 0.775 |
| lang_carbon | 0.895 | 0.826 | 0.853 | 0.834 | 0.818 | 0.816 | 0.800 | 0.766 | 0.766 |
| random | 0.854 | 0.816 | 0.792 | 0.811 | 0.785 | 0.776 | 0.758 | 0.710 | 0.710 |
| smallest | 0.753 | 0.687 | 0.659 | 0.703 | 0.670 | 0.659 | 0.637 | 0.451 | 0.451 |
| largest | 0.940 | 0.879 | 0.901 | 0.890 | 0.852 | 0.863 | 0.830 | 0.813 | 0.813 |
| best_fixed | 0.889 | 0.837 | 0.864 | 0.847 | 0.823 | 0.817 | 0.799 | 0.755 | 0.755 |
| oracle | 0.995 | 0.973 | 0.973 | 0.973 | 0.978 | 0.956 | 0.967 | 0.989 | 0.956 |

## FR

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.721 | 0.662 | 1.134 | 180.458 |
| energy_pq | 0.744 | 0.679 | 2.955 | 468.445 |
| carbon | 0.871 | 0.821 | 7.229 | 1154.930 |
| carbon_no_flesch | 0.857 | 0.801 | 6.425 | 1020.656 |
| carbon_en_emb | 0.858 | 0.804 | 6.491 | 1044.726 |
| carbon_onehot | 0.868 | 0.805 | 6.740 | 1068.348 |
| carbon_ml_emb | 0.858 | 0.819 | 6.339 | 1012.444 |
| lang_carbon | 0.855 | 0.799 | 6.626 | 1067.502 |
| random | 0.788 | 0.710 | 4.121 | 656.132 |
| smallest | 0.652 | 0.451 | 1.661 | 263.968 |
| largest | 0.871 | 0.813 | 6.474 | 1029.025 |
| best_fixed | 0.871 | 0.813 | 6.474 | 1029.025 |
| oracle | 0.975 | 0.956 | 1.488 | 236.962 |

## SE-SE3

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.721 | 0.662 | 0.934 | 180.458 |
| energy_pq | 0.744 | 0.679 | 2.432 | 468.445 |
| carbon | 0.873 | 0.823 | 5.977 | 1134.578 |
| carbon_no_flesch | 0.856 | 0.801 | 4.699 | 918.515 |
| carbon_en_emb | 0.862 | 0.810 | 5.898 | 1134.477 |
| carbon_onehot | 0.870 | 0.808 | 5.327 | 998.609 |
| carbon_ml_emb | 0.863 | 0.808 | 5.982 | 1150.909 |
| lang_carbon | 0.857 | 0.800 | 5.640 | 1092.593 |
| random | 0.788 | 0.710 | 3.423 | 656.132 |
| smallest | 0.652 | 0.451 | 1.370 | 263.968 |
| largest | 0.871 | 0.813 | 5.343 | 1029.025 |
| best_fixed | 0.871 | 0.813 | 5.343 | 1029.025 |
| oracle | 0.975 | 0.956 | 1.231 | 236.962 |

## DE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.721 | 0.662 | 8.827 | 180.458 |
| energy_pq | 0.744 | 0.679 | 23.196 | 468.445 |
| carbon | 0.813 | 0.742 | 31.462 | 652.923 |
| carbon_no_flesch | 0.796 | 0.738 | 35.792 | 801.018 |
| carbon_en_emb | 0.833 | 0.757 | 30.207 | 653.048 |
| carbon_onehot | 0.817 | 0.752 | 34.781 | 719.904 |
| carbon_ml_emb | 0.848 | 0.778 | 37.683 | 798.718 |
| lang_carbon | 0.829 | 0.764 | 34.182 | 740.584 |
| random | 0.788 | 0.710 | 31.908 | 656.132 |
| smallest | 0.652 | 0.451 | 12.861 | 263.968 |
| largest | 0.871 | 0.813 | 50.171 | 1029.025 |
| best_fixed | 0.822 | 0.733 | 24.778 | 523.210 |
| oracle | 0.975 | 0.956 | 11.549 | 236.962 |

## US-CAL-CISO

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.721 | 0.662 | 12.178 | 180.458 |
| energy_pq | 0.744 | 0.679 | 32.410 | 468.445 |
| carbon | 0.828 | 0.758 | 53.762 | 876.472 |
| carbon_no_flesch | 0.816 | 0.757 | 57.109 | 905.131 |
| carbon_en_emb | 0.833 | 0.744 | 46.754 | 735.099 |
| carbon_onehot | 0.845 | 0.759 | 47.841 | 739.487 |
| carbon_ml_emb | 0.830 | 0.771 | 50.148 | 794.352 |
| lang_carbon | 0.838 | 0.770 | 44.541 | 696.811 |
| random | 0.788 | 0.710 | 44.790 | 656.132 |
| smallest | 0.652 | 0.451 | 17.832 | 263.968 |
| largest | 0.871 | 0.813 | 69.453 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 38.519 | 569.385 |
| oracle | 0.975 | 0.956 | 15.957 | 236.962 |

## US-NE-ISNE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.721 | 0.662 | 16.775 | 180.458 |
| energy_pq | 0.744 | 0.679 | 43.332 | 468.445 |
| carbon | 0.794 | 0.722 | 62.363 | 676.931 |
| carbon_no_flesch | 0.794 | 0.727 | 65.837 | 692.074 |
| carbon_en_emb | 0.826 | 0.733 | 61.597 | 652.585 |
| carbon_onehot | 0.810 | 0.707 | 55.845 | 610.059 |
| carbon_ml_emb | 0.823 | 0.747 | 54.922 | 589.228 |
| lang_carbon | 0.817 | 0.743 | 62.982 | 670.701 |
| random | 0.788 | 0.710 | 61.015 | 656.132 |
| smallest | 0.652 | 0.451 | 24.534 | 263.968 |
| largest | 0.871 | 0.813 | 95.650 | 1029.025 |
| best_fixed | 0.785 | 0.713 | 43.864 | 477.036 |
| oracle | 0.975 | 0.956 | 22.022 | 236.962 |

## PL

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.721 | 0.662 | 26.447 | 180.458 |
| energy_pq | 0.744 | 0.679 | 68.874 | 468.445 |
| carbon | 0.761 | 0.680 | 79.566 | 571.381 |
| carbon_no_flesch | 0.775 | 0.687 | 80.919 | 576.874 |
| carbon_en_emb | 0.760 | 0.693 | 70.760 | 483.501 |
| carbon_onehot | 0.775 | 0.697 | 78.875 | 551.866 |
| carbon_ml_emb | 0.783 | 0.713 | 73.636 | 502.646 |
| lang_carbon | 0.761 | 0.697 | 70.343 | 485.244 |
| random | 0.788 | 0.710 | 95.564 | 656.132 |
| smallest | 0.652 | 0.451 | 38.561 | 263.968 |
| largest | 0.871 | 0.813 | 150.386 | 1029.025 |
| best_fixed | 0.767 | 0.703 | 66.358 | 453.948 |
| oracle | 0.975 | 0.956 | 34.636 | 236.962 |
