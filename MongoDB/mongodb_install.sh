#!/bin/bash
module load miniconda/22.11.1-1
conda activate /work/pi_dhruveshpate_umass_edu/grp22/conda/envs/llm-eval/
conda install -c conda-forge mongodb
pip install pymongo