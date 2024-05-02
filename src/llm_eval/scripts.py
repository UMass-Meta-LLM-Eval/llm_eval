import argparse
import os
import sys

from dotenv import load_dotenv
loaded = load_dotenv()
if not loaded:
    print('No .env file found')
    sys.exit(1)

from .database import MongoDB
from . import analysis as llm_analysis

def analysis():
    parser = argparse.ArgumentParser()
    parser.add_argument('func_and_args', nargs='*', default=[])
    parsed_args = parser.parse_args()

    if not parsed_args.func_and_args:
        raise ValueError('No function provided')

    func_name = parsed_args.func_and_args[0]
    args_and_kwargs = parsed_args.func_and_args[1:]

    kwarg_pairs = [arg.split('=', 1) for arg in args_and_kwargs if '=' in arg]
    args = [arg for arg in args_and_kwargs if '=' not in arg]
    kwargs = {k: v for (k, v) in kwarg_pairs}

    # Load func from imported functions
    func = getattr(llm_analysis, func_name)

    # Create the MongoDB object
    db = MongoDB({'uri': os.getenv('MONGODB_URI')})

    # Run the function
    print(f'Running function: {func_name}(*{args}, **{kwargs})')
    func(*args, **kwargs, db=db)
    print('Done!')
