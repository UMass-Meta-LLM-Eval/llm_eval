from datasets import load_dataset
from typing import Generator as Gen

from .base_benchmark import BaseBenchmark

class MMLUBenchmark(BaseBenchmark):
    BM_NAME = 'MMLU'

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
        self.SUBSETS = bm_config.get('subsets', self.SUBSETS)
        self._dataset = []
        self._training_data = []

        # Load data from all subsets
        for subset in self.SUBSETS:
            ds = load_dataset('lukaemon/mmlu', subset, trust_remote_code=True)
            self._dataset += ds['test']
            self._training_data += ds['validation']

        super().__init__(bm_config)

    def _create_question(self, question_text: str, *options):
        labels = ['A', 'B', 'C', 'D']
        for (option, label) in zip(options, labels):
            question_text += f'\n{label}: {option}'
        return question_text

    def _get_acceptable_answers(self, row: dict) -> list[str]:
        label = row['target']
        option = row[label]
        return [label, option, f'{label}: {option}']

    @property
    def sample_generator(self) -> Gen[tuple[str, list[str], dict], None, None]:
        for i in self._shuffled_indices:
            row = self._dataset[int(i)]
            question = self._create_question(row['input'], row['A'], row['B'],
                                             row['C'], row['D'])
            acceptable_answers = self._get_acceptable_answers(row)
            yield question, acceptable_answers, {}

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
            question = self._create_question(row['input'], row['A'], row['B'],
                                             row['C'], row['D'])
            answer = self._get_acceptable_answers(row)[-1]
            yield question, answer

    @property
    def dataset_len(self) -> int:
        return len(self._dataset)
