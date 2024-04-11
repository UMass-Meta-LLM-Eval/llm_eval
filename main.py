from argparse import ArgumentParser
from itertools import product
import json
import os
import sys
import logging
import logging.config
from datetime import datetime
from packaging import version as parse_version
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
from llm_eval.helpers.constants import logging as logging_constants
import torch
import os

# Create custom logging levels
logging.addLevelName(logging_constants.PROGRESS, 'PROGRESS')
logging.addLevelName(logging_constants.UPDATE, 'UPDATE')
logger = logging.getLogger('llm_eval')

def memory_stats():
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
        torch.cuda.empty_cache()
        memory_stats()


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
                          f'{results:.2f}')
        del evaluator
        torch.cuda.empty_cache()
        memory_stats()


def inspect(db: BaseDatabase, config: dict, markdown: bool):
    for (bm_cfg, model_cfg) in product(config['benchmarks'], config['models']):
        benchmark = create_benchmark(bm_cfg)
        model_hash = InfoDoc(**model_cfg).doc_id
        benchmark.inspect_results(db, model_hash, markdown=markdown)


def load_config(cfg_path) -> dict:
    with open(f'configs/{cfg_path}.json') as f:
        cfg = json.load(f)
    return cfg


def validate_config(cfg_path):
    cfg = load_config(cfg_path)

    version: str = cfg.get('metadata', {}).get('version')
    if version is None:
        logger.warning('No version specified in config file')
        return

    src_version = llm_eval.__version__
    
    ver_src = src_version.lstrip('v')
    ver_src_major = src_version.lstrip('v').split('.')[0]
    ver_cfg = version.lstrip('v')
    ver_cfg_major = version.lstrip('v').split('.')[0]

    valid = (ver_cfg_major == ver_src_major) and \
        (parse_version.parse(ver_src) >= parse_version.parse(ver_cfg))
    
    if not valid:
        logger.error(f'Config file version: "{version}" is incompatible '
                       f'with source version: "{src_version}". This can '
                       'lead to unexpected behavior.')
    else:
        logger.info(f'Config file version: "{version}" is compatible '
                    f'with source version: "{src_version}".')


def log_config(db, job_id, bm_cfg, eval_cfg):
    curr_dt_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S%z')
    doc = {
        'job_id': job_id,
        'status': 'running',
        'start_time': curr_dt_str,
        'current_time': curr_dt_str}
    if bm_cfg:
        benchmark = load_config(bm_cfg)
        benchmark['filename'] = bm_cfg
        doc['benchmark'] = benchmark
    if eval_cfg:
        evaluator = load_config(eval_cfg)
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
    parser.add_argument('-eb', '--eval-benchmark',
                        help='Config for both benchmark and evaluation')
    parser.add_argument('-be', '--benchmark-eval',
                        help='Config for both benchmark and evaluation')
    args = parser.parse_args()

    # Override benchmark and evaluation config if combined config is provided
    if args.eval_benchmark:
        args.benchmark_config = args.eval_benchmark
        args.eval_config = args.eval_benchmark
    if args.benchmark_eval:
        args.benchmark_config = args.benchmark_eval
        args.eval_config = args.benchmark_eval

    # Set up logging
    logging_config = load_logging_cfg('default')
    logging.config.dictConfig(logging_config)
    

    # Create the database
    # db = JSONDatabase('json_db', 'data/')
    db = MongoDB({'uri': os.getenv('MONGODB_URI')})

    # Create the job ID and log the job
    if args.job_id:
        job_id = f'BATCH_{args.job_id}'
    else:
        job_id = create_job_id()
    logger.info(f'Starting job: {job_id}')
    log_config(db, job_id, args.benchmark_config, args.eval_config)

    # Run the benchmark
    if args.benchmark_config:
        logger.info('Running benchmark')
        validate_config(args.benchmark_config)
        benchmark(db, load_config(args.benchmark_config))
    else:
        logger.info('No benchmark config provided. Skipped.')

    # Evaluate the results
    if args.eval_config:
        logger.info('Evaluating results')
        validate_config(args.eval_config)
        evaluate(db, load_config(args.eval_config))
    else:
        logger.info('No evaluation config provided. Skipped.')

    # Inspect the results
    if args.inspect_config:
        logger.info('Inspecting results')
        validate_config(args.inspect_config)
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
