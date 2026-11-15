# Routing results: 20261115_143055

- Hardware: NVIDIA A100-SXM4-80GB; models: gemma-4-31b, gemma-4-e4b, qwen3.5-27b, qwen3.5-2b, qwen3.5-9b, tiny-aya-global
- Algorithm: linucb, lambda = 0.9, 5 runs, 250 queries/hour
- Zones: FR, SE-SE3, DE, US-CAL-CISO, US-NE-ISNE, PL

## Test phase, averaged over zones

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.768 | 0.711 | 12.061 | 369.909 |
| carbon_pt_floor | 0.836 | 0.775 | 31.270 | 598.152 |
| random | 0.788 | 0.710 | 40.137 | 656.132 |
| smallest | 0.652 | 0.451 | 16.137 | 263.968 |
| largest | 0.871 | 0.813 | 62.913 | 1029.025 |
| best_fixed | 0.755 | 0.685 | 11.538 | 321.734 |
| oracle | 0.962 | 0.939 | 13.314 | 233.035 |

## Paired comparisons (all zones)

Router minus reference on the same queries. Accuracy in points, carbon in % of the reference. 95% bootstrap CI over test items; * = CI excludes 0.

## Test results by benchmark (all zones)

Pooled carbon above is a mean over all test queries, so it is almost entirely MGSM (an MGSM answer uses about 100x the energy of an XNLI or Belebele one). Here each benchmark is on its own; `% of largest` puts carbon on a common scale (always using the largest model = 100), and its benchmark average weights the three equally.

| strategy | acc belebele | acc mgsm | acc xnli | gCO2/1k belebele | gCO2/1k mgsm | gCO2/1k xnli | % of largest belebele | % of largest mgsm | % of largest xnli | % of largest, benchmarks averaged |
|---|---|---|---|---|---|---|---|---|---|---|
| carbon_pt_lang | 0.844 | 0.744 | 0.703 | 1.670 | 60.886 | 1.621 | 38.990 | 17.862 | 54.971 | 37.274 |
| carbon_pt_floor | 0.912 | 0.903 | 0.730 | 2.352 | 168.474 | 1.648 | 54.927 | 49.425 | 55.877 | 53.410 |
| random | 0.860 | 0.825 | 0.700 | 2.437 | 218.092 | 1.908 | 56.918 | 63.982 | 64.697 | 61.865 |
| smallest | 0.730 | 0.609 | 0.593 | 0.951 | 87.642 | 0.813 | 22.211 | 25.712 | 27.565 | 25.162 |
| largest | 0.945 | 0.945 | 0.765 | 4.282 | 340.867 | 2.950 | 100.000 | 100.000 | 100.000 | 100.000 |
| best_fixed | 0.814 | 0.734 | 0.706 | 1.604 | 58.148 | 1.585 | 37.447 | 17.059 | 53.723 | 36.076 |
| oracle | 0.971 | 0.950 | 0.959 | 1.278 | 69.468 | 1.392 | 29.855 | 20.380 | 47.180 | 32.472 |

Share of each strategy's total carbon spent on each benchmark:

| strategy | share of carbon belebele | share of carbon mgsm | share of carbon xnli |
|---|---|---|---|
| carbon_pt_lang | 0.052 | 0.901 | 0.046 |
| carbon_pt_floor | 0.033 | 0.945 | 0.021 |
| random | 0.025 | 0.955 | 0.020 |
| smallest | 0.024 | 0.955 | 0.021 |
| largest | 0.028 | 0.953 | 0.019 |
| best_fixed | 0.049 | 0.903 | 0.048 |
| oracle | 0.037 | 0.922 | 0.041 |

## Test accuracy by language (all zones)

