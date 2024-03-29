import json
from textwrap import indent, dedent
from termcolor import colored

from .base_doc import BaseDoc
from ...database import BaseDatabase
from ...helpers.constants.db import (METADATA, MODEL, BENCHMARK, DATASETS,
                                     EVALUATOR)
from ...helpers.templates.inspection import INSPECT_CLI, INSPECT_MD

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

    def _create_cli_str(self, benchmark_name: str, model_name: str,
                        data: str, eval_names: dict) -> str:
        """Create the benchmark result string for inspection in the CLI."""
        prompt = indent(colored(self.prompt, 'blue'), ' '*2)
        references = '\n'.join(f'  {ref}' for ref in data['references'])
        response = indent(colored(self.response, 'green'), ' '*2)
        evals = ''
        for eval_hash, result in self.evaluation.items():
            eval_name = eval_names[eval_hash]
            evals += f'\n  {eval_name}: {result["result"]}'
            if result['info'] != {}:
                eval_info = json.dumps(result['info'])
                evals += f'\n    {eval_info}'
        return INSPECT_CLI.format(
            benchmark_name=benchmark_name,
            model_name=model_name,
            question=data['question'],
            prompt=prompt,
            references=references,
            response=response,
            evaluations=evals)
    
    def _create_md_str(self, benchmark_name: str, model_name: str,
                       data: str, eval_names: dict) -> str:
        """Create the benchmark result string for markdown file."""
        references = '\n'.join(f'* {ref}' for ref in data['references'])
        evals = ''
        for eval_hash, result in self.evaluation.items():
            eval_name = eval_names[eval_hash]
            evals += (f'\n* <span style="color:teal">{eval_name}</span>: '
                      f'{result["result"]}')
            if result['info'] != {}:
                eval_info = json.dumps(result['info'], indent=4)
                evals += indent(f'\n```\n{eval_info}\n```', ' '*4)
        return INSPECT_MD.format(
            benchmark_name=benchmark_name,
            model_name=model_name,
            question=data['question'],
            prompt=self.prompt,
            references=references,
            response=self.response,
            evaluations=evals)

    def inspect(self, db: BaseDatabase, markdown: bool = False) -> str:
        benchmark_name = db.get_doc(METADATA, BENCHMARK, self.bm_hash)['name']
        model_name = db.get_doc(METADATA, MODEL, self.model_hash)['name']
        data = db.get_doc(DATASETS, BENCHMARK, self.question_hash)
        eval_names = {eval_hash: db.get_doc(METADATA, EVALUATOR, eval_hash)['name']
                      for eval_hash in self.evaluation.keys()}
        if markdown:
            s = self._create_md_str(benchmark_name, model_name, data,
                                    eval_names)
        else:
            s = self._create_cli_str(benchmark_name, model_name, data,
                                     eval_names)
            print(s)
        return s
