# Routing results: 20261112_223018

- Hardware: NVIDIA A100-SXM4-80GB; models: gemma-4-31b, gemma-4-e4b, qwen3.5-27b, qwen3.5-2b, qwen3.5-9b, tiny-aya-global
- Algorithm: linucb, lambda = 0.9, 5 runs, 250 queries/hour
- Zones: FR, SE-SE3, DE, US-CAL-CISO, US-NE-ISNE, PL

## Test phase, averaged over zones

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.703 | 0.648 | 10.733 | 175.572 |
| energy_pq | 0.657 | 0.487 | 11.547 | 186.139 |
| carbon | 0.783 | 0.714 | 20.814 | 578.060 |
| carbon_no_flesch | 0.818 | 0.750 | 31.571 | 756.027 |
| carbon_en_emb | 0.773 | 0.705 | 21.182 | 545.395 |
| carbon_onehot | 0.775 | 0.703 | 19.528 | 579.439 |
| carbon_ml_emb | 0.772 | 0.702 | 21.465 | 577.431 |
| lang_carbon | 0.777 | 0.714 | 22.010 | 567.590 |
| random | 0.788 | 0.710 | 40.137 | 656.132 |
| smallest | 0.652 | 0.451 | 16.137 | 263.968 |
| largest | 0.871 | 0.813 | 62.913 | 1029.025 |
| best_fixed | 0.783 | 0.688 | 24.104 | 482.418 |
| oracle | 0.968 | 0.950 | 14.022 | 233.830 |

## Paired comparisons (all zones)

Router minus reference on the same queries. Accuracy in points, carbon in % of the reference. 95% bootstrap CI over test items; * = CI excludes 0.

| comparison | question | accuracy (pp) | carbon (%) |
|---|---|---|---|
| lang_carbon vs largest | Savings vs always using the largest model | -9.4 [-12.1, -6.7] * | -65.0% [-67.2, -62.8] * |
| lang_carbon vs best_fixed | vs the best single model in hindsight | -0.6 [-1.4, +0.2] | -8.7% [-12.6, -4.7] * |
| lang_carbon vs greenserv | vs GreenServ (energy-per-token cost, English features) | +7.3 [+1.9, +13.2] * | +105.1% [+89.5, +119.7] * |
| lang_carbon vs carbon_no_flesch | Do language + multilingual embedding help? | -4.2 [-5.4, -2.9] * | -30.3% [-33.1, -27.2] * |
| lang_carbon vs carbon_onehot | Does the embedding add beyond the language label? | +0.1 [-0.7, +1.0] | +12.7% [+8.9, +16.8] * |
| lang_carbon vs carbon_ml_emb | Does the language label add beyond the embedding? | +0.5 [+0.0, +0.9] * | +2.5% [+0.5, +4.7] * |
| carbon_ml_emb vs carbon_en_emb | Multilingual vs English encoder | -0.1 [-0.8, +0.7] | +1.3% [-2.9, +5.6] |
| carbon vs energy_pq | Does seeing the grid help? (carbon vs energy cost) | +12.7 [+8.9, +16.5] * | +80.3% [+71.1, +89.3] * |
| carbon vs carbon_no_flesch | Does Flesch complexity help? | -3.5 [-4.4, -2.6] * | -34.1% [-35.6, -32.5] * |
| carbon vs greenserv | Carbon cost vs GreenServ's energy-per-token cost | +8.0 [+2.4, +14.3] * | +93.9% [+79.8, +107.9] * |

## Test results by benchmark (all zones)

Pooled carbon above is a mean over all test queries, so it is almost entirely MGSM (an MGSM answer uses about 100x the energy of an XNLI or Belebele one). Here each benchmark is on its own; `% of largest` puts carbon on a common scale (always using the largest model = 100), and its benchmark average weights the three equally.

