"""Logging configuration files for the LLM evaluation package."""

import json
from pathlib import Path


def load_logging_cfg(cfg_name: str) -> dict:
    curr_dir = Path(__file__).parent
    cfg_path = curr_dir.joinpath(f'{cfg_name}.json')
    with open(cfg_path) as f:
        cfg = json.load(f)
    return cfg
