from argparse import ArgumentParser
from itertools import product
import json
import os
import sys
import logging
import logging.config
from datetime import datetime
from pkg_resources import parse_version
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
from llm_eval.helpers.misc import create_job_id
from llm_eval.helpers.logging import load_logging_cfg
import torch
import os

def memory_stats():
    print('GPU Allocated Memory - ', torch.cuda.memory_allocated()/1024**2)

def benchmark(db: BaseDatabase, config: dict):
    for (bm_cfg, model_cfg) in product(config['benchmarks'], config['models']):
        benchmark = create_benchmark(bm_cfg)
        model = create_model(model_cfg)
        benchmark.run(model, db)
        print('Benchmark Run complete - ', str(model_cfg))
        del model
        torch.cuda.empty_cache()
        memory_stats()


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
        print('Evaluator Run complete - ', str(evaluator_cfg))
        del evaluator
        torch.cuda.empty_cache()
        memory_stats()


def inspect(db: BaseDatabase, config: dict, markdown: bool):
    for (bm_cfg, model_cfg) in product(config['benchmarks'], config['models']):
        benchmark = create_benchmark(bm_cfg)
        model_hash = InfoDoc(**model_cfg).doc_id
        benchmark.inspect_results(db, model_hash)


def load_config(cfg_path, logger) -> dict:
    with open(f'configs/{cfg_path}.json') as f:
        cfg = json.load(f)
    version: str = cfg.get('metadata', {}).get('version')
    if version is None:
        logger.warning('No version specified in config file')
        return cfg

    src_version = llm_eval.__version__
    
    ver_src = src_version.lstrip('v')
    ver_src_major = src_version.lstrip('v').split('.')[0]
    ver_cfg = version.lstrip('v')
    ver_cfg_major = version.lstrip('v').split('.')[0]

    valid = (ver_cfg_major == ver_src_major) and \
        (parse_version(ver_src) >= parse_version(ver_cfg))
    
    if not valid:
        logger.warning(f'Config file version: "{version}" is incompatible '
                       f'with source version: "{src_version}". This can '
                       'lead to unexpected behavior.')
        
    return cfg


def log_config(db, job_id, bm_cfg, eval_cfg, logger):
    curr_dt_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S%z')
    doc = {
        'job_id': job_id,
        'status': 'running',
        'start_time': curr_dt_str,
        'current_time': curr_dt_str}
    if bm_cfg:
        benchmark = load_config(bm_cfg, logger)
        benchmark['filename'] = bm_cfg
        doc['benchmark'] = benchmark
    if eval_cfg:
        evaluator = load_config(eval_cfg, logger)
        evaluator['filename'] = eval_cfg
        doc['evaluator'] = evaluator
    db.add_doc('metadata', 'jobs', job_id, doc)


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
    args = parser.parse_args()

    # Set up logging
    logging_config = load_logging_cfg('default')
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger(__name__)

    # Create the database
    # db = JSONDatabase('json_db', 'data/')
    db = MongoDB({'uri': os.getenv('MONGODB_URI')})

    # Create the job ID and log the job
    if args.job_id:
        job_id = f'BATCH_{args.job_id}'
    else:
        job_id = create_job_id()
    logger.info(f'Starting job: {job_id}')
    log_config(db, job_id, args.benchmark_config, args.eval_config, logger)

    # Run the benchmark
    if args.benchmark_config:
        logger.info('Running benchmark')
        benchmark(db, load_config(args.benchmark_config, logger))
    else:
        logger.info('No benchmark config provided. Skipped.')

    # Evaluate the results
    if args.eval_config:
        logger.info('Evaluating results')
        evaluate(db, load_config(args.eval_config, logger))
    else:
        logger.info('No evaluation config provided. Skipped.')

    # Inspect the results
    if args.inspect_config:
        logger.info('Inspecting results')
        inspect(db, load_config(args.inspect_config, logger), args.markdown)
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
