from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')

def insert_benchmark_result(benchmark, question, prompt, response):
    document = {
        "benchmark": benchmark,
        "metadata": {
            "subset": "test",
            "num_shots": 1
        },
        "model": {
            "name": "meta-llama/llama-7b-chat-hf",
            "hyperparams": {
                "max_length": 128
            }
        },
        "question": question,
        "prompt": prompt,
        "response": response
    }

    collection.insert_one(document)
    print("Inserted benchmark result into MongoDB.")

benchmark = 'nq_results'

db = client[benchmark]
collection = db['results']

# Example usage
question = "What is the capital of France?"
prompt = "Answer this question: What is the capital of France?"
response = "The capital of France is Paris."

insert_benchmark_result(benchmark,question, prompt, response)
