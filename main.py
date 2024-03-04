from argparse import ArgumentParser
from itertools import product
import json
import sys
from dotenv import load_dotenv
loaded = load_dotenv()
if not loaded:
    print('No .env file found')
    sys.exit(1)

from src.benchmark import create_benchmark
from src.database import BaseDatabase, JSONDatabase, MongoDB
from src.model import create_model
from src.evaluator import create_evaluator


def benchmark(db: BaseDatabase, config: dict):
    for (bm_cfg, model_cfg) in product(config['benchmarks'], config['models']):
        benchmark = create_benchmark(bm_cfg)
        model = create_model(model_cfg)
        benchmark.run(model, db)


def evaluate(db: BaseDatabase, config: dict):
    if 'evaluator' in config:
        evaluators = [config['evaluator']]
    else:
        evaluators = config['evaluators']
    for evaluator_cfg in evaluators:
        evaluator = create_evaluator(evaluator_cfg)
        for (bm_cfg, model_cfg) in product(config['benchmarks'],
                                           config['models']):
            benchmark = create_benchmark(bm_cfg)
            results = benchmark.compute_results(model_cfg, db, evaluator)
            print(results)


def inspect(db: BaseDatabase, config: dict):
    for (bm_cfg, model_cfg) in product(config['benchmarks'], config['models']):
        benchmark = create_benchmark(bm_cfg)
        benchmark.inspect_results(db, model_cfg)


def main():
    parser = ArgumentParser(description='Driver script for running jobs')
    parser.add_argument('-b', '--benchmark-config',
                        help='Path to benchmark config file')
    parser.add_argument('-e', '--eval-config',
                        help='Path to evaluation config file')
    parser.add_argument('-i', '--inspect-config',
                        help='Path to inspect config file')
    args = parser.parse_args()

    # Create the database
    db = JSONDatabase('json_db', 'data/')

    # Run the benchmark
    if args.benchmark_config:
        with open(f'configs/{args.benchmark_config}.json') as f:
            bm_config = json.load(f)
        benchmark(db, bm_config)

    # Evaluate the results
    if args.eval_config:
        with open(f'configs/{args.eval_config}.json') as f:
            eval_config = json.load(f)
        evaluate(db, eval_config)

    # Inspect the results
    if args.inspect_config:
        with open(f'configs/{args.inspect_config}.json') as f:
            inspect_config = json.load(f)
        inspect(db, inspect_config)


if __name__ == '__main__':
    main()
