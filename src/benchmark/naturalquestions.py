from datasets import load_dataset
from numpy.random import Generator, PCG64

from .base_benchmark import BaseBenchmark
from ..database import BaseDatabase
from ..evaluator import BaseEvaluator
from ..helpers import BenchmarkDoc, InfoDoc, NQAnswersHelper
from ..helpers.constants.db import (DATASETS, BENCHMARK, METADATA, MODEL, 
                                    EVALUATOR)
from ..model import BaseModel
from tqdm import tqdm

class NaturalQuestionsBenchmark(BaseBenchmark):
    BM_NAME = 'naturalquestions'
    FEWSHOT_TEMPLATE = 'Q: {question}\nA: {answer}\n\n'
    QUESTION_TEMPLATE = 'Q: {question}\nA:'

    def __init__(self, bm_config: dict):
        self._config = bm_config
        self.nqhelper = NQAnswersHelper()
        self._dataset = load_dataset('natural_questions',
                                     trust_remote_code=True)
        self._fewshot_prefix = self._create_fewshot_examples(
            self._config.get('num_fewshot', 0))
        self._doc = InfoDoc(**bm_config)
        self._use_cache = self._config.get('use_cache', True)

    def _create_fewshot_examples(self, num_fewshot: int):
        rng = self._get_rng(self._config.get('seed', 0))

        if num_fewshot > 0:
            fewshot_idxs = rng.choice(
                len(self._dataset['train']),
                size=10*num_fewshot, replace=False).tolist()
        else:
            fewshot_idxs = []

        # Find fewshot examples with short answers from the training set
        fewshot_examples = []
        i = 0
        for idx in fewshot_idxs:
            if i >= num_fewshot:
                break

            row = self._dataset['train'][idx]
            answers = self.nqhelper.findAcceptableAnswersforNQ(row)
            if len(answers['short_answers']) == 0:
                continue

            fewshot_examples.append((row['question']['text'],
                                     answers['short_answers']))
            i += 1

        # Warn if not enough fewshot examples are found
        if len(fewshot_examples) != num_fewshot:
            print(f'Warning: Fewshot examples requested: '
                  f'{num_fewshot}, but '
                  f'{len(fewshot_examples)} found.')

        # Create the prompt prefix
        prompt = ''
        for (q, a) in fewshot_examples:
            prompt += self.FEWSHOT_TEMPLATE.format(question=q, answer=a[0])

        return prompt

    def _get_rng(self, seed: int):
        return Generator(PCG64(seed=seed))
    
    def _process_response(self, response: str):
        return response.split('\n')[0].strip()
    
    def _get_shuffled_indices(self, rng: Generator):
        if 'num_samples' in self._config:
            total = self._config['num_samples']
            shuffled_indices = rng.permutation(
                len(self._dataset['validation'])).tolist()
        else:
            total = len(self._dataset['validation'])
            shuffled_indices = range(total)

        return total, shuffled_indices

    def create_prompt(self, question:int, **kwargs):
        prompt = self._fewshot_prefix + self.QUESTION_TEMPLATE.format(
            question=question)

        return prompt

    def run(self, model, db: BaseDatabase):
        # Set up the benchmark run
        rng = self._get_rng(self._config.get('seed', 0))
        db.add_doc(METADATA, BENCHMARK, self._doc.doc_id,
                   self._doc.to_json())
        db.add_doc(METADATA, MODEL, model.hashval, model.config)

        # Shuffle the dataset (if sampling)
        total, shuffled_indices = self._get_shuffled_indices(rng)

        num_fewshot = self._config.get('num_fewshot', 0)
        pbar = tqdm(total=len(self._dataset['validation']))
        found_samples = 0
        for i in shuffled_indices:
            # Create the prompt and find acceptable answers
            row = self._dataset['validation'][i]
            prompt = self.create_prompt(row['question']['text'],
                                        num_fewshot=num_fewshot, rng=rng)
            acceptable_answers = self.nqhelper.findAcceptableAnswersforNQ(row)

            # Skip if no acceptable answers are found
            if len(acceptable_answers['short_answers']) == 0:
                pbar.update(1)
                continue

            # Store the question in the database (if it doesn't exist already)
            question_doc = InfoDoc(
                question=row['question']['text'],
                references=acceptable_answers['short_answers'])
            if not db.doc_exists(DATASETS, BENCHMARK, question_doc.doc_id):
                db.add_doc(DATASETS, BENCHMARK, question_doc.doc_id,
                           question_doc.to_json())
            
            # If caching is enabled and document already exists, skip
            doc = BenchmarkDoc(self.hashval, model.hashval,
                               question_doc.doc_id, prompt)
            if self._use_cache and db.doc_exists(BENCHMARK,
                                                 self.BM_NAME,
                                                 doc.doc_id):
                pbar.update(1)
                continue

            # Make model prediction and store in the database
            prediction = model.predict(prompt)
            doc.response = prediction
            db.add_doc(BENCHMARK, self.BM_NAME, doc.doc_id,
                       doc.to_json())

            # Next iteration
            pbar.update(1)
            found_samples += 1
            if found_samples >= total:
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

        num_fewshot = self._config.get('num_fewshot', 0)
        pbar = tqdm(total=total)
        for i in shuffled_indices:

            # Create the prompt and find acceptable answers
            row = self._dataset['validation'][i]
            prompt = self.create_prompt(row['question']['text'],
                                        num_fewshot=num_fewshot, rng=rng)
            acceptable_answers = self.nqhelper.findAcceptableAnswersforNQ(row)

            # Skip if no acceptable answers are found
            if len(acceptable_answers['short_answers']) == 0:
                continue
            
            # Get the model's prediction and evaluate it
            question_hash = InfoDoc(
                question=row['question']['text'],
                references=acceptable_answers['short_answers']).doc_id
            key = BenchmarkDoc(self.hashval, model_hash, question_hash,
                               prompt).doc_id
            doc = self._get_doc_from_db(db, self.BM_NAME, key)
            prediction = self._process_response(doc.response)

            # If caching is enabled and evaluation already exists, skip
            if evaluator.config.get('use_cache', True) \
                    and evaluator.hashval in doc.evaluation:
                result = doc.evaluation[evaluator.hashval]['result']

            # Otherwise, evaluate the prediction and store the result
            else:
                result, info = evaluator.evaluate(
                    row['question']['text'], prediction,
                    acceptable_answers['short_answers'])
                db.update_doc(BENCHMARK, self.BM_NAME, key, f'evaluation.{evaluator.hashval}', {'result': result, 'info': info})
            
            # Update the statistics and progress bar
            checked += 1
            correct += int(result)
            pbar.update(1)
            if pbar.n >= total:
                break

        pbar.close()
        return correct / checked

    def inspect_results(self, db: BaseDatabase, model_hash: str):
        rng = self._get_rng(self._config.get('seed', 0))

        # Shuffle the dataset (if sampling)
        total, shuffled_indices = self._get_shuffled_indices(rng)

        num_fewshot = self._config.get('num_fewshot', 0)
        n = 0
        for i in shuffled_indices:
            row = self._dataset['validation'][i]
            prompt = self.create_prompt(row['question']['text'],
                                        num_fewshot=num_fewshot, rng=rng)
            acceptable_answers = self.nqhelper.findAcceptableAnswersforNQ(row)
            if len(acceptable_answers['short_answers']) == 0:
                continue
            question_hash = InfoDoc(
                question=row['question']['text'],
                references=acceptable_answers['short_answers']).doc_id
            key = BenchmarkDoc(self.hashval, model_hash, question_hash,
                               prompt).doc_id
            doc = self._get_doc_from_db(db, self.BM_NAME, key)
            doc.inspect(db)
            n += 1
            if n >= total:
                break
            if input() == 'q':
                break

    @property
    def config(self):
        return self._config
    
    @property
    def hashval(self) -> str:
        return self._doc.doc_id


