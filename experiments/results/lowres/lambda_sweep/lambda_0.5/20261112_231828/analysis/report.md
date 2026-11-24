# Routing results: 20261112_231828

- Hardware: NVIDIA A100-SXM4-80GB; models: gemma-4-31b, gemma-4-e4b, qwen3.5-27b, qwen3.5-2b, qwen3.5-9b, tiny-aya-global
- Algorithm: linucb, lambda = 0.5, 5 runs, 250 queries/hour
- Zones: FR, SE-SE3, DE, US-CAL-CISO, US-NE-ISNE, PL

## Test phase, averaged over zones

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.731 | 0.496 | 4.363 | 53.612 |
| energy_pq | 0.763 | 0.549 | 5.486 | 66.551 |
| carbon | 0.797 | 0.562 | 6.055 | 83.195 |
| carbon_no_flesch | 0.798 | 0.554 | 6.302 | 80.700 |
| carbon_en_emb | 0.782 | 0.529 | 5.795 | 78.625 |
| carbon_onehot | 0.787 | 0.456 | 5.736 | 78.068 |
| carbon_ml_emb | 0.789 | 0.558 | 5.986 | 80.703 |
| lang_carbon | 0.782 | 0.529 | 5.952 | 79.610 |
| random | 0.661 | 0.413 | 4.548 | 55.549 |
| smallest | 0.449 | 0.293 | 1.944 | 23.741 |
| largest | 0.827 | 0.600 | 6.927 | 84.600 |
| best_fixed | 0.827 | 0.600 | 6.927 | 84.600 |
| oracle | 0.929 | 0.787 | 2.455 | 29.985 |

## Paired comparisons (all zones)

Router minus reference on the same queries. Accuracy in points, carbon in % of the reference. 95% bootstrap CI over test items; * = CI excludes 0.

| comparison | question | accuracy (pp) | carbon (%) |
|---|---|---|---|
| lang_carbon vs largest | Savings vs always using the largest model | -4.4 [-5.6, -3.3] * | -14.1% [-15.2, -12.9] * |
| lang_carbon vs best_fixed | vs the best single model in hindsight | -4.4 [-5.6, -3.3] * | -14.1% [-15.2, -12.9] * |
| lang_carbon vs greenserv | vs GreenServ (energy-per-token cost, English features) | +5.1 [+3.5, +6.9] * | +36.4% [+34.8, +38.1] * |
| lang_carbon vs carbon_no_flesch | Do language + multilingual embedding help? | -1.6 [-2.2, -0.9] * | -5.6% [-6.8, -4.4] * |
| lang_carbon vs carbon_onehot | Does the embedding add beyond the language label? | -0.5 [-1.0, +0.0] | +3.8% [+2.5, +5.0] * |
| lang_carbon vs carbon_ml_emb | Does the language label add beyond the embedding? | -0.6 [-1.1, -0.1] * | -0.6% [-1.8, +0.7] |
| carbon_ml_emb vs carbon_en_emb | Multilingual vs English encoder | +0.7 [+0.1, +1.3] * | +3.3% [+1.9, +4.8] * |
| carbon vs energy_pq | Does seeing the grid help? (carbon vs energy cost) | +3.4 [+2.5, +4.5] * | +10.4% [+9.8, +11.0] * |
| carbon vs carbon_no_flesch | Does Flesch complexity help? | -0.0 [-0.5, +0.4] | -3.9% [-4.4, -3.5] * |
| carbon vs greenserv | Carbon cost vs GreenServ's energy-per-token cost | +6.6 [+4.9, +8.6] * | +38.8% [+37.6, +39.9] * |

## Test results by benchmark (all zones)

Pooled carbon above is a mean over all test queries, so it is almost entirely MGSM (an MGSM answer uses about 100x the energy of an XNLI or Belebele one). Here each benchmark is on its own; `% of largest` puts carbon on a common scale (always using the largest model = 100), and its benchmark average weights the three equally.

