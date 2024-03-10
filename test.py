from src.benchmark import create_benchmark
from src.evaluator import LLMEvaluator 
from src.database.mongodb import MongoDB
import json
from dotenv import load_dotenv
load_dotenv()

def test_llm_evaluator():
    test_config = 'poc-llama7b-llmevalulator'

    with open(f'configs/{test_config}.json') as f:
        eval_config = json.load(f)

    test = LLMEvaluator(eval_config['evaluators'][0])

    ques = 'When was the last time anyone was on the moon?'
    res = 'December 1972 UTC'
    ref = ['14 December 1972 UTC, December 1972']

    benchmark = create_benchmark(eval_config['benchmarks'][0])

    print(test.evaluate(question=ques, response=res, references=ref, benchmark=benchmark))
    
def DummyMongoDB():
    db = MongoDB('test', 'MONGODBURI1')

    test_db_name = 'benchmark'
    test_collection_name = 'naturalquestions'

    doc_id = 1234
    test_doc = {
        'model': 'dummy',
        'question': 'When was the last time anyone was on the moon?',
        'prompt': 'Q. When was the last time anyone was on the moon? A: ',
        'response': 'VGhlIGxhc3QgdGltZSBhbnlvbmUgd2FzIG9uIHRoZSBtb29uIHdhcyBkdXJpbmcgdGhlIEFwb2xsbyAxNyBtaXNzaW9uIGluIERlY2VtYmVyIDE5NzI=',
        'accepted_answers' : ['14 December 1972 UTC', 'December 1972'],
    }

    #print('Adding document...')
    #db.add_doc(test_db_name, test_collection_name, doc_id, test_doc)
    
    print('Retrieving documents...')
    documents = db.get_doc(test_db_name, test_collection_name)
    print(len(documents))
    
if __name__ == '__main__':
    DummyMongoDB()
    #test_llm_evaluator()