# from dotenv import load_dotenv
# load_dotenv()

from itertools import product
import json
import os
os.environ["HF_HOME"] = '/work/pi_dhruveshpate_umass_edu/grp22/.cache/huggingface'
os.environ['HF_TOKEN'] = ''
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.benchmark import create_benchmark
from src.model import create_model
from src.database import MongoDBDatabase
from src.evaluator.base_evaluator import DummyEvaluator
from src.database.dummy_mongodb import DummyMongoDB  # Dummy database
import os

def main():
    print('HF Home set to - ', os.environ["HF_HOME"])
    with open('demo/naturalquestions/benchmark/info.json') as f:
        run_info = json.load(f)
    
    # Uncomment below to use real MongoDB
    # db = MongoDBDatabase('/work/pi_dhruveshpate_umass_edu/grp22/db')
    # Dummy database integration
    dummy_mongo_db = DummyMongoDB(name="dummy_db_name", db_params={})
    db = dummy_mongo_db

    dummy_evaluator = DummyEvaluator(eval_config={}, mongo_db=dummy_mongo_db)
    for (bm_cfg, model_cfg) in product(run_info['benchmarks'], run_info['models']):
        benchmark = create_benchmark(bm_cfg)
        #model = create_model(model_cfg)
        #benchmark.run(model, db)
        benchmark.compute_results(model_cfg, db, dummy_evaluator)


if __name__ == '__main__':
    main()
