# README

This repository contains the code for the paper "[Judging the Judges: Evaluating Alignment and Vulnerabilities in LLMs-as-Judges](https://arxiv.org/abs/2406.12624)".

![Judging the Judges](images/fig1.png)

## Abstract

Offering a promising solution to the scalability challenges associated with human evaluation, the LLM-as-a-judge paradigm is rapidly gaining traction as an approach to evaluating large language models (LLMs). However, there are still many open questions about the strengths and weaknesses of this paradigm, and what potential biases it may hold. In this paper, we present a comprehensive study of the performance of various LLMs acting as judges. We leverage TriviaQA as a benchmark for assessing objective knowledge reasoning of LLMs and evaluate them alongside human annotations which we found to have a high inter-annotator agreement. Our study includes 9 judge models and 9 exam taker models -- both base and instruction-tuned. We assess the judge model's alignment across different model sizes, families, and judge prompts. Among other results, our research rediscovers the importance of using Cohen's kappa as a metric of alignment as opposed to simple percent agreement, showing that judges with high percent agreement can still assign vastly different scores. We find that both Llama-3 70B and GPT-4 Turbo have an excellent alignment with humans, but in terms of ranking exam taker models, they are outperformed by both JudgeLM-7B and the lexical judge Contains, which have up to 34 points lower human alignment. Through error analysis and various other studies, including the effects of instruction length and leniency bias, we hope to provide valuable lessons for using LLMs as judges in the future.

# Running experiments

All the experiments in the paper were run using the code in this repository, on the Unity cluster at the University of Massachusetts Amherst and stored on a MongoDB database.

## Creating configs

To run any benchmark and/or evaluation, the user only needs to specify the
config as a JSON file, and run the `main.py` script with the appropriate
arguments.

The JSON config files are stored in the `configs` directory. The config files
have the following keys:

1. `metadata`: Metadata for the job, useful for storing any extra information
    about the job. The metadata is not used by the code.
2. `benchmarks`: A list of benchmark configurations.
3. `models`: A list of model configurations.
4. `evaluators`: A list of evaluator configurations.

A benchmark job will run each benchmark with each model. An evaluation job will
run each evaluator with each benchmark-model pair. Evaluation job assumes that
the corresponding benchmark job has already been run.

A sample config file is shown below:

