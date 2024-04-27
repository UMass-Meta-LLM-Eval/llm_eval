"""Evaluation suite for LLMs on Core-Knowledge tasks."""

__version__ = '1.5.2'
"""Version number of the package."""

from .benchmark import create_benchmark
from .evaluator import create_evaluator
from .model import create_model
