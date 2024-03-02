import base64

def print_doc(doc):
    print(f'Benchmark : {doc["benchmark"]["name"]}')
    print(f'Model     : {doc["model"]["name"]}')
    print(f'Question  : {doc["question"]}')
    print(f'Prompt    : {doc["prompt"]}')
    response = base64.b64decode(doc["response"]).decode('utf-8')
    print(f'Response  : {response}')
    print('Evaluations:')
    for eval in doc['evaluation'].values():
        print(f'  {eval["evaluator"]["name"]}: {eval["result"]}')
        if eval.get('info', {}) != {}:
            print(f'    {eval["info"]}')
    print()

def inspect_collection(collection):
    for doc in collection.values():
        print_doc(doc)