```json
{
    "metadata": {
        "version": "v1.6.0",
    },
    "benchmarks": [
        {
            "name": "triviaQA-400-v1.5.0",
            "cls": "TriviaQABenchmark",
            "subset": "unfiltered", 
            "seed": 51,
            "num_samples": 400,
            "num_fewshot": 5
        }
    ],
    "models" : [
        {
            "name": "gpt-4t",
            "cls": "OpenAIModel",
            "model": "gpt-4-turbo-2024-04-09",
            "chat": true
        },
        {
            "name": "mistral-7B",
            "cls": "MistralModel",
            "model": "mistralai/Mistral-7B-v0.1"
        }
    ],
    "evaluators": [
        {
            "name": "eval-qwen72-extract",
            "cls": "LLMExtractEvaluator",
            "model_config": {
                "cls": "HFModel",
                "model": "Qwen/Qwen1.5-72B-Chat",
                "chat": true,
                "max_new_tokens": 512
            },
            "truncate": "newlinequestion",
            "template": "TAG",
            "eval_tag": "evaluation"
        }
    ]
}
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

3. `-be` or `-eb`: The name of the config JSON file in the `configs` directory.
This file contains the configuration for both the benchmark and evaluation to
run.

4. `-i` or `--inspect-config`: The name of the config JSON file in the
`configs` directory. This file contains the configuration for manual inspection
of the model output, which will be printed to the console.

5. `-v` or `--verbose`: If set, the output will be more verbose.

6. `--json-db`: Use a local JSON database instead of MongoDB. Useful for
testing.

7. `--markdown`: Used with the `inspect` job to save the output to a markdown
file.

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

If the benchmark and evaluation configs are the same, you can run the
following equivalent command:

```bash
python main.py -be benchmark
```

To run an inspection job using the config present in `configs/inspection.json`,
you can run the following command:

```bash
python main.py -i inspection
```

# Models

Models have the following attributes:

1. `cls` (`str`): The name of the model class to use
2. `name` (`str`): Name for easy identification in outputs and logs, not used
    by the code
3. `max_new_tokens` (`int`): The maximum number of new tokens to generate
    (default: 32)

## Model classes

1. HuggingFace
    
    `cls` = [`HFModel`, `LlamaModel`, `MistralModel`,`Phi2Model`]
    * `chat` (`bool`): If using the chat model (default: `False`)
    * `model` (`str`): The name of the model. Full model name
    including org name (e.g., `"meta-llama/Llama-2-70b"`). If using a custom
    model class (e.g. `LlamaModel`), you can specify the full model name or
    just the model name on HuggingFace (e.g., `"Llama-2-70b"`). In the latter
    case, the default org name for the model class (`HF_ORG_NAME` attribute)
    will be used.
    (default: 32)

    All the supported models are listed below:

    | **Model**       | **HFModel**         | **HFModel**    | **LlamaModel**            | **MistralModel**           | **HFModel**      | **Phi2Model** | **HFModel**     | **HFModel**          | **HFModel**           |
    |-----------------|---------------------|----------------|---------------------------|----------------------------|------------------|---------------|-----------------|----------------------|-------------------|
    | **Org Name**    | _tiiuae_            | _google_       | _meta-llama_              | _mistralai_                | _allenai_        | _microsoft_   | _lmsys_         | _HuggingFaceH4_      | _Qwen_            |
    | **Base Models** | falcon-7b           | gemma-2b       | Llama-2-7b-hf             | Mistral-7B-v0.1            | OLMo-1B          | phi-2         |                 |                      | Qwen1.5-0.5B      |
    |                 | falcon-40b          | gemma-7b       | Llama-2-13b-hf            | Mixtral-8x7B-v0.1          | OLMo-7B          |               |                 |                      | Qwen1.5-1.8B      |
    |                 | falcon-180b         |                | Llama-2-70b-hf            |                            |                  |               |                 |                      | Qwen1.5-4B        |
    |                 |                     |                | Meta-Llama-3-8B           |                            |                  |               |                 |                      | Qwen1.5-7B        |
    |                 |                     |                | Meta-Llama-3-70B          |                            |                  |               |                 |                      | Qwen1.5-14B       |
    |                 |                     |                |                           |                            |                  |               |                 |                      | Qwen1.5-72B       |
    | **Chat Models** | falcon-7b-instruct  | gemma-2b-it    | Llama-2-7b-chat-hf        | Mistral-7B-Instruct-v0.2   | OLMo-7B-Instruct | phi-2         | vicuna-7b-v1.5  | zephyr-7b-beta       | Qwen1.5-0.5B-Chat |
    |                 | falcon-40b-instruct | gemma-7b-it    | Llama-2-13b-chat-hf       | Mixtral-8x7B-Instruct-v0.1 |                  |               | vicuna-13b-v1.5 | zephyr-7b-gemma-v0.1 | Qwen1.5-1.8B-Chat |
    |                 | falcon-180b-chat    |                | Llama-2-70b-chat-hf       |                            |                  |               | vicuna-33b-v1.3 |                      | Qwen1.5-4B-Chat   |
    |                 |                     |                | Meta-Llama-3-8B-Instruct  |                            |                  |               |                 |                      | Qwen1.5-7B-Chat   |
    |                 |                     |                | Meta-Llama-3-70B-Instruct |                            |                  |               |                 |                      | Qwen1.5-14B-Chat  |
    |                 |                     |                |                           |                            |                  |               |                 |                      | Qwen1.5-72B-Chat  |

2. OpenAI

    `cls` = `OpenAIModel`
    `model` (`str`): The name of the model, as defined by OpenAI in their
    API reference (e.g., `"gpt-4-turbo-2024-04-09"`)

3. Anthropic

    `cls` = `AnthropicModel`
    * `chat` (`bool`): If using the chat model (default: `False`)

4. HumanModel
    
    `cls` = `HumanModel`
    
    Makes queries to the human using CLI. For testing purposes.

5. DummyModel
    
    `cls` = "DummyModel"
    
    Returns the prompt with a fixed prefix. For automated testing purposes.

    * `prefix` (`str`): The fixed prefix to return (default: `""`)


# Benchmarks

Benchmarks have the following attributes:

1. `cls` (`str`): The name of the benchmark class to use
2. `name` (`str`): Name for easy identification in outputs and logs, not used
    by the code
3. `seed` (`int`): The random seed to use for shuffling the fewshot examples
    and benchmark questions (if sampling). Default is `0`.
4. `num_samples` (`int`): The number of samples (questions) to use. A value of
    `None` means all questions are used without shuffling. Default is `None`.
5. `num_fewshot` (`int`): The number of few-shot examples to use. Default is
    `0`.
6. `template` (`str`): Name of the template to use for creating the prompt.
    Default is `"BASE_SIMPLE"`. See `llm_eval/helpers/templates/` for available
    templates.

## Benchmark classes

1. Natural Questions

    `cls` = "NaturalQuestionsBenchmark"

2. TriviaQA

    `cls` = "TriviaQABenchmark"
    * `subset`: (`str`:"unfiltered"/"rc") : The subset of TriviaQA to use
    for benchamrking

3. MMLU

    `cls` = "MMLUBenchmark"

# Evaluators

Evaluators have the following attributes:

1. `cls` (`str`): The name of the evaluator class to use
2. `name` (`str`): Name for easy identification in outputs and logs, not used
    by the code

## Evaluator classes

1. Exact Match

    `cls` = "ExactMatchEvaluator"
    * `cased` (`bool`): If the evaluation should be case-sensitive (default: `True`)

2. Contains

    `cls` = "ContainsMatchEvaluator"
    * `cased` (`bool`): If the evaluation should be case-sensitive (default: `True`)

3. HumanEvaluator

    `cls` = "HumanEvaluator"
    
    Makes queries to the human using CLI. Human must answer with `y`, `n`,
    `y?`, or `n?` for each prompt.

4. LLMEvaluator

    `cls` = "LLMEvaluator"
    * `model` (`Model`): The model to use for generating
    * `template` (`str`): Name of the template to use for creating the prompt
    for the evaluator. Default is `"DEFAULT"`.
    * truncate (`str`): The truncation logic to use. Available options are
    `"newline"`, `"newlinequestion"`,  `"skip"`, and `"eleutherai"`. Default
    is `"newline"`.
    * `eval_tag` (`str`): A tag to identify the evaluation in the output. For
    example, if the `eval_tag` is `"tag"`, and the raw output of the evaluator
    is `"The answer is <tag>correct</tag> because..."`, the evaluator will
    extract `"correct"` as the answer. Useful if the template asks the evalutor
    to wrap its evaluation inside a specified tag. If the `eval_tag` is `None`,
    the raw output is used as the answer. Default is `None`.


# Cite Us

```bibtex
@misc{thakur2024judging,
      title={Judging the Judges: Evaluating Alignment and Vulnerabilities in {LLMs}-as-Judges}, 
      author={Aman Singh Thakur and Kartik Choudhary and Venkat Srinik Ramayapally and Sankaran Vaidyanathan and Dieuwke Hupkes},
      year={2024},
      eprint={2406.12624},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2406.12624}, 
}
```

