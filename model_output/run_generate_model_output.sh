#!/bin/bash

#SBATCH --partition=gpu-preempt
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=1
#SBATCH --mem=20GB
#SBATCH --time=01:00:00
#SBATCH --constraint=a100
#SBATCH -o generate_id-%j.out

#conda run -n llm-parsing python /home/amansinghtha_umass_edu/llm_eval/model_output/test_mmlu.py
module load miniconda/22.11.1-1

/work/pi_dhruveshpate_umass_edu/grp22/conda/envs/llm-eval/bin/mongod --fork --dbpath /work/pi_dhruveshpate_umass_edu/grp22/db --logpath /work/pi_dhruveshpate_umass_edu/grp22/db/logs/log.log --logappend

conda activate llm-parsing
python /home/amansinghtha_umass_edu/llm_eval/model_output/generate_model_output.py

/work/pi_dhruveshpate_umass_edu/grp22/conda/envs/llm-eval/bin/mongod --dbpath /work/pi_dhruveshpate_umass_edu/grp22/db --shutdown
ps ax | grep "mongod"