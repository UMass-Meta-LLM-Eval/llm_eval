#!/bin/bash

#SBATCH -N 1                # Number of nodes requested
#SBATCH -n 1                # Number of tasks requested
#SBATCH -p gpu-preempt      # Partition
#SBATCH -c 8                # Number of cores requested
#SBATCH -t 4:00:00          # Time (Days-Hours:Minutes:Seconds)
#SBATCH --mem=8G            # memory per node (defaults to MB without "G")
#SBATCH --gpus=1            # Number of GPUs
#SBATCH --mail-type=ALL     # Type of email notification- BEGIN,END,FAIL,ALL
#SBATCH --constraint=vram16 # GPU type
#SBATCH -J poc-llama7b      # Job Name
#SBATCH -o logs/%x-%j.out   # Standard output
#SBATCH -e logs/%x-%j.err   # Standard error

# Load the conda environment
module load miniconda/22.11.1-1
module load gcc/11.2.0
module load cuda/12.2.1
conda activate /work/pi_dhruveshpate_umass_edu/grp22/users/<<username>>/conda/envs/<<env-name>>/

# Change to the project directory
cd /work/pi_dhruveshpate_umass_edu/grp22/users/<<username>>/projects/llm_eval/

# Run the script
echo "Running main.py"
python main.py "$@" -j ${SLURM_JOBID}

# Done
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo "Job completed successfully"
else
    echo "Job failed with exit code $exit_code"
fi
