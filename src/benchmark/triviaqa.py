from datasets import load_dataset
from numpy.random import Generator, PCG64

from .base_benchmark import BaseBenchmark
from ..database import BaseDatabase
from ..evaluator import BaseEvaluator
from ..helpers import BenchmarkDoc, InfoDoc, TriviaQaAnswersHelper
from ..helpers.constants.db import (DATASETS, BENCHMARK, METADATA, MODEL, 
                                    EVALUATOR)
from ..model import BaseModel
from tqdm import tqdm

class TriviaQABenchmark(BaseBenchmark):
    BM_NAME = 'TriviaQA'
    FEWSHOT_TEMPLATE = 'Q: {question}\nA: {answer}\n\n'
    QUESTION_TEMPLATE = 'Q: {question}\nA:'

    def __init__(self, bm_config:dict):
        self._config = bm_config
        self.subset = bm_config['subset']
        self.dataset = load_dataset('trivia_qa', self.subset, split='validation')
        self.training_data = load_dataset('trivia_qa', self.subset, split='train')
        self._fewshot_prefix = self._create_fewshot_examples(bm_config.get('num_fewshot', 0))
        self._doc = InfoDoc(**bm_config)
        self._use_cache = self._config.get('use_cache', True)
        self.triviaQAhelper = TriviaQaAnswersHelper()
        
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
            answer = row['answer']['value']
            if answer:
                fewshot_examples.append((row['question'], answer))
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
        for (q, a) in fewshot_examples:
            prompt += self.FEWSHOT_TEMPLATE.format(question=q, answer=a)

        return prompt
    
    def _get_rng(self, seed: int):
        return Generator(PCG64(seed=seed))
    
    def _process_response(self, response: str):
        return response.split('\n')[0].strip()

    def create_prompt(self, question:int, **kwargs):
        prompt = self._fewshot_prefix + self.QUESTION_TEMPLATE.format(
            question=question)
        return prompt
    
    def _get_shuffled_indices(self, rng: Generator):
        if 'num_samples' in self._config:
            total = self._config['num_samples']
            shuffled_indices = rng.permutation(len(self.dataset)).tolist()
        else:
            total = len(self.dataset)
            shuffled_indices = range(total)

        return total, shuffled_indices
    
    def run(self, model, db:BaseDatabase):
        # Set up the benchmark run
        rng = self._get_rng(self._config.get('seed', 0))
        db.add_doc(METADATA, BENCHMARK, self._doc.doc_id,
                   self._doc.to_json())
        db.add_doc(METADATA, MODEL, model.hashval, model.config)

        # Shuffle the dataset (if sampling)
        total, shuffled_indices = self._get_shuffled_indices(rng)

        num_fewshot = self._config.get('num_fewshot', 0)
        pbar = tqdm(total=total, desc='Evaluating TriviaQA')

        for i in shuffled_indices:
            row = self.dataset[i]
            question_text = row['question']
            prompt = self.create_prompt(question_text)
            acceptable_answers = self.triviaQAhelper.findAcceptableAnswersforTriviaQA(row)

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

        pbar = tqdm(total=total, desc="Computing Results for TriviaQA")

        for i in shuffled_indices:
            row = self.dataset[i]
            question_text = row['question']
            prompt = self.create_prompt(question_text)
            acceptable_answers = self.triviaQAhelper.findAcceptableAnswersforTriviaQA(row)

            # Get the model's prediction and evaluate it
            question_hash = InfoDoc(
                question=question_text,
                references=acceptable_answers).doc_id
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
    
    def inspect_results(self, db: BaseDatabase, model_hash: str):
        rng = self._get_rng(self._config.get('seed', 0))
        # Shuffle the dataset (if sampling)
        total, shuffled_indices = self._get_shuffled_indices(rng)

        num_fewshot = self._config.get('num_fewshot', 0)
        n = 0
        for i in shuffled_indices:
            row = self.dataset[i]
            question_text = row['question']
            prompt = self.create_prompt(question_text)
            acceptable_answers = self.triviaQAhelper.findAcceptableAnswersforTriviaQA(row)
            
            question_hash = InfoDoc(
                question=question_text,
                references=acceptable_answers).doc_id
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