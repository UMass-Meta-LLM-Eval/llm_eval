import os
from anthropic import Anthropic
from .base_model import BaseModel


class AnthropicModel(BaseModel):
    def __init__(self, model_config: dict):
        self._config = model_config
        client_kwargs = self._config.get('client_kwargs', {})
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'),
                             **client_kwargs)
        self._completions_kwargs = self._config.get('completions_kwargs', {})

    def _predict(self, prompt: str) -> str:
        messages = [{'role': 'user', 'content': prompt}]
        response = self.client.messages.create(
            model=self._config['model'],
            messages=messages,
            **self._completions_kwargs).content[0].text
        return response

    @property
    def config(self) -> dict:
        return self._config
