import os
import json
from typing import Optional

DEFAULT_CONFIG_PATH = f"{os.path.expanduser('~')}/.local/share/k8s_walker"
DEFAULT_CONFIG = {}


def seed_config() -> str or None:
    if os.access(os.path.split(DEFAULT_CONFIG_PATH)[-1], os.W_OK | os.R_OK):
        with open(os.path.join(DEFAULT_CONFIG_PATH, 'config.json'), 'w') as config_file:
            json.dump(DEFAULT_CONFIG, config_file)
            return DEFAULT_CONFIG_PATH
    return None


def find_config(arg: Optional[str] = None) -> str:
    """Find the config file in the current directory and return the path to it."""

    def config_in_dir(dir_path: str) -> str or None:
        if not isinstance(dir_path, str):
            return None
        root, _, files = next(os.walk(dir_path))
        if 'config.json' in files:
            return os.path.join(root, 'config.json')

    possible_locations = [arg, DEFAULT_CONFIG_PATH, os.getcwd()]

    for location in possible_locations:
        try:
            if config_path := config_in_dir(location):
                return config_path
        except StopIteration:
            continue

    raise FileNotFoundError("No config.json found")


def read_config(config_path: str or None = None) -> dict:
    if config_path is None:
        config_path = find_config()
    with open(config_path, 'r') as config_file:
        return json.load(config_file)
