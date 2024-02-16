# README

Project root on unity: `/work/pi_dhruveshpate_umass_edu/grp22/`

Repo: `/work/pi_dhruveshpate_umass_edu/grp22/src/llm_eval`

Conda env: `/work/pi_dhruveshpate_umass_edu/grp22/conda/envs/llm-eval`

pip install -r requirements.txt

conda create --name llm-parsing python=3.9.7 pip

Hugging face Login
https://huggingface.co/docs/huggingface_hub/en/quick-start

srun  --partition gpu-preempt --gres=gpu:1 -t 0-01:00:00 --pty --constraint=a100 conda run -n llm-parsing p
ython /home/amansinghtha_umass_edu/llm_eval/model_output/test.py


