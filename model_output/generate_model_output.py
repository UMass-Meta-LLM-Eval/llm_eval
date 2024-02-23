from datasets import load_dataset
from transformers import AutoTokenizer
import transformers
import torch
from transformers import pipeline
import base64

configs = ['abstract_algebra', 'anatomy', 'astronomy', 'business_ethics', 'clinical_knowledge', 'college_biology', 'college_chemistry', 'college_computer_science', 'college_mathematics', 'college_medicine', 'college_physics', 'computer_security', 'conceptual_physics', 'econometrics', 'electrical_engineering', 'elementary_mathematics', 'formal_logic', 'global_facts', 'high_school_biology', 'high_school_chemistry', 'high_school_computer_science', 'high_school_european_history', 'high_school_geography', 'high_school_government_and_politics', 'high_school_macroeconomics', 'high_school_mathematics', 'high_school_microeconomics', 'high_school_physics', 'high_school_psychology', 'high_school_statistics', 'high_school_us_history', 'high_school_world_history', 'human_aging', 'human_sexuality', 'international_law', 'jurisprudence', 'logical_fallacies', 'machine_learning', 'management', 'marketing', 'medical_genetics', 'miscellaneous', 'moral_disputes', 'moral_scenarios', 'nutrition', 'philosophy', 'prehistory', 'professional_accounting', 'professional_law', 'professional_medicine', 'professional_psychology', 'public_relations', 'security_studies', 'sociology', 'us_foreign_policy', 'virology', 'world_religions']

dataset = load_dataset("lukaemon/mmlu", configs[0])

if not torch.cuda.is_available():
    print('GPU not available!')
    exit(1)
else:
    print(torch.cuda.get_device_name(0))

model = "meta-llama/Llama-2-7b-chat-hf" # meta-llama/Llama-2-7b-hf

tokenizer = AutoTokenizer.from_pretrained(model, use_auth_token=True)

llama_pipeline = pipeline(
    "text-generation",  # LLM task
    model=model,
    torch_dtype=torch.float16,
    device_map="auto",
)

print('Pipeline Generated!')

def get_llm_response(prompt: str) -> None:
    """
    Generate a response from the Llama model.

    Parameters:
        prompt (str): The user's input/question for the model.

    Returns:
        None: Prints the model's response.
    """
    sequences = llama_pipeline(
        prompt,
        do_sample=True,
        top_k=10,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
        max_length=256,
    )
    response = sequences[0]['generated_text']
    if question in prompt:
        return response[len(prompt):]
    return response

def insert_benchmark_result(question, prompt_prefix, prompt_suffix, response):
    document = {
        "benchmark": "mmlu",
        "metadata": {
            "subset": configs[0],
            "num_shots": 1
        },
        "model": {
            "name": "meta-llama/llama-7b-chat-hf",
            "hyperparams": {
                "max_length": 128
            }
        },
        "question": question,
        "prompt_prefix": prompt_prefix,
        "prompt_suffix": prompt_suffix,
        "response": response
    }

    #collection.insert_one(document)
    print("Inserted benchmark result into MongoDB.")
    return document

def encoderesponseb64(response):
    sample_string_bytes = response.encode("ascii") 
    base64_bytes = base64.b64encode(sample_string_bytes) 
    return base64_bytes

def decoderresponseb64(base64_bytes):
    response_bytes = base64.b64decode(base64_bytes) 
    response = response_bytes.decode("ascii")
    return response

for key in dataset:
  for row in dataset[key]:
    question, target = '', ''
    prompt_suffix = ' A: '+row['A']+', B: '+row['B']+', C: '+row['C']+', D: '+row['D']
    prompt_prefix = ''
    question = prompt_prefix+row['input']+prompt_suffix
    target = row['target']
    response = get_llm_response(question)
    response = encoderesponseb64(response)
    document = insert_benchmark_result(question, prompt_prefix, prompt_suffix, response)
    print(document)
    exit(1)



