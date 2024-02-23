#!/bin/bash

#SBATCH --partition=gpu-preempt
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=1
#SBATCH --mem=20GB
#SBATCH --time=01:00:00
#SBATCH --constraint=a100
#SBATCH -o generate_id-%j.out

#conda run -n llm-parsing python /home/amansinghtha_umass_edu/llm_eval/model_output/test_mmlu.py
conda run -n llm-parsing python /home/amansinghtha_umass_edu/llm_eval/model_output/generate_model_output.py