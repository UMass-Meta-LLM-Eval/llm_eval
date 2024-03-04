"""Wrappers for the benchmarks."""

from .base_benchmark import BaseBenchmark, DummyBenchmark
from .mmlu import MMLUBenchmark
from .naturalquestions import NaturalQuestionsBenchmark, DummyNQBenchmark

classes = {
    'DummyBenchmark': DummyBenchmark,
    'MMLUBenchmark': MMLUBenchmark,
    'NaturalQuestionsBenchmark' : NaturalQuestionsBenchmark,
    'DummyNQBenchmark': DummyNQBenchmark,
    # Add new benchmarks here
}

def create_benchmark(bm_config: dict) -> BaseBenchmark:
    bm_cls = classes[bm_config['cls']]
    return bm_cls(bm_config)
