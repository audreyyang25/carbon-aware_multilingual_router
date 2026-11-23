# config/manager.py
import os

import yaml

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config(name):
    """Load config/<name>.yaml, resolved relative to this file so it works from any working directory.

    Raises FileNotFoundError if the file doesn't exist; an empty file returns {}.
    """
    path = os.path.join(CONFIG_DIR, f"{name}.yaml")
    print(f"Loading config from {os.path.relpath(path)}")
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}
