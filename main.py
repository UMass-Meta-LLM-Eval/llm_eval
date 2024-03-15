from argparse import ArgumentParser
from itertools import product
import json
import os
import sys
from dotenv import load_dotenv
loaded = load_dotenv()
if not loaded:
    print('No .env file found')
    sys.exit(1)

from src.benchmark import create_benchmark
from src.database import BaseDatabase, JSONDatabase, MongoDB
from src.evaluator import create_evaluator
from src.helpers import InfoDoc
from src.model import create_model


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
            model_hash = InfoDoc(**model_cfg).doc_id
            results = benchmark.compute_results(model_hash, db, evaluator)
            print(results)


def inspect(db: BaseDatabase, config: dict):
    for (bm_cfg, model_cfg) in product(config['benchmarks'], config['models']):
        benchmark = create_benchmark(bm_cfg)
        model_hash = InfoDoc(**model_cfg).doc_id
        benchmark.inspect_results(db, model_hash)

def init_db(config: dict):
    if 'db' not in config:
        return JSONDatabase('json_db', 'data/')
    return MongoDB(config['db']['env'], config['db']['uri'])

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
    # db = JSONDatabase('json_db', 'data/')
    db = MongoDB({'uri': os.getenv('MONGODB_URI')})

    # Run the benchmark
    if args.benchmark_config:
        with open(f'configs/{args.benchmark_config}.json') as f:
            bm_config = json.load(f)
        benchmark(db, bm_config)
        print('Benchmarking Complete')
    else:
        print('Benchmarking Skipped')

    # Evaluate the results
    if args.eval_config:
        with open(f'configs/{args.eval_config}.json') as f:
            eval_config = json.load(f)
        evaluate(db, eval_config)
        print('Evaluation Complete')
    else:
        print('Evaluation Skipped')

    # Inspect the results
    if args.inspect_config:
        with open(f'configs/{args.inspect_config}.json') as f:
            inspect_config = json.load(f)
        inspect(db, inspect_config)
        print('Inspect Complete')
    else:
        print('Inspect Skipped')


if __name__ == '__main__':
    main()
