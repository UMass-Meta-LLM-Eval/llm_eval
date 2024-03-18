from .base_hf_model import BaseHFModel

class ZephyrModel(BaseHFModel):
    HF_ORG_NAME = 'HuggingFaceH4'

    def _predict(self, prompt: str) -> str:
        messages = [{
            'role': 'user',
            'content': prompt}]
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False,
                                                    add_generation_prompt=True)

        return super()._predict(prompt)
