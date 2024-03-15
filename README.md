# README

## Important Destinations
Project root on unity: `/work/pi_dhruveshpate_umass_edu/grp22/` <br />
Repo: `/work/pi_dhruveshpate_umass_edu/grp22/src/llm_eval` <br />
Conda env: `/work/pi_dhruveshpate_umass_edu/grp22/conda/envs/llm-eval` <br />

## Creating Personal Environments
`conda create --name llm-parsing python=3.9.7 pip` <br />
`pip install -r requirements.txt` <br />
`conda activate llm-parsing` <br />

## Setup

Activate a CPU interactive session and load modules:

```bash
salloc -N 1 -n 1 -c 8 -p cpu-preempt -t 2:00:00 --mem=8G
source activate-cpu.sh
```

Activate a GPU interactive session and load modules:

```bash
salloc -N 1 -n 1 -c 8 -p gpu-preempt -t 2:00:00 --mem=8G --gpus=1
source activate-gpu.sh
```

For bigger GPU, set the constraint

```bash
salloc -N 1 -n 1 -p gpu,gpu-preempt -t 2:00:00 --mem=8G --gpus=1 --constraint="[a100|m40|rtx8000]"
```

## Running a job

The code for all the benchmarks and evaluation is in the `src` directory. In
the root of the project, you can run the `main.py` driver script to run a job.
The script takes a few arguments:

1. `-b` or `--benchmark-config`: The name of the config JSON file in the
`configs` directory. This file contains the configuration for the benchmark
to run.

2. `-e` or `--eval-config`: The name of the config JSON file in the `configs`
directory. This file contains the configuration for the evaluation to run.

3. `-i` or `--inspect-config`: The name of the config JSON file in the
`configs` directory. This file contains the configuration for manual inspection
of the model output, which will be printed to the console.

For example, to run a benchmark job using the config present in
`configs/benchmark.json`, you can run the following command:

```bash
python main.py -b benchmark
```

To run an evaluation job using the config present in `configs/evaluation.json`,
you can run the following command:

```bash
python main.py -e evaluation
```

To run both the benchmark and evaluation in a single job, you can run the
following command:

```bash
python main.py -b benchmark -e evaluation
```

To run an inspection job using the config present in `configs/inspection.json`,
you can run the following command:

```bash
python main.py -i inspection
```

## Submitting a job

To submit a job to the cluster, you can use the `main.sh` script with `sbatch`.
The script takes the same arguments as `main.py`, for example, to submit a
benchmark job using the config present in `configs/benchmark.json`, you can run
the following command:

```bash
sbatch main.sh -b benchmark
```
##Setting up MongoDB Atlas

To connect to the MongoDB Atlas cluster:

1. Download the server CA certificate from https://letsencrypt.org/certs/isrgrootx1.pem and place it in the root directory of the project.

2. Download the driver for MongoDB Atlas
```bash
python -m pip install "pymongo[srv]"==3.6
```

3. Place the MongoDB URI in the .env file as 

'MONGO_URI="mongodb+srv://<username>:<password>@<cluster_url>/?retryWrites=true&w=majority&appName=<cluster_name>&tlsCAFile=isrgrootx1.pem"

Note: Make sure to grant database user access to the users for shared access to the respective cluster.

4. Grant Network Access to the IP address of the client for your cluster. Grant access to '0.0.0.0' if you are running it on Unity. 

5. In the root directory, run the following command to test if the client is able to establish connection with the server

```bash
python -m src.database.mongodb_test
```

# Available Implementations

## Models

1. Llama
    
    `cls` = "LlamaModel"
    * `chat` (`bool`): If using the chat model (default: `False`)

2. OpenAI

    `cls` = "OpenAIModel"
    

3. Anthropic

    `cls` = "AnthropicModel"
    * `chat` (`bool`): If using the chat model (default: `False`)

4. HumanModel
    
    `cls` = "HumanModel"
    
    Makes queries to the human using CLI. For testing purposes.

5. DummyModel
    
    `cls` = "DummyModel"
    
    Returns the prompt with a fixed prefix. For automated testing purposes.

    * `prefix` (`str`): The fixed prefix to return (default: `""`)


## Benchmarks

1. Natural Questions

    `cls` = "NaturalQuestionsBenchmark"
    * `num_samples` (`int`): The number of samples (questions) to use (default: `None`)
    * `num_fewshot` (`int`): The number of few-shot examples to use (default: 0)
    * `seed` (`int`): The random seed to use for shuffling the dataset (default: `None`)

2. TriviaQA

    `cls` = TBD

3. MMLU

    `cls` = "MMLUBenchmark"
    
4. DummyNQ

    `cls` = "DummyNQBenchmark"
    
    Natural Questions benchmark with only 1 sample for testing purposes.


## Evaluators

1. Exact Match

    `cls` = "ExactMatchEvaluator"
    * `cased` (`bool`): If the evaluation should be case-sensitive (default: `True`)

2. Contains

    `cls` = "ContainsMatchEvaluator"
    * `cased` (`bool`): If the evaluation should be case-sensitive (default: `True`)

3. HumanEvaluator

    `cls` = "HumanEvaluator"
    
    Makes queries to the human using CLI. Human must answer with `y`, `n`, `yy`,
    or `nn` for each prompt.
