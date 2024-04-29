from datasets import load_dataset
from typing import Generator as Gen

from .base_benchmark import BaseBenchmark

class NaturalQuestionsBenchmark(BaseBenchmark):
    BM_NAME = 'NQ_Open'

    def __init__(self, bm_config: dict):
        dataset = load_dataset('nq_open')
        self._dataset = dataset['validation']
        self._training_data = dataset['train']
        super().__init__(bm_config)

    @property
    def sample_generator(self) -> Gen[tuple[str, list[str], dict], None, None]:
        for i in self._shuffled_indices:
            row = self._dataset[int(i)]
            yield row['question'], row['answer'], {}

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
            yield row['question'], row['answer'][0]

    @property
    def dataset_len(self) -> int:
        return len(self._dataset)
