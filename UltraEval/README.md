We use UltraEval for evaluating the performance.
first, install eval envs:
```
conda create -n loraflow-eval python=3.10.13 -y
conda activate loraflow-eval
pip install -r eval_env.txt
pip uninstall torch xformers -y
pip install xformers==0.0.23.post1 --index-url https://download.pytorch.org/whl/cu118
pip install torch==2.1.2 --index-url https://download.pytorch.org/whl/cu118
```
<!-- Then cd ./lora-fusion
install modifed peft and transformers library using pip. For example:
```
cd ./trasformers
pip install -e .
``` -->
