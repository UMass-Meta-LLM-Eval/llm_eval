# README

## Important Destinations
Project root on unity: `/work/pi_dhruveshpate_umass_edu/grp22/` <br />
Repo: `/work/pi_dhruveshpate_umass_edu/grp22/src/llm_eval` <br />
Conda env: `/work/pi_dhruveshpate_umass_edu/grp22/conda/envs/llm-eval` <br />

## Creating Personal Environments
`conda create --name llm-parsing python=3.9.7 pip` <br />
`pip install -r requirements.txt` <br />
`conda activate llm-parsing` <br />

## Running Model Output Pipeline
Model Output Pipeline will cache all the LLM responses based on hyper-parameters
Hyper-parameters with model and benchmark name in `model_output/configs/`
Running on Slurm - `sbatch run_generate_model_output.sh`

Running Locally - <br />
`conda activate /work/pi_dhruveshpate_umass_edu/grp22/conda/envs/llm-eval` <br />
`mongod --dbpath /work/pi_dhruveshpate_umass_edu/grp22/db` <br />
`python model_output/generate_model_output.py` <br />
`python model_output/retrieve_model_output.py` <br />





