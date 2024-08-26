from datetime import datetime
import json
from packaging import version as parse_version

from . import logger


def load_config(cfg_path: str) -> dict:
    with open(f'configs/{cfg_path}.json') as f:
        cfg = json.load(f)
    return cfg


def validate_config(cfg_path: str, src_version: str):
    cfg = load_config(cfg_path)

    version: str = cfg.get('metadata', {}).get('version')
    if version is None:
        logger.warning('No version specified in config file')
        return

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
