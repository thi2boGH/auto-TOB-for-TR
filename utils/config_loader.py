import yaml
import os


def load_config(file_path="config.yaml"):
    """Loads configuration from a YAML file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file '{file_path}' not found.")
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config