| strategy | acc belebele | acc mgsm | acc xnli | gCO2/1k belebele | gCO2/1k mgsm | gCO2/1k xnli | % of largest belebele | % of largest mgsm | % of largest xnli | % of largest, benchmarks averaged |
|---|---|---|---|---|---|---|---|---|---|---|
| greenserv | 0.765 | 0.651 | 0.664 | 1.609 | 53.517 | 1.603 | 37.577 | 15.700 | 54.363 | 35.880 |
| energy_pq | 0.730 | 0.642 | 0.589 | 0.984 | 61.311 | 0.878 | 22.968 | 17.987 | 29.757 | 23.571 |
| carbon | 0.880 | 0.861 | 0.654 | 1.343 | 112.812 | 1.032 | 31.359 | 33.096 | 34.978 | 33.144 |
| carbon_no_flesch | 0.906 | 0.908 | 0.692 | 1.943 | 171.684 | 1.418 | 45.380 | 50.367 | 48.085 | 47.944 |
| carbon_en_emb | 0.860 | 0.848 | 0.653 | 1.351 | 114.987 | 0.989 | 31.558 | 33.734 | 33.536 | 32.942 |
| carbon_onehot | 0.872 | 0.836 | 0.653 | 1.281 | 105.726 | 0.996 | 29.918 | 31.017 | 33.781 | 31.572 |
| carbon_ml_emb | 0.855 | 0.844 | 0.658 | 1.337 | 116.573 | 1.013 | 31.217 | 34.199 | 34.357 | 33.258 |
| lang_carbon | 0.856 | 0.848 | 0.667 | 1.384 | 119.509 | 1.036 | 32.317 | 35.060 | 35.131 | 34.169 |
| random | 0.860 | 0.825 | 0.700 | 2.437 | 218.092 | 1.908 | 56.918 | 63.982 | 64.697 | 61.865 |
| smallest | 0.730 | 0.609 | 0.593 | 0.951 | 87.642 | 0.813 | 22.211 | 25.712 | 27.565 | 25.162 |
| largest | 0.945 | 0.945 | 0.765 | 4.282 | 340.867 | 2.950 | 100.000 | 100.000 | 100.000 | 100.000 |
| best_fixed | 0.865 | 0.872 | 0.662 | 1.219 | 132.038 | 0.938 | 28.463 | 38.736 | 31.811 | 33.003 |
| oracle | 0.970 | 0.973 | 0.964 | 0.971 | 75.454 | 0.861 | 22.686 | 22.136 | 29.189 | 24.670 |

Share of each strategy's total carbon spent on each benchmark:

| strategy | share of carbon belebele | share of carbon mgsm | share of carbon xnli |
|---|---|---|---|
| greenserv | 0.062 | 0.877 | 0.062 |
| energy_pq | 0.037 | 0.930 | 0.033 |
| carbon | 0.028 | 0.951 | 0.021 |
| carbon_no_flesch | 0.027 | 0.954 | 0.019 |
| carbon_en_emb | 0.026 | 0.956 | 0.019 |
| carbon_onehot | 0.027 | 0.952 | 0.020 |
| carbon_ml_emb | 0.025 | 0.957 | 0.018 |
| lang_carbon | 0.025 | 0.956 | 0.019 |
| random | 0.025 | 0.955 | 0.020 |
| smallest | 0.024 | 0.955 | 0.021 |
| largest | 0.028 | 0.953 | 0.019 |
| best_fixed | 0.022 | 0.960 | 0.017 |
| oracle | 0.028 | 0.946 | 0.025 |

## Test accuracy by language (all zones)

