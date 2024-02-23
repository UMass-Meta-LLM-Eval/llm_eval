# README

## Important Destinations
Project root on unity: `/work/pi_dhruveshpate_umass_edu/grp22/`
Repo: `/work/pi_dhruveshpate_umass_edu/grp22/src/llm_eval`
Conda env: `/work/pi_dhruveshpate_umass_edu/grp22/conda/envs/llm-eval`

## Creating Personal Environments
`conda create --name llm-parsing python=3.9.7 pip`
`pip install -r requirements.txt`
`conda activate llm-parsing`

## Running Model Output Pipeline
Model Output Pipeline will cache all the LLM responses based on hyper-parameters
Hyper-parameters with model and benchmark name in `model_output/configs/`
Running on Slurm - `sbatch run_generate_model_output.sh`

Running Locally -
`conda activate /work/pi_dhruveshpate_umass_edu/grp22/conda/envs/llm-eval`
`mongod --dbpath /work/pi_dhruveshpate_umass_edu/grp22/db`
`python model_output/generate_model_output.py`
`python model_output/retrieve_model_output.py`





