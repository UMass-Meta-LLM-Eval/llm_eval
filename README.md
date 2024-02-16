# README

Project root on unity: `/work/pi_dhruveshpate_umass_edu/grp22/`

Repo: `/work/pi_dhruveshpate_umass_edu/grp22/src/llm_eval`

Conda env: `/work/pi_dhruveshpate_umass_edu/grp22/conda/envs/llm-eval`

## Setup

Activate a CPU interactive session and load modules:

```bash
salloc -N 1 -n 1 -p cpu-preempt -t 2:00:00 --mem=8G
source activate-cpu.sh
```

Activate a GPU interactive session and load modules:

```bash
salloc -N 1 -n 1 -p gpu-preempt -t 2:00:00 --mem=8G --gpus=1
source activate-gpu.sh
```

For bigger GPU, set the constraint

```bash
salloc -N 1 -n 1 -p gpu,gpu-preempt -t 2:00:00 --mem=8G --gpus=1 --constraint="[a100|m40|rtx8000]"
```