| strategy | en | de | es | fr | ru | zh | th | sw | worst |
|---|---|---|---|---|---|---|---|---|---|
| greenserv | 0.775 | 0.714 | 0.692 | 0.742 | 0.708 | 0.665 | 0.648 | 0.681 | 0.648 |
| energy_pq | 0.744 | 0.696 | 0.660 | 0.718 | 0.665 | 0.653 | 0.631 | 0.487 | 0.487 |
| carbon | 0.837 | 0.800 | 0.814 | 0.807 | 0.780 | 0.764 | 0.749 | 0.716 | 0.716 |
| carbon_no_flesch | 0.876 | 0.832 | 0.848 | 0.838 | 0.811 | 0.807 | 0.786 | 0.750 | 0.750 |
| carbon_en_emb | 0.832 | 0.782 | 0.787 | 0.795 | 0.776 | 0.754 | 0.745 | 0.708 | 0.708 |
| carbon_onehot | 0.834 | 0.791 | 0.794 | 0.794 | 0.779 | 0.763 | 0.742 | 0.704 | 0.704 |
| carbon_ml_emb | 0.838 | 0.779 | 0.793 | 0.788 | 0.774 | 0.761 | 0.740 | 0.702 | 0.702 |
| lang_carbon | 0.846 | 0.783 | 0.804 | 0.785 | 0.771 | 0.766 | 0.744 | 0.714 | 0.714 |
| random | 0.854 | 0.816 | 0.792 | 0.811 | 0.785 | 0.776 | 0.758 | 0.710 | 0.710 |
| smallest | 0.753 | 0.687 | 0.659 | 0.703 | 0.670 | 0.659 | 0.637 | 0.451 | 0.451 |
| largest | 0.940 | 0.879 | 0.901 | 0.890 | 0.852 | 0.863 | 0.830 | 0.813 | 0.813 |
| best_fixed | 0.841 | 0.795 | 0.815 | 0.803 | 0.786 | 0.771 | 0.760 | 0.688 | 0.688 |
| oracle | 0.986 | 0.969 | 0.968 | 0.965 | 0.966 | 0.953 | 0.959 | 0.979 | 0.953 |

## FR

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.703 | 0.648 | 1.104 | 175.572 |
| energy_pq | 0.657 | 0.487 | 1.194 | 186.139 |
| carbon | 0.871 | 0.813 | 6.477 | 1029.526 |
| carbon_no_flesch | 0.871 | 0.813 | 6.477 | 1029.526 |
| carbon_en_emb | 0.855 | 0.807 | 5.599 | 892.148 |
| carbon_onehot | 0.871 | 0.813 | 6.477 | 1029.526 |
| carbon_ml_emb | 0.859 | 0.804 | 6.089 | 969.871 |
| lang_carbon | 0.861 | 0.813 | 5.600 | 890.401 |
| random | 0.788 | 0.710 | 4.121 | 656.132 |
| smallest | 0.652 | 0.451 | 1.661 | 263.968 |
| largest | 0.871 | 0.813 | 6.474 | 1029.025 |
| best_fixed | 0.858 | 0.753 | 3.585 | 569.385 |
| oracle | 0.975 | 0.956 | 1.488 | 236.962 |

## SE-SE3

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.703 | 0.648 | 0.911 | 175.572 |
| energy_pq | 0.657 | 0.487 | 0.963 | 186.139 |
| carbon | 0.871 | 0.813 | 5.346 | 1029.526 |
| carbon_no_flesch | 0.871 | 0.813 | 5.346 | 1029.526 |
| carbon_en_emb | 0.854 | 0.808 | 4.568 | 872.827 |
| carbon_onehot | 0.871 | 0.813 | 5.346 | 1029.526 |
| carbon_ml_emb | 0.858 | 0.809 | 5.035 | 978.628 |
| lang_carbon | 0.858 | 0.811 | 4.959 | 959.089 |
| random | 0.788 | 0.710 | 3.423 | 656.132 |
| smallest | 0.652 | 0.451 | 1.370 | 263.968 |
| largest | 0.871 | 0.813 | 5.343 | 1029.025 |
| best_fixed | 0.860 | 0.765 | 3.491 | 661.313 |
| oracle | 0.975 | 0.956 | 1.231 | 236.962 |

