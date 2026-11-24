# src/bandit/base.py
from abc import ABC, abstractmethod


class BaseBandit(ABC):
    """Base class for multi-armed bandit algorithms"""

    def __init__(self, model_ids, context_dimension=None):
        self.model_ids = list(model_ids)
        self.n_models = len(model_ids)
        self.context_dimension = context_dimension
        self._validate_init()

    def _validate_init(self):
        if not self.model_ids:
            raise ValueError("model_ids cannot be empty")
        if self.n_models <= 0:
            raise ValueError("Number of models must be positive")

    @abstractmethod
    def select_model(self, context=None):
        """Select a model based on current knowledge"""
        pass

    @abstractmethod
    def update(self, model_id, reward, context=None):
        """Update algorithm state based on observed reward"""
        pass

    # get_state / set_state / add_model: GreenServ leftovers, unused here. GreenServ's live routing
    # service saved bandits between requests and added models at run time; the simulation in
    # experiments/run.py builds a fresh bandit per run and never calls them. They stay abstract so
    # every bandit class keeps the same interface.
    @abstractmethod
    def get_state(self):
        """Get serializable state of the algorithm"""
        return {
            "model_ids": self.model_ids,
            "context_dimension": self.context_dimension,
        }

    @abstractmethod
    def set_state(self, state):
        """Restore algorithm state from serialized state"""
        self.model_ids = state.get("model_ids", self.model_ids)
        self.context_dimension = state.get("context_dimension", self.context_dimension)

    @abstractmethod
    def add_model(self, model_id):
        """Adds a new model (arm) to the bandit algorithm dynamically."""
        pass