class DummyNQBenchmark(BaseBenchmark):
    BM_NAME = 'nq_dummy'
    def __init__(self, bm_config: dict):
        self._config = bm_config
        self._dataset = [{
            'question': 'When was the last time anyone was on the moon?',
            'references': ['14 December 1972 UTC', 'December 1972']}]
        self._doc = InfoDoc(**bm_config)
        self._use_cache = self._config.get('use_cache', True)

    def create_prompt(self, question, **kwargs):
        return f'Q. {question} A: '

    def run(self, model, db: BaseDatabase):
        db.add_doc(METADATA, BENCHMARK, self.hashval, self._doc.to_json())
        db.add_doc(METADATA, MODEL, model.hashval, model.config)
        for item in self._dataset:
            prompt = self.create_prompt(item['question'])

            # Store the question in the database (if it doesn't exist already)
            question_doc = InfoDoc(question=item['question'],
                                   references=item['references'])
            if not db.doc_exists(DATASETS, BENCHMARK, question_doc.doc_id):
                db.add_doc(DATASETS, BENCHMARK, question_doc.doc_id,
                           question_doc.to_json())

            # If caching is enabled and document already exists, skip
            doc = BenchmarkDoc(self.hashval, model.hashval,
                               question_doc.doc_id, prompt)
            if self._use_cache and db.doc_exists(BENCHMARK, self.BM_NAME,
                                                 doc.doc_id):
                continue

            # Make model prediction and store in the database
            prediction = model.predict(prompt)
            doc.response = prediction
            db.add_doc(BENCHMARK, self.BM_NAME, doc.doc_id, doc.to_json())

    def compute_results(self, model_hash: str, db: BaseDatabase,
                        evaluator: BaseEvaluator):
        db.add_doc(METADATA, EVALUATOR, evaluator.hashval, evaluator.config)
        checked = 0
        correct = 0
        for item in self._dataset:
            prompt = self.create_prompt(item['question'])

            # Get the model's prediction and evaluate it
            question_hash = InfoDoc(
                question=item['question'],
                references=item['references']).doc_id
            key = BenchmarkDoc(self.hashval, model_hash, question_hash,
                               prompt).doc_id
            doc = self._get_doc_from_db(db, self.BM_NAME, key)
            prediction = doc.response

            # If caching is enabled and evaluation already exists, skip
            if evaluator.config.get('use_cache', True) \
                    and evaluator.hashval in doc.evaluation:
                result = doc.evaluation[evaluator.hashval]['result']

            # Otherwise, evaluate the prediction and store the result
            else:
                result, info = evaluator.evaluate(
                    item['question'], prediction,
                    item['references'])
                
                doc.evaluation[evaluator.hashval] = {'result': result,
                                                     'info': info}
                db.add_doc('benchmark', self.BM_NAME, key, doc.to_json())

            # Update the statistics
            checked += 1
            correct += int(result)

        return correct / checked

    def inspect_results(self, db: BaseDatabase, model_hash: str):
        for item in self._dataset:
            prompt = self.create_prompt(item['question'])
            question_hash = InfoDoc(
                question=item['question'],
                references=item['references']).doc_id
            key = BenchmarkDoc(self.hashval, model_hash, question_hash,
                               prompt).doc_id
            doc = self._get_doc_from_db(db, self.BM_NAME, key)
            doc.inspect(db)
            if input() == 'q':
                break

    @property
    def config(self):
        return self._config
    
    @property
    def hashval(self) -> str:
        return self._doc.doc_id