## DE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.703 | 0.648 | 8.565 | 175.572 |
| energy_pq | 0.657 | 0.487 | 9.682 | 186.139 |
| carbon | 0.758 | 0.695 | 18.310 | 406.617 |
| carbon_no_flesch | 0.829 | 0.769 | 35.324 | 799.495 |
| carbon_en_emb | 0.758 | 0.678 | 20.622 | 460.050 |
| carbon_onehot | 0.760 | 0.684 | 22.643 | 520.797 |
| carbon_ml_emb | 0.755 | 0.685 | 22.694 | 482.440 |
| lang_carbon | 0.763 | 0.699 | 20.264 | 454.114 |
| random | 0.788 | 0.710 | 31.908 | 656.132 |
| smallest | 0.652 | 0.451 | 12.861 | 263.968 |
| largest | 0.871 | 0.813 | 50.171 | 1029.025 |
| best_fixed | 0.767 | 0.703 | 22.153 | 453.948 |
| oracle | 0.974 | 0.956 | 11.546 | 236.935 |

## US-CAL-CISO

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.703 | 0.648 | 11.841 | 175.572 |
| energy_pq | 0.657 | 0.487 | 12.825 | 186.139 |
| carbon | 0.750 | 0.686 | 24.829 | 397.728 |
| carbon_no_flesch | 0.850 | 0.791 | 57.672 | 914.510 |
| carbon_en_emb | 0.738 | 0.666 | 28.811 | 436.847 |
| carbon_onehot | 0.744 | 0.676 | 24.957 | 395.867 |
| carbon_ml_emb | 0.755 | 0.695 | 29.700 | 451.055 |
| lang_carbon | 0.756 | 0.703 | 31.514 | 473.310 |
| random | 0.788 | 0.710 | 44.790 | 656.132 |
| smallest | 0.652 | 0.451 | 17.832 | 263.968 |
| largest | 0.871 | 0.813 | 69.453 | 1029.025 |
| best_fixed | 0.767 | 0.703 | 30.653 | 453.948 |
| oracle | 0.971 | 0.954 | 15.850 | 235.908 |

## US-NE-ISNE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.703 | 0.648 | 16.320 | 175.572 |
| energy_pq | 0.657 | 0.487 | 16.901 | 186.139 |
| carbon | 0.736 | 0.669 | 29.379 | 309.303 |
| carbon_no_flesch | 0.767 | 0.703 | 42.232 | 454.449 |
| carbon_en_emb | 0.737 | 0.660 | 33.744 | 365.103 |
| carbon_onehot | 0.721 | 0.623 | 26.537 | 281.293 |
| carbon_ml_emb | 0.722 | 0.646 | 32.210 | 351.958 |
| lang_carbon | 0.726 | 0.644 | 34.299 | 371.531 |
| random | 0.788 | 0.710 | 61.015 | 656.132 |
| smallest | 0.652 | 0.451 | 24.534 | 263.968 |
| largest | 0.871 | 0.813 | 95.650 | 1029.025 |
| best_fixed | 0.767 | 0.703 | 42.186 | 453.948 |
| oracle | 0.966 | 0.952 | 21.636 | 232.997 |

## PL

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.703 | 0.648 | 25.659 | 175.572 |
| energy_pq | 0.657 | 0.487 | 27.717 | 186.139 |
| carbon | 0.714 | 0.608 | 40.541 | 295.663 |
| carbon_no_flesch | 0.722 | 0.608 | 42.376 | 308.656 |
| carbon_en_emb | 0.694 | 0.612 | 33.748 | 245.397 |
| carbon_onehot | 0.685 | 0.612 | 31.206 | 219.626 |
| carbon_ml_emb | 0.683 | 0.574 | 33.060 | 230.636 |
| lang_carbon | 0.695 | 0.611 | 35.423 | 257.098 |
| random | 0.788 | 0.710 | 95.564 | 656.132 |
| smallest | 0.652 | 0.451 | 38.561 | 263.968 |
| largest | 0.871 | 0.813 | 150.386 | 1029.025 |
| best_fixed | 0.675 | 0.501 | 42.558 | 301.964 |
| oracle | 0.946 | 0.926 | 32.380 | 223.216 |
