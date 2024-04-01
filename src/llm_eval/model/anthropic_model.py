import os
import time
from anthropic import Anthropic
from .base_model import BaseModel
from ..helpers.documents import InfoDoc


class AnthropicModel(BaseModel):
    def __init__(self, model_config: dict):
        self._config = model_config
        client_kwargs = self._config.get('client_kwargs', {})
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'),
                             **client_kwargs)
        self._completions_kwargs = self._config.get('completions_kwargs', {})
        self._doc = InfoDoc(**model_config)

    def _predict(self, prompt: str) -> str:
        t_start = time.time()
        messages = [{'role': 'user', 'content': prompt}]
        response = self.client.messages.create(
            model=self._config['model'],
            messages=messages,
            **self._completions_kwargs).content[0].text
        t_elapsed = time.time() - t_start
        t_sleep = 1.01
        if t_elapsed < t_sleep:
            time.sleep(t_sleep - t_elapsed)
        return response

    @property
    def config(self) -> dict:
        return self._config

    @property
    def hashval(self):
        return self._doc.doc_id
