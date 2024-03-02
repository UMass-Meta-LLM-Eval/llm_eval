# from dotenv import load_dotenv
# load_dotenv()

from itertools import product
import json
import os
os.environ["HF_HOME"] = '/work/pi_dhruveshpate_umass_edu/grp22/.cache/huggingface'
os.environ['HF_TOKEN'] = ' '
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.benchmark import create_benchmark
from src.model import create_model
from src.database import MongoDBDatabase
import os

def main():
    print('HF Home set to - ', os.environ["HF_HOME"])
    with open('demo/naturalquestions/benchmark/info.json') as f:
        run_info = json.load(f)
    
    db = MongoDBDatabase('/work/pi_dhruveshpate_umass_edu/grp22/db')
    for (bm_cfg, model_cfg) in product(run_info['benchmarks'], run_info['models']):
        benchmark = create_benchmark(bm_cfg)
        model = create_model(model_cfg)
        benchmark.run(model, db)
    
    print('Run Successful!')


if __name__ == '__main__':
    main()
