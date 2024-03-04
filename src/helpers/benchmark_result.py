import base64
import hashlib
import json
import textwrap
from termcolor import colored


class BenchmarkDoc:
    def __init__(self, bm_config: dict, model_config: dict,
                 prompt: str, response: str = None, evaluation: dict = None):
        self.bm_config = bm_config
        self.model_config = model_config
        self.prompt = prompt
        self.response = response
        self.evaluation = {} if evaluation is None else evaluation

    @staticmethod
    def str_to_b64_str(s: str) -> str:
        return base64.b64encode(s.encode('utf-8')).decode('utf-8')
    
    @staticmethod
    def b64_str_to_str(b: str) -> str:
        return base64.b64decode(b).decode('utf-8')

    @property
    def prompt_b64(self) -> str:
        return self.str_to_b64_str(self.prompt)
    
    @property
    def response_b64(self) -> str:
        return self.str_to_b64_str(self.response)

    def to_json(self):
        return {
            'benchmark': self.bm_config,
            'model': self.model_config,
            'prompt': self.prompt_b64,
            'response': self.response_b64,
            'evaluation': self.evaluation}

    def get_hash(self) -> int:
        """Return the SHA256 hash of the object."""
        json_str = json.dumps({
            'benchmark': self.bm_config,
            'model': self.model_config,
            'prompt': self.prompt_b64})
        return int(hashlib.sha256(
            json_str.encode(encoding='utf-8')).hexdigest(), 16)

    @classmethod
    def from_json(cls, json_obj: dict):
        return cls(json_obj['benchmark'], json_obj['model'], 
                   cls.b64_str_to_str(json_obj['prompt']),
                   cls.b64_str_to_str(json_obj['response']),
                   json_obj.get('evaluation'))

    def inspect(self, question, references):
        print(f'{colored("Benchmark", "red")} : {self.bm_config["name"]}')
        print(f'{colored("Model", "red")}     : {self.model_config["name"]}')
        print(f'{colored("Question", "red")}  : {question}')
        print(f'{colored("Prompt", "red")}    :')
        print(textwrap.indent(colored(self.prompt, 'blue'), '  '))
        print(f'{colored("References", "red")}:')
        for ref in references:
            print(f'  {ref}')
        print(f'{colored("Response", "red")}  :')
        print(textwrap.indent(colored(self.response, 'green'), '  '))
        print(f'{colored("Evaluations", "red")}:')
        for eval in self.evaluation.values():
            print(textwrap.indent(
                f'{eval["evaluator"]["name"]}: {eval["result"]}', '  '))
            if eval['info'] != {}:
                eval_info = json.dumps(eval['info'])
                print(textwrap.indent(eval_info, '    '))
        print()
