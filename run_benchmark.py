import torch
import os
os.environ['HF_HOME'] = '/work/pi_dhruveshpate_umass_edu/grp22/.cache/huggingface'

from transformers import pipeline
from lm_eval import simple_evaluate
import json

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'Using device: {device}')

model_name = 'microsoft/phi-2'
# pipe = pipeline('text-generation', model=model_name, device_map='cuda',
#     torch_dtype=torch.float16, trust_remote_code=True)

print('Running evaluation...')
result = simple_evaluate(
    'hf',
    model_args=f'pretrained={model_name},device_map=cuda,dtype=float16,trust_remote_code=True',
    tasks='mmlu',
    # device=device,
    batch_size='auto',
    limit=10)
print('Evaluation complete.')

with open('result.json', 'w') as f:
    json.dump(result, f, indent=4)

with open('result_scores.json', 'w') as f:
    json.dump(result['results'], f, indent=4)
