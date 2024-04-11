from datasets import load_dataset
from numpy.random import Generator, PCG64
from tqdm import tqdm

from .base_benchmark import BaseBenchmark
from ..database import BaseDatabase
from ..evaluator import BaseEvaluator
from ..helpers import BenchmarkDoc, InfoDoc, NQAnswersHelper
from ..helpers.constants.db import (DATASETS, BENCHMARK, METADATA, MODEL, 
                                    EVALUATOR)
from ..helpers.logging import TqdmToLogger
from llm_eval.helpers.misc import truncate_response
from . import logger

class MMLUBenchmark(BaseBenchmark):
    BM_NAME = 'MMLU'
    FEWSHOT_TEMPLATE = 'Q: {question}\nA: {A}\nB: {B}\nC: {C}\nD: {D}\nAns: {answer}\n\n'
    QUESTION_TEMPLATE = 'Q: {question}\nA: {A}\nB: {B}\nC: {C}\nD: {D}\nAns:'

    SUBSETS = ['abstract_algebra', 'anatomy', 'astronomy', 'business_ethics',
               'clinical_knowledge', 'college_biology', 'college_chemistry',
               'college_computer_science', 'college_mathematics',
               'college_medicine', 'college_physics', 'computer_security',
               'conceptual_physics', 'econometrics', 'electrical_engineering',
               'elementary_mathematics', 'formal_logic', 'global_facts',
               'high_school_biology', 'high_school_chemistry',
               'high_school_computer_science', 'high_school_european_history',
               'high_school_geography', 'high_school_government_and_politics',
               'high_school_macroeconomics', 'high_school_mathematics',
               'high_school_microeconomics', 'high_school_physics',
               'high_school_psychology', 'high_school_statistics',
               'high_school_us_history', 'high_school_world_history',
               'human_aging', 'human_sexuality', 'international_law',
               'jurisprudence', 'logical_fallacies', 'machine_learning',
               'management', 'marketing', 'medical_genetics', 'miscellaneous',
               'moral_disputes', 'moral_scenarios', 'nutrition', 'philosophy',
               'prehistory', 'professional_accounting', 'professional_law',
               'professional_medicine', 'professional_psychology',
               'public_relations', 'security_studies', 'sociology',
               'us_foreign_policy', 'virology', 'world_religions']

    def __init__(self, bm_config:dict):
        self._config = bm_config
        self.SUBSETS = bm_config['subset'] if 'subset' in bm_config else self.SUBSETS
        self.bm_config = bm_config
        self._tqdm_file = TqdmToLogger(logger)
        self.training_data = []
        self.dataset = []
        self._doc = InfoDoc(**self.bm_config)
        self._use_cache = self._config.get('use_cache', True)

        #Load data from all subsets
        for subset in self.SUBSETS:
            self.dataset += load_dataset('lukaemon/mmlu', subset, split='test')
            self.training_data += load_dataset('lukaemon/mmlu', subset, split='validation')
       
        self._fewshot_prefix = self._create_fewshot_examples(self.bm_config.get('num_fewshot', 0))
        
    def _create_fewshot_examples(self, num_fewshot: int):
        rng = self._get_rng(self._config.get('seed', 0))
        fewshot_examples = []

        if num_fewshot > 0:
            fewshot_idxs = rng.choice(
                len(self.training_data),
                size=10*num_fewshot, replace=False).tolist()
        else:
            fewshot_idxs = []

        fewshot_examples = []
        i = 0
        for idx in fewshot_idxs:
            if i >= num_fewshot:
                break

            row = self.training_data[idx]
            answer = self._get_mmlu_single_answer(row)
            if answer:
                fewshot_examples.append((row['input'], answer, row['A'], row['B'], row['C'], row['D']))
                if len(fewshot_examples) == num_fewshot:
                    break

            i += 1

        # Warn if not enough few-shot examples are found
        if len(fewshot_examples) != num_fewshot:
            print(f'Warning: Fewshot examples requested: '
                  f'{num_fewshot}, but '
                  f'{len(fewshot_examples)} found.')

        # Generate the prompt from the few-shot examples
        prompt = ''
        for (q, ans, A, B, C, D) in fewshot_examples:
            prompt += self.FEWSHOT_TEMPLATE.format(question=q, answer=ans, A=A, B=B, C=C, D=D)

        return prompt
    
    def _get_rng(self, seed: int):
        return Generator(PCG64(seed=seed))
    
    def _process_response(self, config, response: str):
        return truncate_response(config, response)

    def create_prompt(self, question:int, **kwargs):
        prompt = self._fewshot_prefix + self.QUESTION_TEMPLATE.format(
            question=question, A=kwargs.get('A'), B=kwargs.get('B'), C=kwargs.get('C'), D=kwargs.get('D'))
        return prompt
    
    def _get_shuffled_indices(self, rng: Generator):
        if 'num_samples' in self._config:
            total = self._config['num_samples']
            shuffled_indices = rng.permutation(len(self.dataset)).tolist()
        else:
            total = len(self.dataset)
            shuffled_indices = range(total)

        return total, shuffled_indices

    def _get_mmlu_answer(self, row):
        return [row['target'], row[row['target']], row['target'] + ": " + row[row['target']]]

    def _get_mmlu_single_answer(self, row):
        return row['target'] + ": " + row[row['target']]

    def run(self, model, db:BaseDatabase):
        # Set up the benchmark run
        rng = self._get_rng(self._config.get('seed', 0))
        db.add_doc(METADATA, BENCHMARK, self._doc.doc_id,
                self._doc.to_json())
        db.add_doc(METADATA, MODEL, model.hashval, model.config)

        # Shuffle the dataset (if sampling)
        total, shuffled_indices = self._get_shuffled_indices(rng)

        num_fewshot = self._config.get('num_fewshot', 0)
        pbar = tqdm(total=total, desc=f'Benchmarking {self.BM_NAME}',
                    file=self._tqdm_file, mininterval=60)

        for i in shuffled_indices:
            row = self.dataset[i]
            question_text = row['input']
            prompt = self.create_prompt(question_text, A=row['A'], B=row['B'], C=row['C'], D=row['D'])
            #Acceptable Answer is the Option and the Value of the Option
            acceptable_answers = self._get_mmlu_answer(row)

            # Store the question in the database (if it doesn't exist already)
            question_doc = InfoDoc(
                question=question_text,
                references=acceptable_answers)
            if not db.doc_exists(DATASETS, BENCHMARK, question_doc.doc_id):
                db.add_doc(DATASETS, BENCHMARK, question_doc.doc_id,
                        question_doc.to_json())
            
            # If caching is enabled and document already exists, skip
            doc = BenchmarkDoc(self.hashval, model.hashval,
                            question_doc.doc_id, prompt)
            if self._use_cache and db.doc_exists(BENCHMARK,
                                                self.BM_NAME,
                                                doc.doc_id):
                continue
            
            prediction = model.predict(prompt)
            doc.response = prediction
            db.add_doc(BENCHMARK, self.BM_NAME, doc.doc_id,
                    doc.to_json())
            pbar.update(1)
            if pbar.n >= total:
                break
        pbar.close()

    def compute_results(self, model_hash: str, db: BaseDatabase,
                        evaluator: BaseEvaluator) -> float:
        rng = self._get_rng(self._config.get('seed', 0))
        db.add_doc(METADATA, EVALUATOR, evaluator.hashval, evaluator.config)
        checked = 0
        correct = 0

        # Shuffle the dataset (if sampling)
        total, shuffled_indices = self._get_shuffled_indices(rng)

        pbar = tqdm(total=total, desc=f'Evaluating {self.BM_NAME}',
                    file=self._tqdm_file, mininterval=60)

        for i in shuffled_indices:
            row = self.dataset[i]
            question_text = row['input']
            prompt = self.create_prompt(question_text, A=row['A'], B=row['B'], C=row['C'], D=row['D'])
            acceptable_answers = self._get_mmlu_answer(row)

            # Get the model's prediction and evaluate it
            question_hash = InfoDoc(
                question=question_text,
                references=acceptable_answers).doc_id
            key = BenchmarkDoc(self.hashval, model_hash, question_hash,
                            prompt).doc_id
            doc = self._get_doc_from_db(db, self.BM_NAME, key)
            prediction = self._process_response(evaluator.config, doc.response)

            # If caching is enabled and evaluation already exists, skip
            if evaluator.config.get('use_cache', True) \
                    and evaluator.hashval in doc.evaluation:
                result = doc.evaluation[evaluator.hashval]['result']

            # Otherwise, evaluate the prediction and store the result
            else:
                result, info = evaluator.evaluate(
                    question_text, prediction,
                    acceptable_answers)
                
                doc.evaluation[evaluator.hashval] = {'result': result,
                                                    'info': info}
                db.add_doc(BENCHMARK, self.BM_NAME, key, doc.to_json())

            checked += 1
            correct += int(result)
            pbar.update(1)
            if pbar.n >= total:
                break

        pbar.close()
        return correct / checked
    
    def inspect_results(self, db: BaseDatabase, model_hash: str,
                        markdown: bool=False):
        rng = self._get_rng(self._config.get('seed', 0))
        # Shuffle the dataset (if sampling)
        total, shuffled_indices = self._get_shuffled_indices(rng)

        if markdown:
            pbar = tqdm(total=total, desc=f'Inspecting {self.BM_NAME}',
                        file=self._tqdm_file, mininterval=1)
        else:
            pbar = tqdm(total=total, desc=f'Inspecting {self.BM_NAME}')

        n = 0
        for i in shuffled_indices:
            row = self.dataset[i]
            question_text = row['input']
            prompt = self.create_prompt(question_text, A=row['A'], B=row['B'], C=row['C'], D=row['D'])
            acceptable_answers = self._get_mmlu_answer(row)
            
            question_hash = InfoDoc(
                question=question_text,
                references=acceptable_answers).doc_id
            key = BenchmarkDoc(self.hashval, model_hash, question_hash,
                               prompt).doc_id
            doc = self._get_doc_from_db(db, self.BM_NAME, key)
            s = doc.inspect(db, markdown=markdown)
            if markdown:
                with open('inspect.md', 'a') as f:
                    f.write(s+'\n\n---\n\n')
            n += 1
            pbar.update(1)
            if n >= total:
                break
            if not markdown and input() == 'q':
                break

        pbar.close()

    @property
    def config(self):
        return self._config
    
    @property
    def hashval(self) -> str:
        return self._doc.doc_id
