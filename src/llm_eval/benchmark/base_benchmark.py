from abc import ABC, abstractmethod
from typing import Generator as Gen

from numpy.random import Generator, PCG64
from tqdm import tqdm

from ..helpers import BenchmarkDoc, InfoDoc, templates
from ..helpers.constants.db import (DATASETS, BENCHMARK, METADATA, MODEL, 
                                    EVALUATOR)
from ..helpers.constants.logging import UPDATE
from ..helpers.logging.tqdm_to_logger import TqdmToLogger
from ..helpers.misc import truncate_response
from ..database import BaseDatabase
from ..evaluator import BaseEvaluator
from . import logger

class BaseBenchmark(ABC):
    def __init__(self, bm_config: dict):
        """Initialize the benchmark with the given configuration.

        The implementation should load the dataset and any other necessary
        resources after calling the `super()` method, or completely override
        this method, but keep the signature of this `__init__` method.
        
        In addition to the public properties, following attributes are
        available after initialization:
        - `_seed: int`: Seed for random number generator.
        - `_use_cache: bool`: Whether to use caching.
        - `_tqdm_file`: File to which tqdm writes progress.
        - `_num_fewshot: int`: Number of fewshot examples.
        - `_question_template: str`: Template for questions.
        - `_fewshot_template: str`: Template for fewshot examples.
        - `_fewshot: str`: Formatted fewshot examples.
        - `_shuffled_indices: list[int]`: Shuffled indices of samples.
        - `_template_name: str`: Name of the template used.
        """

        # Set the benchmark's configuration
        self._config = bm_config

        # Set the seed
        seed = self.config.get('seed')
        if seed is None:
            logger.warning('Seed not specified. Defaulting to 0.')
            seed = 0
        self._seed: int = seed

        # Set up other helpers and utilities
        self._use_cache: bool = self.config.get('use_cache', True)
        self._tqdm_file = TqdmToLogger(logger)

        # Load template
        template_name = self.config.get('template', '').upper()
        if template_name == '':
            logger.warning('Template name not specified. Defaulting to '
                           'BASE_SIMPLE.')
            template_name = 'BASE_SIMPLE'
        logger.log(UPDATE, 'Using template: %s', template_name)

        # Set up fewshot examples
        self._num_fewshot: int = self._config.get('num_fewshot')
        if self._num_fewshot is None:
            logger.warning('Fewshot examples not specified. Defaulting to 0.')
            self._num_fewshot = 0
        self._set_templates(template_name)
        self._fewshot = self._create_fewshot_examples()

        # Compute sample indices
        total, shuffled_indices = self._get_shuffled_indices(
            self._get_rng(self._seed), self.dataset_len)
        self._total_questions = total
        self._shuffled_indices = shuffled_indices

    def _get_rng(self, seed: int) -> Generator:
        """Utility method to get a random number generator with the given
        seed."""
        return Generator(PCG64(seed=seed))
    
    def _get_shuffled_indices(self, rng: Generator, dataset_len: int
                              ) -> tuple[int, list[int]]:
        """Utility method to get the total number of samples and a
        shuffled list of indices (deterministic given the seed) for the
        dataset."""
        if 'num_samples' in self.config:
            total = self.config['num_samples']
            logger.info('Running benchmark on a %d sample subset.', total)
            shuffled_indices = rng.permutation(dataset_len)[:total].tolist()
        else:
            logger.info('Running benchmark on the full dataset.')
            total = dataset_len
            shuffled_indices = range(total)

        return total, shuffled_indices
        
    def _set_templates(self, template_name: str):
        """Set the question and fewshot templates for the benchmark."""
        self._template_name = template_name
        template_cls = getattr(templates, template_name)
        if self._num_fewshot > 0:
            self._question_template: str = template_cls.QUESTION
        elif hasattr(template_cls, 'QUESTION_ZERO_SHOT'):
            self._question_template: str = template_cls.QUESTION_ZERO_SHOT
        else:
            logger.warning('Zero-shot template for "%s"  not found. Creating '
                           'prompts with fewshot template. This may lead to '
                           'unexpected results.', template_name)
            self._question_template: str = template_cls.QUESTION
        self._fewshot_template: str = template_cls.FEWSHOT

    def _get_doc_from_db(self, db: BaseDatabase, bm_name, key) -> BenchmarkDoc:
        """Get a BenchmarkDoc from the database."""
        doc = db.get_doc(BENCHMARK, bm_name, key)
        return BenchmarkDoc.from_json(doc)

    def _create_fewshot_examples(self) -> str:
        """Create fewshot examples for the benchmark."""
        fewshot = ''
        for (question, answer) in self.fewshot_generator:
            fewshot += self._fewshot_template.format(
                question=question, answer=answer)
        return fewshot

    def _create_prompt(self, question: str, **kwargs):
        """Create a prompt for the given question. The can be used to format
        the question in a way that the model can understand, adding context or
        few-shot learning examples."""
        return self._question_template.format(question=question,
                                              fewshot=self._fewshot)
    
    def _parse_response(self, response: str, config: dict) -> str:
        """Parse the model's response to the question. This method should
        extract the answer from the model's response, which will then be
        sent to the evaluator."""
        return truncate_response(config, response)
    
    def _validate_num_fewshot(self, num_fewshot: int, n_train: int) -> int:
        """Validate the number of fewshot examples."""
        if num_fewshot > n_train:
            logger.warning('Fewshot number (%d) is greater than training data '
                           'size (%d). Setting fewshot number to %d.',
                           num_fewshot, n_train, n_train)
            num_fewshot = n_train
        return num_fewshot

    def run(self, model, db: BaseDatabase):
        """Run the benchmark with the given model configuration and store the
        results in the given database."""
        
        # Set up the benchmark run
        db.add_doc(METADATA, BENCHMARK, self.hashval,
                   self.doc.to_json())
        db.add_doc(METADATA, MODEL, model.hashval, model.config)

        # If model is a chat model, check if a chat template is used
        model_is_chat = model.config.get('chat', False)
        template_is_chat = self._template_name.lower().startswith('chat')
        if model_is_chat and not template_is_chat:
            logger.warning('The model is a chat model but the template %s '
                           'is not a chat template. This may lead to '
                           'unexpected results.', self._template_name)

        # Run the benchmark
        pbar = tqdm(self.sample_generator, total=self.total_questions,
                    file=self._tqdm_file, mininterval=60,
                    desc=f'Benchmarking {self.BM_NAME}')

        for (question, acceptable_answers) in pbar:
            
            # Create a prompt for the question
            prompt = self._create_prompt(question)

            # Store the question in the database (if it doesn't exist already)
            question_doc = InfoDoc(question=question,
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

            # Otherwise make model prediction and store in the database
            prediction = model.predict(prompt)
            doc.response = prediction
            db.add_doc(BENCHMARK, self.BM_NAME, doc.doc_id, doc.to_json())

    def compute_results(self, model_hash: str, db: BaseDatabase,
                        evaluator: BaseEvaluator) -> float:
        """Compute the results of the benchmark using the given evaluator that
        will judge if the model's predictions are correct. The results will be
        stored in the given database."""

        # Set up the evaluator run
        db.add_doc(METADATA, EVALUATOR, evaluator.hashval, evaluator.config)
        correct = 0

        # Run the evaluation
        pbar = tqdm(self.sample_generator, total=self.total_questions,
                    file=self._tqdm_file, mininterval=60,
                    desc=f'Evaluating {self.BM_NAME}')

        for (question, acceptable_answers) in pbar:

            # Create the prompt
            prompt = self._create_prompt(question)

            # Get the model's prediction and evaluate it
            question_hash = InfoDoc(
                question=question, references=acceptable_answers).doc_id
            key = BenchmarkDoc(self.hashval, model_hash, question_hash,
                               prompt).doc_id
            doc = self._get_doc_from_db(db, self.BM_NAME, key)
            prediction = self._parse_response(doc.response, evaluator.config)

            # If eval caching is enabled and evaluation already exists, skip
            if evaluator.config.get('use_cache', True) \
                    and evaluator.hashval in doc.evaluation:
                result = doc.evaluation[evaluator.hashval]['result']

            # Otherwise, evaluate the prediction and store the result
            else:
                result, info = evaluator.evaluate(question, prediction,
                                                  acceptable_answers,
                                                  doc=doc, db=db,
                                                  bm_name=self.BM_NAME)
                if result is not None:
                    # Result can be None in case of Multi-Human Evaluator
                    # because it stores its results into the `info` dicts
                    # of other evals
                    db.update_doc(BENCHMARK, self.BM_NAME, key,
                                f'evaluation.{evaluator.hashval}',
                                {'result': result, 'info': info})

            # Update the evaluation statistics
            correct += 0 if result is None else int(result)

        # Return the final score
        return correct / self.total_questions

    def inspect_results(self, db: BaseDatabase, model_hash: str,
                        markdown: bool = False) -> None:
        """Inspect the results of the benchmark stored in the given database.
        """
        if markdown:
            pbar = tqdm(self.sample_generator,total=self.total_questions,
                        file=self._tqdm_file, mininterval=1,
                        desc=f'Inspecting {self.BM_NAME}')
        else:
            pbar = tqdm(self.sample_generator, total=self.total_questions,
                        desc=f'Inspecting {self.BM_NAME}')
        for (question, acceptable_answers) in pbar:
            # Create the prompt
            prompt = self._create_prompt(question)

            # Get the model prediction and evaluations
            question_hash = InfoDoc(
                question=question, references=acceptable_answers).doc_id
            key = BenchmarkDoc(self.hashval, model_hash, question_hash,
                               prompt).doc_id
            doc = self._get_doc_from_db(db, self.BM_NAME, key)

            # Inspect the result
            s = doc.inspect(db, markdown=markdown)
            if markdown:
                with open('inspect.md', 'a') as f:
                    f.write(s+'\n\n---\n\n')

            # Break if user quits in interactive mode
            if not markdown and input() == 'q':
                break

    @property
    def config(self) -> dict:
        """Return the benchmark's configuration."""
        return self._config

    @property
    def doc(self) -> InfoDoc:
        """Return the benchmark's config metadata as an InfoDoc."""
        return InfoDoc(**self.config)

    @property
    def hashval(self) -> str:
        """Return the SHA256 hash of the benchmark's configuration as a base64
        string."""
        return self.doc.doc_id

    @property
    def total_questions(self) -> int:
        """Total number of questions in the benchmark.
        
        This would be the number of samples if the benchmark is run on a
        subset of the dataset, otherwise it would be length of the dataset."""
        return self._total_questions

    @property
    @abstractmethod
    def dataset_len(self) -> int:
        """Total length of the dataset (not the number of samples)."""

    @property
    @abstractmethod
    def sample_generator(self) -> Gen[tuple[str, list[str]], None, None]:
        """Return a generator that yields samples from the benchmark."""

    @property
    @abstractmethod
    def fewshot_generator(self) -> Gen[tuple[str, str], None, None]:
        """Return a generator that yields fewshot examples from the
        benchmark."""


class DummyBenchmark(BaseBenchmark):
    ...