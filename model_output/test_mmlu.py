from datasets import load_dataset
from transformers import AutoTokenizer
import transformers
import torch
from transformers import pipeline

configs = ['abstract_algebra', 'anatomy', 'astronomy', 'business_ethics', 'clinical_knowledge', 'college_biology', 'college_chemistry', 'college_computer_science', 'college_mathematics', 'college_medicine', 'college_physics', 'computer_security', 'conceptual_physics', 'econometrics', 'electrical_engineering', 'elementary_mathematics', 'formal_logic', 'global_facts', 'high_school_biology', 'high_school_chemistry', 'high_school_computer_science', 'high_school_european_history', 'high_school_geography', 'high_school_government_and_politics', 'high_school_macroeconomics', 'high_school_mathematics', 'high_school_microeconomics', 'high_school_physics', 'high_school_psychology', 'high_school_statistics', 'high_school_us_history', 'high_school_world_history', 'human_aging', 'human_sexuality', 'international_law', 'jurisprudence', 'logical_fallacies', 'machine_learning', 'management', 'marketing', 'medical_genetics', 'miscellaneous', 'moral_disputes', 'moral_scenarios', 'nutrition', 'philosophy', 'prehistory', 'professional_accounting', 'professional_law', 'professional_medicine', 'professional_psychology', 'public_relations', 'security_studies', 'sociology', 'us_foreign_policy', 'virology', 'world_religions']

dataset = load_dataset("lukaemon/mmlu", configs[0])

prompt_prefix = ''

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

def get_llama_response(prompt: str) -> None:
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
    return sequences[0]['generated_text']

f1 = open("/home/amansinghtha_umass_edu/llm_eval/model_output/response.txt", "a")
f2 = open("/home/amansinghtha_umass_edu/llm_eval/model_output/target.txt", "a")

counter = 1
for key in dataset:
  for row in dataset[key]:
    question, target = '', ''
    prompt_suffix = '. Answer using Options A/B/C/D - A: '+row['A']+', B: '+row['B']+', C: '+row['C']+', D: '+row['D']
    question = prompt_prefix+row['input']+prompt_suffix
    target = row['target']
    response = get_llama_response(question)
    f1.write(response+'\n**\n')
    f2.write(target+'\n**\n')
    print(str(counter)+'/'+str(len(dataset[key])))
f1.close()
f2.close()



