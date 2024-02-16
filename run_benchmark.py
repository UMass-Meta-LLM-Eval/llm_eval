import torch
import os
from dotenv import load_dotenv
load_dotenv()

from transformers import AutoTokenizer, AutoModelForCausalLM
from lm_eval import simple_evaluate
from lm_eval.models.huggingface import HFLM
import json

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'Using device: {device}')

# Create the HuggingFace model
model_name = os.getenv('MODEL_NAME')
if model_name is None:
    print('No model name found in environment')
    # model_name = 'microsoft/phi-2'
    # model_name = 'meta-llama/Llama-2-7b-hf'
    model_name = 'EleutherAI/pythia-14m'

print(f'Using model: {model_name}')
model = AutoModelForCausalLM.from_pretrained(
    model_name, device_map='cuda',
    torch_dtype=torch.float16, token=os.getenv('HF_TOKEN'),
    trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Wrap the model in a lm_eval model
model = HFLM(pretrained=model, tokenizer=tokenizer, batch_size='auto')

print('Running evaluation...')
result = simple_evaluate(
    model,
    tasks=['triviaqa', 'nq_open', 'mmlu'],
    # limit=10
    )
print('Evaluation complete.')

model_name = model_name.replace('/', '__')
with open(f'result-{model_name}.json', 'w') as f:
    json.dump(result, f, indent=4)

with open(f'result_scores-{model_name}.json', 'w') as f:
    json.dump(result['results'], f, indent=4)
