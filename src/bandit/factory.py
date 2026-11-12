# src/bandit/factory.py
import logging

from src.bandit.epsilon_greedy import (
    ContextualEpsilonGreedy,
    EpsilonGreedy,
    LinearEpsilonGreedy,
)
from src.bandit.linucb import LinUCB
from src.bandit.thompson_sampling import ThompsonSampling

logger = logging.getLogger(__name__)


def create_bandit_instance(
    algo_name: str,
    algo_params: dict,
    model_ids: list,
    context_dimension: int,
    reg_lambda: float,
    seed: int,
):
    """
    Factory function to create a bandit instance based on configuration.

    Args:
        algo_name (str): Name of the algorithm (e.g., 'linear_epsilon_greedy').
        algo_params (dict): Dictionary of parameters specific to the algorithm.
        model_ids (list): List of model IDs (arms).
        context_dimension (int): The context dimension required for this instance.
        reg_lambda (float): Regularization lambda (used by linear models).
        seed (int): Random seed for the run.

    Returns:
        An initialized bandit instance (subclass of BaseBandit) or None if error.
    """

    algo_name_lower = algo_name.lower()
    logger.debug(
        f"Attempting to create bandit: {algo_name_lower} with params: {algo_params}, dim: {context_dimension}, lambda: {reg_lambda}, seed: {seed}"
    )

    try:
        if algo_name_lower == "linear_epsilon_greedy":
            return LinearEpsilonGreedy(
                model_ids=model_ids,
                context_dimension=context_dimension,
                initial_epsilon=algo_params["initial_epsilon"],
                decay_factor=algo_params["decay_factor"],
                min_epsilon=algo_params["min_epsilon"],
                lambda_=reg_lambda,
                seed=seed,
            )
        elif algo_name_lower == "contextual_epsilon_greedy":

            return ContextualEpsilonGreedy(
                model_ids=model_ids,
                context_dimension=context_dimension,
                initial_epsilon=algo_params["initial_epsilon"],
                decay_factor=algo_params["decay_factor"],
                min_epsilon=algo_params["min_epsilon"],
                seed=seed,
            )
        elif algo_name_lower == "epsilon_greedy":
            return EpsilonGreedy(
                model_ids=model_ids,
                initial_epsilon=algo_params["initial_epsilon"],
                decay_factor=algo_params["decay_factor"],
                min_epsilon=algo_params["min_epsilon"],
                seed=seed,
            )
        elif algo_name_lower == "linucb":
            return LinUCB(
                model_ids=model_ids,
                context_dimension=context_dimension,
                alpha=algo_params["alpha"],
                regularization=algo_params["regularization"],
                seed=seed,
            )
        elif algo_name_lower == "thompson_sampling":
            return ThompsonSampling(
                model_ids=model_ids,
                context_dimension=context_dimension,
                sigma=algo_params["sigma"],
                prior_variance=algo_params["prior_variance"],
                seed=seed,
            )
        else:
            logger.error(f"Unsupported algorithm name: {algo_name}")
            return None
    except KeyError as e:
        logger.error(
            f"Missing required parameter '{e}' for algorithm '{algo_name}' in config."
        )
        return None
    except Exception as e:
        logger.error(f"Error creating bandit instance {algo_name}: {e}", exc_info=True)
        return None
