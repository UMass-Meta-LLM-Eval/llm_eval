import base64
import hashlib
import json


class BenchmarkDoc:
    
    def __init__(self, bm_config: dict, model_config: dict, 
                 question: str, prompt: str, response: str, acceptable_answers: list):
        self.bm_config = bm_config
        self.model_config = model_config
        self.question = question
        self.prompt = prompt
        self.response = response
    def to_json(self):
        return {
            'benchmark': self.bm_config,
            'model': self.model_config,
            'question': self.question,
            'prompt': self.prompt,
            'response': self.response,
            'evaluation': {}}
    def get_hash(self) -> int:
        """Return the SHA256 hash of the object."""
        json_str = json.dumps({
            'benchmark': self.bm_config,
            'model': self.model_config,
            'question': self.question,
            'prompt': self.prompt})
        obj_bytes =  base64.b64encode(json_str.encode(encoding='utf-8'))
        return int(hashlib.sha256(obj_bytes).hexdigest(), 16)
    