import json
from tempfile import NamedTemporaryFile

from ..helpers.constants.model import (OAI_BATCH_PURPOSE, OAI_BATCH_ENDPOINT,
                                       OAI_BATCH_COMPLETION_WINDOW,
                                       OAI_BATCH_METHOD, OAI_BATCH_SUCCESS)
from ..helpers.misc import create_hash
from ..helpers.constants.logging import UPDATE
from .openai_model import OpenAIModel
from . import logger


class OpenAIBatchRequestModel(OpenAIModel):
    def __init__(self, model_config: dict):
        super().__init__(model_config)
        self._request_data: list[dict] = []

    def _upload_jsonl(self, data: list[dict], purpose: str) -> str:
        """Upload the given data for the given purpose to OpenAI
        using the OpenAI client. Returns the file ID of the
        uploaded data."""
        with NamedTemporaryFile(suffix='.jsonl') as f:
            for item in data:
                line = json.dumps(item)+'\n'
                f.write(line.encode('utf-8'))
            file_response = self.client.files.create(file=f.file,
                                                     purpose=purpose)
            return file_response.id

    def _submit_batch_request(self, data: list[dict]) -> str:
        """Submit a batch processing request with the given data
        to OpenAI using the OpenAI client. Returns the batch ID
        of the submitted job."""
        file_id = self._upload_jsonl(data, purpose=OAI_BATCH_PURPOSE)
        batch_response = self.client.batches.create(
            input_file_id=file_id,
            endpoint=OAI_BATCH_ENDPOINT,
            completion_window=OAI_BATCH_COMPLETION_WINDOW)
        return batch_response.id
    
    def _predict(self, prompt: str, **kwargs) -> str:
        prompt_hash = create_hash(prompt)
        messages = [{'role': 'user', 'content': prompt}]
        request_object = {
            'custom_id': prompt_hash,
            'method': OAI_BATCH_METHOD,
            'url': OAI_BATCH_ENDPOINT,
            'body': {
                'model': self._config['model'],
                'messages': messages,
                **self._completions_kwargs}}
        self._request_data.append(request_object)
        
        return f'success ({prompt_hash[-4:]})'

    @property
    def request_count(self) -> int:
        return len(self._request_data)

    def exit(self, message: str = None) -> str:
        """Send the accumulated prompts as a batch request to OpenAI and
        return the ID of the submitted batch request."""

        logger.log(UPDATE, 'Creating and submitting batch request with %d '
                   'items.', self.request_count)

        batch_id: str = self._submit_batch_request(self._request_data)
        logger.log(UPDATE, 'Batch request submitted with ID: `%s`.', batch_id)

        super().exit(message)

        return batch_id

class OpenAIBatchRetrieveModel(OpenAIModel):
    def __init__(self, model_config: dict):
        super().__init__(model_config)
        
        try:
            self._batch_id = model_config['batch_id']
        except KeyError as e:
            logger.error('`batch_id` not found in model configuration.')
            raise ValueError('Batch ID needs to be provided in model '
                             'configuration.') from e
        
        # Boolean to enable lazy retrieval of results
        self._retrieved: bool = False
        self._results: dict[str, dict] = {}

    def _set_results(self):
        results_list = self._retrieve_batch_results(self._batch_id,
                                                    success=OAI_BATCH_SUCCESS,
                                                    verify=True)
        
        self._results = self._results_to_dict(results_list)
        self._retrieved = True

    def _download_jsonl(self, file_id: str) -> list[dict]:
        """Download the data corresponding to the give file ID
        from OpenAI using the OpenAI client. Returns the
        downloaded data."""
        content = self.client.files.content(file_id)
        content_lines = content.read().decode().splitlines()
        result_data = []
        for line in content_lines:
            result_data.append(json.loads(line))
        return result_data

    def get_batch_status(self) -> str:
        """Get the status of a batch job with the given batch ID."""
        batch_info = self.client.batches.retrieve(self._batch_id)
        return batch_info.status

    def _verify_batch_completion(self, raise_on_failure: bool = True) -> bool:
        """Verify if a batch job with the given batch ID has been completed
        and optionally raise an error on failure."""
        status = self.get_batch_status()

        if status == OAI_BATCH_SUCCESS:
            return True

        if raise_on_failure:
            raise RuntimeError(f'Batch completion for batch ID: `{self._batch_id}` '
                f' could not be verified. Status: `{status}`.')

        return False

    def _retrieve_batch_results(self, verify: bool = True):
        """Retrieve the results for a completed batch job corresponding the to
        the given batch ID after optinally checking for successful completion
        first."""
        if verify:
            self._verify_batch_completion(self._batch_id, OAI_BATCH_SUCCESS,
                                          raise_on_failure=True)

        batch_info = self.client.batches.retrieve(self._batch_id)
        output_file_id: str = batch_info.output_file_id
        return self._download_jsonl(output_file_id)
    
    def _results_to_dict(self, results_list: list[dict]) -> dict[str, dict]:
        """Convert a list of results to a dictionary indexed by the
        custom ID."""

        results_dict = {}
        for result in results_list:
            custom_id = result['custom_id']
            results_dict[custom_id] = result
        
        return results_dict

    def _predict(self, prompt: str, **kwargs) -> str:
        # Lazily retrieve results if not already done
        if not self._retrieved:
            self._set_results()

        prompt_hash = create_hash(prompt)
        result = self._results[prompt_hash]
        return result['response']['body']['choices'][0]['message']['content']
