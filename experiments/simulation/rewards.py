"""Reward and cost functions shared by every router in experiments/run.py."""
import numpy as np
import pandas as pd


def energy_cost(row, ci, ctx):
    """GreenServ cost: normalized energy per token (ignores grid intensity)."""
    return row["energy_per_token_norm"]


def energy_per_query_cost(row, ci, ctx):
    """Normalized energy per query (ignores grid intensity)."""
    return row["energy_consumption_norm"]


def carbon_cost(row, ci, ctx):
    """Normalized carbon per query; ctx["carbon_normalizer"] is a CarbonNormalizer."""
    return ctx["carbon_normalizer"].cost(row["energy_consumption"], ci, row["dataset"])


def carbon_per_token_cost(row, ci, ctx):
    """Normalized carbon per token: GreenServ's per-token cost unit, priced at the current grid."""
    return ctx["carbon_normalizer"].cost(row["energy_per_token"], ci, row["dataset"], "energy_per_token")


# Keys match `cost:` in config/routers.yaml
COST_FUNCTIONS = {
    "energy_per_token": energy_cost,
    "energy": energy_per_query_cost,
    "carbon": carbon_cost,
    "carbon_per_token": carbon_per_token_cost,
}


def calculate_reward(
    accuracy_norm: float, cost_norm: float, lambda_weight: float
) -> float:
    """Calculate reward based on normalized accuracy and cost.

    Args:
        accuracy_norm (float): Normalized accuracy (0 to 1).
        cost_norm (float): Normalized energy or carbon (0 to 1, where 0 is best); user designates which cost is used.
        lambda_weight (float): Weight for cost efficiency (0 to 1).

    Returns:
        float: Calculated reward (0 to 1), or NaN if inputs are NaN.
    """
    if pd.isna(accuracy_norm) or pd.isna(cost_norm):
        return np.nan
    cost_efficiency_norm = 1.0 - cost_norm
    reward = (
        1.0 - lambda_weight
    ) * accuracy_norm + lambda_weight * cost_efficiency_norm
    return max(0.0, min(1.0, reward))