| strategy | acc belebele | gCO2/1k belebele | % of largest belebele | % of largest, benchmarks averaged |
|---|---|---|---|---|
| greenserv | 0.731 | 4.363 | 62.983 | 62.983 |
| energy_pq | 0.763 | 5.486 | 79.197 | 79.197 |
| carbon | 0.797 | 6.055 | 87.418 | 87.418 |
| carbon_no_flesch | 0.798 | 6.302 | 90.986 | 90.986 |
| carbon_en_emb | 0.782 | 5.795 | 83.665 | 83.665 |
| carbon_onehot | 0.787 | 5.736 | 82.809 | 82.809 |
| carbon_ml_emb | 0.789 | 5.986 | 86.414 | 86.414 |
| lang_carbon | 0.782 | 5.952 | 85.923 | 85.923 |
| random | 0.661 | 4.548 | 65.665 | 65.665 |
| smallest | 0.449 | 1.944 | 28.063 | 28.063 |
| largest | 0.827 | 6.927 | 100.000 | 100.000 |
| best_fixed | 0.827 | 6.927 | 100.000 | 100.000 |
| oracle | 0.929 | 2.455 | 35.446 | 35.446 |

Share of each strategy's total carbon spent on each benchmark:

| strategy | share of carbon belebele |
|---|---|
| greenserv | 1.000 |
| energy_pq | 1.000 |
| carbon | 1.000 |
| carbon_no_flesch | 1.000 |
| carbon_en_emb | 1.000 |
| carbon_onehot | 1.000 |
| carbon_ml_emb | 1.000 |
| lang_carbon | 1.000 |
| random | 1.000 |
| smallest | 1.000 |
| largest | 1.000 |
| best_fixed | 1.000 |
| oracle | 1.000 |

## Test accuracy by language (all zones)

| strategy | en | sw | am | gn | ha | ig | km | lo | my | ne | si | wo | yo | zu | worst |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| greenserv | 0.880 | 0.845 | 0.696 | 0.603 | 0.715 | 0.680 | 0.821 | 0.755 | 0.875 | 0.765 | 0.813 | 0.507 | 0.600 | 0.685 | 0.507 |
| energy_pq | 0.915 | 0.899 | 0.739 | 0.707 | 0.755 | 0.723 | 0.819 | 0.757 | 0.824 | 0.797 | 0.829 | 0.549 | 0.621 | 0.755 | 0.549 |
| carbon | 0.980 | 0.914 | 0.789 | 0.730 | 0.773 | 0.740 | 0.857 | 0.792 | 0.866 | 0.842 | 0.917 | 0.568 | 0.629 | 0.766 | 0.568 |
| carbon_no_flesch | 0.967 | 0.908 | 0.832 | 0.725 | 0.768 | 0.720 | 0.882 | 0.804 | 0.878 | 0.850 | 0.919 | 0.554 | 0.610 | 0.755 | 0.554 |
| carbon_en_emb | 0.956 | 0.885 | 0.813 | 0.711 | 0.764 | 0.704 | 0.855 | 0.784 | 0.863 | 0.815 | 0.908 | 0.530 | 0.606 | 0.749 | 0.530 |
| carbon_onehot | 0.973 | 0.902 | 0.804 | 0.736 | 0.771 | 0.724 | 0.866 | 0.782 | 0.876 | 0.836 | 0.915 | 0.460 | 0.611 | 0.768 | 0.460 |
| carbon_ml_emb | 0.970 | 0.889 | 0.817 | 0.735 | 0.759 | 0.708 | 0.853 | 0.780 | 0.864 | 0.832 | 0.894 | 0.559 | 0.616 | 0.764 | 0.559 |
| lang_carbon | 0.962 | 0.898 | 0.823 | 0.738 | 0.773 | 0.685 | 0.855 | 0.767 | 0.852 | 0.815 | 0.900 | 0.534 | 0.601 | 0.750 | 0.534 |
| random | 0.917 | 0.789 | 0.659 | 0.528 | 0.573 | 0.592 | 0.736 | 0.725 | 0.771 | 0.693 | 0.741 | 0.413 | 0.507 | 0.613 | 0.413 |
| smallest | 0.827 | 0.493 | 0.453 | 0.293 | 0.373 | 0.413 | 0.507 | 0.413 | 0.547 | 0.427 | 0.507 | 0.320 | 0.347 | 0.360 | 0.293 |
| largest | 0.987 | 0.920 | 0.880 | 0.773 | 0.800 | 0.747 | 0.907 | 0.813 | 0.880 | 0.893 | 0.960 | 0.600 | 0.627 | 0.787 | 0.600 |
| best_fixed | 0.987 | 0.920 | 0.880 | 0.773 | 0.800 | 0.747 | 0.907 | 0.813 | 0.880 | 0.893 | 0.960 | 0.600 | 0.627 | 0.787 | 0.600 |
| oracle | 1.000 | 0.987 | 0.920 | 0.920 | 0.920 | 0.933 | 0.987 | 0.907 | 0.960 | 0.933 | 0.987 | 0.787 | 0.827 | 0.933 | 0.787 |

