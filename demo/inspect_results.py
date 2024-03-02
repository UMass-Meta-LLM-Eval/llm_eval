from itertools import product
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.benchmark import create_benchmark
from src.database import JSONDatabase, DummyMongoDB
from src.evaluator import create_evaluator


def main():
    with open('demo/eval_info.json') as f:
        run_info = json.load(f)

    db = JSONDatabase('test_db', 'data/')
    # db = DummyMongoDB('dummy_db', {})
    if 'evaluator' in run_info:
        evaluators = [run_info['evaluator']]
    else:
        evaluators = run_info['evaluators']
    for (bm_cfg, model_cfg) in product(run_info['benchmarks'], run_info['models']):
        benchmark = create_benchmark(bm_cfg)
        benchmark.inspect_results(db, model_cfg)


if __name__ == '__main__':
    main()
