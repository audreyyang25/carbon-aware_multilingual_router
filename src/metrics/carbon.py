J_PER_KWH = 3.6e6


def carbon_g(energy_j, intensity_g_per_kwh, pue=1.0):
    """Operational emissions (gCO2eq) for one query."""
    return energy_j / J_PER_KWH * pue * intensity_g_per_kwh


class CarbonNormalizer:
    """Per-dataset energy bounds x global grid-intensity bounds.

    energy_bounds has a `bounds` dict {dataset: {"energy_consumption": {min, max}}}, e.g. TrainBounds.
    """

    def __init__(self, ci_min, ci_max, energy_bounds, pue=1.0):
        self.ci_min = ci_min
        self.ci_max = ci_max
        self.pue = pue
        self.energy = energy_bounds

    def normalize(self, carbon, dataset):
        """Scale gCO2eq to [0, 1] using this dataset's energy range and the global CI range."""
        if dataset not in self.energy.bounds:
            raise KeyError(f"No energy bounds for dataset '{dataset}' in the training results")
        b = self.energy.bounds[dataset]["energy_consumption"]
        lo = carbon_g(b["min"], self.ci_min, self.pue)
        hi = carbon_g(b["max"], self.ci_max, self.pue)
        return min(1.0, max(0.0, (carbon - lo) / (hi - lo)))

    def cost(self, energy_j, intensity_g_per_kwh, dataset):
        """Normalized carbon cost for one query (0 = cleanest, 1 = dirtiest)."""
        return self.normalize(carbon_g(energy_j, intensity_g_per_kwh, self.pue), dataset)
