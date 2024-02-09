# Use a pipeline as a high-level helper
import torch
import os
os.environ['HF_HOME'] = '/work/pi_dhruveshpate_umass_edu/grp22/.cache/huggingface'

from transformers import pipeline

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'Using device: {device}')

model_name = 'microsoft/phi-2'
pipe = pipeline('text-generation', model=model_name, device_map='cuda',
    torch_dtype=torch.float16, trust_remote_code=True)

# Generate text
ans = pipe('To bake a cake, first', num_return_sequences=1, do_sample=True,
    max_new_tokens=20)
print(ans[0]['generated_text'])
