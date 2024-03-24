import json
import textwrap
from termcolor import colored

from .base_doc import BaseDoc
from ...database import BaseDatabase
from ...helpers.constants.db import (METADATA, MODEL, BENCHMARK, DATASETS,
                                     EVALUATOR)

class BenchmarkDoc(BaseDoc):
    def __init__(self, bm_hash: str, model_hash: str, question_hash: str,
                 prompt: str, response: str = None, evaluation: dict = None):
        self.bm_hash = bm_hash
        self.model_hash = model_hash
        self.question_hash = question_hash
        self.prompt = prompt
        self.response = response
        self.evaluation = {} if evaluation is None else evaluation

    @property
    def prompt_b64(self) -> str:
        return self.str_to_b64_str(self.prompt)
    
    @property
    def response_b64(self) -> str:
        return self.str_to_b64_str(self.response)
    
    def _encode(self) -> bytes:
        json_str = json.dumps({
            'benchmark': self.bm_hash,
            'model': self.model_hash,
            'question': self.question_hash,
            'prompt': self.prompt_b64})
        return json_str.encode(encoding='utf-8')

    def to_json(self):
        return {
            'benchmark': self.bm_hash,
            'model': self.model_hash,
            'question': self.question_hash,
            'prompt': self.prompt_b64,
            'response': self.response_b64,
            'evaluation': self.evaluation}

    @classmethod
    def from_json(cls, json_obj: dict):
        return cls(json_obj['benchmark'], json_obj['model'],
                   json_obj['question'],
                   cls.b64_str_to_str(json_obj['prompt']),
                   cls.b64_str_to_str(json_obj['response']),
                   json_obj.get('evaluation'))

    def inspect(self, db: BaseDatabase):
        benchmark_name = db.get_doc(METADATA, BENCHMARK, self.bm_hash)['name']
        model_name = db.get_doc(METADATA, MODEL, self.model_hash)['name']
        data = db.get_doc(DATASETS, BENCHMARK, self.question_hash)
        print(f'{colored("Benchmark", "red")} : {benchmark_name}')
        print(f'{colored("Model", "red")}     : {model_name}')
        print(f'{colored("Question", "red")}  : {data["question"]}')
        print(f'{colored("Prompt", "red")}    :')
        print(textwrap.indent(colored(self.prompt, 'blue'), ' '*2))
        print(f'{colored("References", "red")}:')
        for ref in data['references']:
            print(f'  {ref}')
        print(f'{colored("Response", "red")}  :')
        print(textwrap.indent(colored(self.response, 'green'), '  '))
        print(f'{colored("Evaluations", "red")}:')
        for eval_hash, result in self.evaluation.items():
            eval_name = db.get_doc(METADATA, EVALUATOR, eval_hash)['name']
            print(textwrap.indent(
                f'{eval_name}: {result["result"]}', ' '*2))
            if result['info'] != {}:
                eval_info = json.dumps(result['info'])
                print(textwrap.indent(eval_info, ' '*4))
        print()
