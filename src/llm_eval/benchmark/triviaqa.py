from datasets import load_dataset
from typing import Generator as Gen

from .base_benchmark import BaseBenchmark
from ..helpers import find_acceptable_answers_triviaqa
from ..helpers.constants.logging import UPDATE
from . import logger

class TriviaQABenchmark(BaseBenchmark):
    BM_NAME = 'TriviaQA'

    def __init__(self, bm_config:dict):
        dataset = load_dataset('trivia_qa', bm_config['subset'])
        self._dataset = dataset['validation']
        self._training_data = dataset['train']
        super().__init__(bm_config)

    @property
    def sample_generator(self) -> Gen[tuple[str, list[str], dict], None, None]:
        generated = 0
        for i in self._shuffled_indices:
            # Stop if we have generated enough samples
            if generated >= self.total_questions:
                break

            # Create the question and references
            row = self._dataset[int(i)]
            acceptable_answers = find_acceptable_answers_triviaqa(row)
            extra = {'num_references': len(acceptable_answers)}

            # Skip this question if there are too many references
            if (self._max_references > 0) and \
                (len(acceptable_answers) > self._max_references):
                continue

            # Update the counter and yield the question-references-extras tuple
            generated += 1
            yield row['question'], acceptable_answers, extra

    @property
    def fewshot_generator(self) -> Gen[tuple[str, str], None, None]:
        n_train = len(self._training_data)
        n_fewshot = self._validate_num_fewshot(self._num_fewshot, n_train)

        indices = []
        if n_fewshot > 0:
            rng = self._get_rng(self._seed)
            indices = rng.choice(n_train, n_fewshot, replace=False)

        for i in indices:
            row = self._training_data[int(i)]
            yield row['question'], row['answer']['value']

    @property
    def dataset_len(self) -> int:
        return len(self._dataset)