## FR

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.731 | 0.496 | 0.576 | 53.612 |
| energy_pq | 0.763 | 0.549 | 0.708 | 66.551 |
| carbon | 0.821 | 0.595 | 1.003 | 95.705 |
| carbon_no_flesch | 0.821 | 0.589 | 0.918 | 86.061 |
| carbon_en_emb | 0.808 | 0.563 | 0.904 | 88.072 |
| carbon_onehot | 0.805 | 0.488 | 0.885 | 86.114 |
| carbon_ml_emb | 0.809 | 0.584 | 0.949 | 91.240 |
| lang_carbon | 0.810 | 0.568 | 0.909 | 88.131 |
| random | 0.661 | 0.413 | 0.578 | 55.549 |
| smallest | 0.449 | 0.293 | 0.247 | 23.741 |
| largest | 0.827 | 0.600 | 0.879 | 84.600 |
| best_fixed | 0.827 | 0.600 | 0.879 | 84.600 |
| oracle | 0.929 | 0.787 | 0.312 | 29.985 |

## SE-SE3

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.731 | 0.496 | 0.316 | 53.612 |
| energy_pq | 0.763 | 0.549 | 0.388 | 66.551 |
| carbon | 0.820 | 0.589 | 0.568 | 97.301 |
| carbon_no_flesch | 0.821 | 0.589 | 0.507 | 86.061 |
| carbon_en_emb | 0.802 | 0.565 | 0.521 | 87.946 |
| carbon_onehot | 0.805 | 0.488 | 0.502 | 85.050 |
| carbon_ml_emb | 0.805 | 0.576 | 0.528 | 90.192 |
| lang_carbon | 0.804 | 0.536 | 0.521 | 88.114 |
| random | 0.661 | 0.413 | 0.328 | 55.549 |
| smallest | 0.449 | 0.293 | 0.140 | 23.741 |
| largest | 0.827 | 0.600 | 0.500 | 84.600 |
| best_fixed | 0.827 | 0.600 | 0.500 | 84.600 |
| oracle | 0.929 | 0.787 | 0.177 | 29.985 |

