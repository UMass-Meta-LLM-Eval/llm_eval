from transformers import AutoTokenizer
import transformers
import torch
from transformers import pipeline

if not torch.cuda.is_available():
    print('GPU not available!')
    exit(1)
else:
    print(torch.cuda.get_device_name(0))

exit(0)

model = "meta-llama/Llama-2-7b-chat-hf" # meta-llama/Llama-2-7b-hf

tokenizer = AutoTokenizer.from_pretrained(model, use_auth_token=True)

llama_pipeline = pipeline(
    "text-generation",  # LLM task
    model=model,
    torch_dtype=torch.float16,
    device_map="auto",
)

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
        max_length=64,
    )
    print("Chatbot:", sequences[0]['generated_text'])



prompt = 'What is the Capital of India?\n'
print(get_llama_response(prompt))