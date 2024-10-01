
### 1. Download LoRA ckpts and gates(optional).

# export HF_ENDPOINT=https://hf-mirror.com

mkdir -p ./checkpoints

# huggingface-cli download --token xxxxx --resume-download Bowen232/LoRA-Flow --local-dir ./checkpoints


### 2. transform lora to bmversion. 
#(SKIP THIS NOTE IF YOU DON'T TRAIN LORA FROM SCRATCH USING BMTRAIN: 
# Note that this .py can also transform bm lora to peft lora, and you need to add adapter_config.json manually.)

mkdir -p ./checkpoints/BM_LoRAs

LoRA_names=("zh" "es" "ru" "math" "code")

for LoRA_name in "${LoRA_names[@]}"; do
    python scripts/transform_lora.py \
        --input_model_path "./checkpoints/LoRAs/${LoRA_name}_lora" \
        --output_model_path "./checkpoints/BM_LoRAs/${LoRA_name}" \
        --direction "peft2malign" &&  # malign2peft

    echo "Finishing transform ${LoRA_name} lora to bmtrain format."

done


### 3. transform llama2-7b-hf to llama2-7b-mc

# python scripts/transform_llama_to_bmtrain.py "/path/to/your/llama2-7b-hf" "./checkpoints/Llama-2-7b-mc" &&
# echo "Finishing transform llama2-7b-hf to bmtrain format."