| strategy | en | de | es | fr | ru | zh | th | sw | worst |
|---|---|---|---|---|---|---|---|---|---|
| carbon_pt_lang | 0.833 | 0.779 | 0.775 | 0.803 | 0.773 | 0.735 | 0.719 | 0.729 | 0.719 |
| carbon_pt_floor | 0.888 | 0.829 | 0.874 | 0.847 | 0.825 | 0.824 | 0.805 | 0.793 | 0.793 |
| random | 0.854 | 0.816 | 0.792 | 0.811 | 0.785 | 0.776 | 0.758 | 0.710 | 0.710 |
| smallest | 0.753 | 0.687 | 0.659 | 0.703 | 0.670 | 0.659 | 0.637 | 0.451 | 0.451 |
| largest | 0.940 | 0.879 | 0.901 | 0.890 | 0.852 | 0.863 | 0.830 | 0.813 | 0.813 |
| best_fixed | 0.830 | 0.761 | 0.764 | 0.788 | 0.756 | 0.727 | 0.709 | 0.707 | 0.707 |
| oracle | 0.984 | 0.965 | 0.962 | 0.963 | 0.963 | 0.940 | 0.950 | 0.973 | 0.940 |

## FR

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.868 | 0.814 | 4.202 | 665.318 |
| carbon_pt_floor | 0.868 | 0.814 | 4.202 | 665.318 |
| random | 0.788 | 0.710 | 4.121 | 656.132 |
| smallest | 0.652 | 0.451 | 1.661 | 263.968 |
| largest | 0.871 | 0.813 | 6.474 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 3.585 | 569.385 |
| oracle | 0.975 | 0.956 | 1.556 | 247.624 |

## SE-SE3

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.870 | 0.824 | 4.216 | 815.907 |
| carbon_pt_floor | 0.870 | 0.824 | 4.216 | 815.907 |
| random | 0.788 | 0.710 | 3.423 | 656.132 |
| smallest | 0.652 | 0.451 | 1.370 | 263.968 |
| largest | 0.871 | 0.813 | 5.343 | 1029.025 |
| best_fixed | 0.860 | 0.765 | 3.491 | 661.313 |
| oracle | 0.975 | 0.956 | 1.286 | 247.624 |

## DE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.734 | 0.667 | 8.948 | 185.576 |
| carbon_pt_floor | 0.832 | 0.770 | 26.037 | 547.053 |
| random | 0.788 | 0.710 | 31.908 | 656.132 |
| smallest | 0.652 | 0.451 | 12.861 | 263.968 |
| largest | 0.871 | 0.813 | 50.171 | 1029.025 |
| best_fixed | 0.703 | 0.648 | 8.529 | 174.927 |
| oracle | 0.972 | 0.951 | 11.550 | 239.077 |

## US-CAL-CISO

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.724 | 0.660 | 12.912 | 200.083 |
| carbon_pt_floor | 0.830 | 0.773 | 37.274 | 568.010 |
| random | 0.788 | 0.710 | 44.790 | 656.132 |
| smallest | 0.652 | 0.451 | 17.832 | 263.968 |
| largest | 0.871 | 0.813 | 69.453 | 1029.025 |
| best_fixed | 0.703 | 0.648 | 11.793 | 174.927 |
| oracle | 0.968 | 0.945 | 15.649 | 235.220 |

## US-NE-ISNE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.709 | 0.648 | 16.491 | 177.348 |
| carbon_pt_floor | 0.812 | 0.748 | 50.821 | 542.609 |
| random | 0.788 | 0.710 | 61.015 | 656.132 |
| smallest | 0.652 | 0.451 | 24.534 | 263.968 |
| largest | 0.871 | 0.813 | 95.650 | 1029.025 |
| best_fixed | 0.703 | 0.648 | 16.261 | 174.927 |
| oracle | 0.960 | 0.936 | 21.354 | 229.940 |

## PL

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| carbon_pt_lang | 0.703 | 0.649 | 25.600 | 175.220 |
| carbon_pt_floor | 0.802 | 0.719 | 65.072 | 450.016 |
| random | 0.788 | 0.710 | 95.564 | 656.132 |
| smallest | 0.652 | 0.451 | 38.561 | 263.968 |
| largest | 0.871 | 0.813 | 150.386 | 1029.025 |
| best_fixed | 0.703 | 0.648 | 25.566 | 174.927 |
| oracle | 0.924 | 0.891 | 28.491 | 198.722 |
