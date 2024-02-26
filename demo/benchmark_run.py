from itertools import product
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.benchmark import create_benchmark
from src.model import create_model
from src.database import JSONDatabase


def main():
    with open('demo/benchmark_info.json') as f:
        run_info = json.load(f)

    db = JSONDatabase('test_db', 'data/')
    for (bm_cfg, model_cfg) in product(run_info['benchmarks'], run_info['models']):
        benchmark = create_benchmark(bm_cfg)
        model = create_model(model_cfg)
        benchmark.run(model, db)


if __name__ == '__main__':
    main()
