TASK_NAME=humaneval 
NUMBER_OF_THREAD=1
language=zh
HF_MODEL_NAME=/path/to/your/model
NUMBER_OF_THREAD=1  # 线程数，一般设为 gpu数/per-proc-gpus 
OUTPUT_BASE_PATH=/your/output/path/

Gate_path=/path/to/your/gate
language_MODEL_Path=/path/to/your/language_lora
task_model=/path/to/your/task_lora
 

for (( i=0; i<${#Gate_path[@]}; i++ )); do 
port=$((5030 + i))

URL="http://127.0.0.1:${port}/vllm-url31-infer"

nohup python URLs/vllm_url31.py \
  --task_model $task_model \
  --language_model $language_model \
  --temperature 1.0 \
  --gpuid $i  \
  --port $port  \
  --model_name $HF_MODEL_NAME \
  --gate_path ${Gate_path[$i]} &

sleep 30

python main.py \
    --model general \
    --model_args url=$URL,concurrency=$NUMBER_OF_THREAD \
    --config_path $CONFIG_PATH \
    --output_base_path $OUTPUT_BASE_PATH \
    --batch_size 8 \
    --postprocess general_torch \
    --params models/model_params/vllm_sample_wizardcode.json \
    --write_out \

done
