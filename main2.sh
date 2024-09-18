#!/bin/bash

#SBATCH -N 1                # Number of nodes requested
#SBATCH -n 1                # Number of tasks requested
#SBATCH -p gpu-preempt      # Partition
#SBATCH -c 8                # Number of cores requested
#SBATCH -t 1:00:00          # Time (Days-Hours:Minutes:Seconds)
#SBATCH --mem=8G            # memory per node (defaults to MB without "G")
#SBATCH --gpus=2            # Number of GPUs
#SBATCH --mail-type=ALL     # Type of email notification- BEGIN,END,FAIL,ALL
#SBATCH -J poc-llama7b      # Job Name
#SBATCH --constraint=a100   # GPU type
#SBATCH -o logs/%x-%j.out   # Standard output
#SBATCH -e logs/%x-%j.err   # Standard error

# Load the conda environment
module load miniconda/22.11.1-1
module load gcc/11.2.0
module load cuda/12.2.1
conda activate llm-parsing

# Change to the project directory
cd /home/amansinghtha_umass_edu/llm_eval_vAug25/llm_eval/

# Run the script
echo "Running main.py"
python main.py -e chat/configV1_ChatLlama270B

# Done
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo "Job completed successfully"
else
    echo "Job failed with exit code $exit_code"
fi
