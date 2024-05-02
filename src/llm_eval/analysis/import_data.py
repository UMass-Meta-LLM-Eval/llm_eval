import pandas as pd
import numpy as np
import json
from sklearn.metrics import cohen_kappa_score
from tqdm import tqdm
from typing import Union

from .. import create_benchmark
from ..helpers import InfoDoc, BenchmarkDoc
from ..helpers.constants.db import METADATA, BENCHMARK, EVALUATOR
from ..helpers.misc import load_config
from . import logger


def _parse_as_list(s: Union[str, list], rtype = None) -> list:
    if isinstance(s, str):
        s = s.strip('"').strip("'")
        s = [col.strip() for col in s.split(',')]
    if rtype is not None:
        s = [rtype(col) for col in s]
    return s


def collect_results(cfg_path: str, bm_idxs: list[int] = None,
                    model_idxs: list[int] = None, save_prefix: str = None,
                    rm_cols: list = None, db = None, ret_as: str = 'csv',
                    human_cols_prefix: str = 'human', **kwargs) -> list[list]:
    cfg = load_config(cfg_path)
    bm_idxs = [0] if bm_idxs is None else _parse_as_list(bm_idxs, int)
    model_idxs = [0] if model_idxs is None else _parse_as_list(model_idxs, int)

    results = []
    for bm_idx in bm_idxs:
        this_results = []
        bm_cfg = cfg['benchmarks'][bm_idx]
        bm_name = bm_cfg.get('name', f'bm-{bm_idx}')
        benchmark = create_benchmark(bm_cfg)

        for model_idx in model_idxs:
            logger.info('Collecting results for benchmark: %d, model: %d',
                        bm_idx, model_idx)

            model_cfg = cfg['models'][model_idx]
            model_name = model_cfg.get('name', f'model-{model_idx}')

            if ret_as == 'csv':
                data = pd.DataFrame()
            elif ret_as == 'jsonl':
                data = []
            else:
                raise ValueError(f'Invalid return type: {ret_as}')
        
            model_hash = InfoDoc(**model_cfg).doc_id

            pbar = tqdm(benchmark.sample_generator,
                        total=benchmark.total_questions,
                        desc=f'Collecting results: {benchmark.BM_NAME}')
            for (question, references, _) in pbar:
                
                # Create the prompt
                prompt = benchmark._create_prompt(question)

                # Get the model prediction and evaluations
                question_hash = InfoDoc(
                    question=question, references=references).doc_id
                key = BenchmarkDoc(benchmark.hashval, model_hash, question_hash,
                                    prompt).doc_id
                doc = BenchmarkDoc.from_json(db.get_doc(BENCHMARK,
                                                        benchmark.BM_NAME, key))

                evals = {}
                for eval_hash, eval_data in doc.evaluation.items():
                    eval_name = db.get_doc(METADATA, EVALUATOR,
                                            eval_hash)['name']
                    if ret_as == 'csv':
                        # Add the results to the DataFrame
                        eval_bool = int(eval_data['result'])
                        if eval_name.startswith(human_cols_prefix):
                            valid = eval_data.get('confident', True)
                        else:
                            valid = eval_data.get('parsed_successfully', True)

                        if valid:
                            data.loc[key, eval_name] = 1 if eval_bool else -1
                        else:
                            data.loc[key, eval_name] = 0
                    else:
                        # Add the results to the list
                        evals[eval_name] = eval_data
                        data.append(evals)

            if rm_cols is not None:
                rm_cols = _parse_as_list(rm_cols)
                if ret_as == 'csv':
                    data = data.drop(columns=rm_cols, errors='ignore')
                else:
                    for d in data:
                        for col in rm_cols:
                            d.pop(col, None)

            if save_prefix is not None:
                save_loc = f'{save_prefix}_{bm_name}_{model_name}.{ret_as}'
                if ret_as == 'csv':
                    data.to_csv(save_loc)
                else:
                    with open(save_loc, 'w') as f:
                        for d in data:
                            f.write(json.dumps(d) + '\n')
            
            this_results.append(data)

        results.append(this_results)
        
    return results


def get_info_col(results: list[dict], col: str, **kwargs) -> pd.DataFrame:
    df = pd.DataFrame()
    for i, res in enumerate(results):
        for eval_name, eval_data in res.items():
            df[i, eval_name] = eval_data[col]
    return df


def get_kappa_matrix(results: pd.DataFrame, **kwargs)->pd.DataFrame:
    src = list(results.columns)
    trg = list(results.columns)
    matrix = np.zeros((len(src), len(trg))) - 1
    for i, s in enumerate(src):
        for j, t in enumerate(trg):
            try:
                matrix[i, j] = cohen_kappa_score(results[s], results[t])
            except ValueError:
                print(f'Could not compute score for {s} vs {t}, skipping.')
    return pd.DataFrame(matrix, index=results.columns, columns=results.columns)