## DE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.731 | 0.496 | 6.696 | 53.612 |
| energy_pq | 0.763 | 0.549 | 8.395 | 66.551 |
| carbon | 0.794 | 0.565 | 9.735 | 78.109 |
| carbon_no_flesch | 0.791 | 0.531 | 10.286 | 80.696 |
| carbon_en_emb | 0.786 | 0.563 | 9.252 | 73.330 |
| carbon_onehot | 0.773 | 0.464 | 8.319 | 67.889 |
| carbon_ml_emb | 0.792 | 0.547 | 9.666 | 76.842 |
| lang_carbon | 0.774 | 0.528 | 9.647 | 76.629 |
| random | 0.661 | 0.413 | 6.925 | 55.549 |
| smallest | 0.449 | 0.293 | 2.960 | 23.741 |
| largest | 0.827 | 0.600 | 10.546 | 84.600 |
| best_fixed | 0.827 | 0.600 | 10.546 | 84.600 |
| oracle | 0.929 | 0.787 | 3.738 | 29.985 |

## US-CAL-CISO

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.731 | 0.496 | 3.742 | 53.612 |
| energy_pq | 0.763 | 0.549 | 4.796 | 66.551 |
| carbon | 0.796 | 0.547 | 5.671 | 79.755 |
| carbon_no_flesch | 0.798 | 0.549 | 5.975 | 86.094 |
| carbon_en_emb | 0.798 | 0.533 | 6.052 | 83.670 |
| carbon_onehot | 0.805 | 0.475 | 6.076 | 85.296 |
| carbon_ml_emb | 0.805 | 0.584 | 6.193 | 84.038 |
| lang_carbon | 0.807 | 0.568 | 6.067 | 85.142 |
| random | 0.661 | 0.413 | 3.990 | 55.549 |
| smallest | 0.449 | 0.293 | 1.705 | 23.741 |
| largest | 0.827 | 0.600 | 6.080 | 84.600 |
| best_fixed | 0.827 | 0.600 | 6.080 | 84.600 |
| oracle | 0.929 | 0.787 | 2.155 | 29.985 |

## US-NE-ISNE

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.731 | 0.496 | 4.578 | 53.612 |
| energy_pq | 0.763 | 0.549 | 5.631 | 66.551 |
| carbon | 0.801 | 0.589 | 7.110 | 83.331 |
| carbon_no_flesch | 0.783 | 0.531 | 6.466 | 76.062 |
| carbon_en_emb | 0.792 | 0.520 | 6.939 | 81.688 |
| carbon_onehot | 0.808 | 0.448 | 7.199 | 84.902 |
| carbon_ml_emb | 0.801 | 0.589 | 7.074 | 83.114 |
| lang_carbon | 0.779 | 0.528 | 6.701 | 78.786 |
| random | 0.661 | 0.413 | 4.725 | 55.549 |
| smallest | 0.449 | 0.293 | 2.021 | 23.741 |
| largest | 0.827 | 0.600 | 7.200 | 84.600 |
| best_fixed | 0.827 | 0.600 | 7.200 | 84.600 |
| oracle | 0.929 | 0.787 | 2.552 | 29.985 |

## PL

| strategy | accuracy | worst_language_acc | carbon_g_per_1k | energy_j |
|---|---|---|---|---|
| greenserv | 0.731 | 0.496 | 10.268 | 53.612 |
| energy_pq | 0.763 | 0.549 | 12.998 | 66.551 |
| carbon | 0.752 | 0.485 | 12.244 | 64.972 |
| carbon_no_flesch | 0.773 | 0.533 | 13.664 | 69.226 |
| carbon_en_emb | 0.703 | 0.432 | 11.104 | 57.045 |
| carbon_onehot | 0.729 | 0.373 | 11.434 | 59.158 |
| carbon_ml_emb | 0.719 | 0.469 | 11.503 | 58.791 |
| lang_carbon | 0.719 | 0.445 | 11.865 | 60.860 |
| random | 0.661 | 0.413 | 10.744 | 55.549 |
| smallest | 0.449 | 0.293 | 4.591 | 23.741 |
| largest | 0.827 | 0.600 | 16.355 | 84.600 |
| best_fixed | 0.827 | 0.600 | 16.355 | 84.600 |
| oracle | 0.929 | 0.787 | 5.798 | 29.985 |
