import os
from openai import OpenAI
from .base_model import BaseModel


class OpenAIModel(BaseModel):
    def __init__(self, model_config: dict):
        self._config = model_config
        client_kwargs = self._config.get('client_kwargs', {})
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'),
                             **client_kwargs)
        self._completions_kwargs = self._config.get('completions_kwargs', {})

    def _predict(self, prompt: str) -> str:
        messages = [{'role': 'user', 'content': prompt}]
        response = self.client.chat.completions.create(
            model=self._config['model'],
            messages=messages,
            **self._completions_kwargs).choices[0].message.content
        return response

    @property
    def config(self) -> dict:
        return self._config
