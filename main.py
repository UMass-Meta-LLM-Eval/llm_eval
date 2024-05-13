from argparse import ArgumentParser
from itertools import product
import gc
import os
import sys
import logging
import logging.config
from datetime import datetime

from dotenv import load_dotenv
loaded = load_dotenv()
if not loaded:
    print('No .env file found')
    sys.exit(1)

import llm_eval
from llm_eval import create_benchmark
from llm_eval import create_evaluator
from llm_eval import create_model
from llm_eval.database import BaseDatabase, JSONDatabase, MongoDB
from llm_eval.helpers import InfoDoc
from llm_eval.helpers.misc import (create_job_id, load_config, log_config,
                                   validate_config)
from llm_eval.helpers.logging import load_logging_cfg
from llm_eval.helpers.constants import logging as logging_constants
import torch
import os

# Create custom logging levels
logging.addLevelName(logging_constants.PROGRESS, 'PROGRESS')
logging.addLevelName(logging_constants.UPDATE, 'UPDATE')
logger = logging.getLogger('llm_eval')

def clear_gpu():
    torch.cuda.empty_cache()
    gc.collect()
    logger.info('GPU Allocated Memory: '
                f'{torch.cuda.memory_allocated()/1024**3:.2f} GB')


def benchmark(db: BaseDatabase, config: dict):
    for (bm_cfg, model_cfg) in product(config['benchmarks'], config['models']):
        logger.log(logging_constants.UPDATE, 'Running benchmark: '
                   f'{bm_cfg.get("name", "unknown")}')
        logger.info(f'Benchmark config: {bm_cfg}')
        benchmark = create_benchmark(bm_cfg)
        model = create_model(model_cfg)
        benchmark.run(model, db)
        logger.log(logging_constants.UPDATE, 'Completed benchmark run for '
                          f'benchmark `{bm_cfg.get("name", "unknown")}`, '
                          f'model `{model_cfg.get("name", "unknown")}`.')
        del model
        clear_gpu()


def evaluate(db: BaseDatabase, config: dict):
    if 'evaluator' in config:
        evaluators = [config['evaluator']]
    else:
        evaluators = config['evaluators']
    for evaluator_cfg in evaluators:
        logger.log(logging_constants.UPDATE, 'Running evaluator: '
                   f'{evaluator_cfg.get("name", "unknown")}')
        logger.info(f'Evaluator config: {evaluator_cfg}')
        evaluator = create_evaluator(evaluator_cfg)
        for (bm_cfg, model_cfg) in product(config['benchmarks'],
                                           config['models']):
            benchmark = create_benchmark(bm_cfg)
            model_hash = InfoDoc(**model_cfg).doc_id
            results = benchmark.compute_results(model_hash, db, evaluator)
            logger.log(logging_constants.UPDATE, 'Computed results for '
                          f'evaluator `{evaluator_cfg.get("name", "unknown")}`, '
                          f'benchmark `{bm_cfg.get("name", "unknown")}`, '
                          f'model `{model_cfg.get("name", "unknown")}`: '
                          f'{results*100:.2f}%')
        evaluator.exit()
        del evaluator
        clear_gpu()


def inspect(db: BaseDatabase, config: dict, markdown: bool):
    for (bm_cfg, model_cfg) in product(config['benchmarks'], config['models']):
        benchmark = create_benchmark(bm_cfg)
        model_hash = InfoDoc(**model_cfg).doc_id
        benchmark.inspect_results(db, model_hash, markdown=markdown)


def main():
    parser = ArgumentParser(description='Driver script for running jobs')
    parser.add_argument('-b', '--benchmark-config',
                        help='Path to benchmark config file')
    parser.add_argument('-e', '--eval-config',
                        help='Path to evaluation config file')
    parser.add_argument('-i', '--inspect-config',
                        help='Path to inspect config file')
    parser.add_argument('-j', '--job-id', help='Job ID')
    parser.add_argument('--markdown', action='store_true',
                        help='Save inspection results in markdown format')
    parser.add_argument('-eb', '--eval-benchmark',
                        help='Config for both benchmark and evaluation')
    parser.add_argument('-be', '--benchmark-eval',
                        help='Config for both benchmark and evaluation')
    parser.add_argument('--json-db', action='store_true',
                        help='Use JSON database instead of MongoDB')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Increase verbosity in interactive mode')
    args = parser.parse_args()

    # Override benchmark and evaluation config if combined config is provided
    if args.eval_benchmark:
        args.benchmark_config = args.eval_benchmark
        args.eval_config = args.eval_benchmark
    if args.benchmark_eval:
        args.benchmark_config = args.benchmark_eval
        args.eval_config = args.benchmark_eval

    # Create the job ID
    if args.job_id:
        job_id = f'BATCH_{args.job_id}'
        logging_type = 'batch'
    else:
        job_id = create_job_id()
        logging_type = 'interactive-verbose' if args.verbose else 'interactive'

    # Set up logging
    logging_config = load_logging_cfg(logging_type)
    logging.config.dictConfig(logging_config)
    logger.log(logging_constants.UPDATE, 'Logging with configuration: %s',
               logging_type)

    # Create the database
    if args.json_db:
        db = JSONDatabase('json_db', 'data/')
        logger.log(logging_constants.UPDATE, 'JSON database initialized')
    else:
        db = MongoDB({'uri': os.getenv('MONGODB_URI')})
        logger.log(logging_constants.UPDATE, 'MongoDB initialized')

    # Log the job start
    logger.info(f'Starting job: {job_id}')
    log_config(db, job_id, args.benchmark_config, args.eval_config)

    # Run the benchmark
    if args.benchmark_config:
        logger.info('Running benchmark')
        validate_config(args.benchmark_config, llm_eval.__version__)
        benchmark(db, load_config(args.benchmark_config))
    else:
        logger.info('No benchmark config provided. Skipped.')

    # Evaluate the results
    if args.eval_config:
        logger.info('Evaluating results')
        validate_config(args.eval_config, llm_eval.__version__)
        evaluate(db, load_config(args.eval_config))
    else:
        logger.info('No evaluation config provided. Skipped.')

    # Inspect the results
    if args.inspect_config:
        logger.info('Inspecting results')
        validate_config(args.inspect_config, llm_eval.__version__)
        inspect(db, load_config(args.inspect_config), args.markdown)
    else:
        logger.info('No inspect config provided. Skipped.')

    # Log the job completion
    logger.info(f'Job completed: {job_id}')
    db.update_doc_multi(
        'metadata', 'jobs', job_id, {
            'status': 'completed',
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S%z')})


if __name__ == '__main__':
    main()
