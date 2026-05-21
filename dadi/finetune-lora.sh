export MODEL_NAME="runwayml/stable-diffusion-v1-5"
export OUTPUT_DIR="lora-remote-sensing"
export HUB_MODEL_ID="remote-sensing-lora"
export DATASET_NAME="<redacted>/EuroSAT-InstructCaptions"

accelerate launch ./diffusers/examples/text_to_image/train_text_to_image_lora.py \
  --pretrained_model_name_or_path=$MODEL_NAME \
  --dataset_name=$DATASET_NAME \
  --caption_column="caption" \
  --resolution=512 \
  --random_flip \
  --train_batch_size=1 \
  --gradient_accumulation_steps=4 \
  --num_train_epochs=20 \
  --learning_rate=1e-04 \
  --max_grad_norm=1 \
  --lr_scheduler="constant" \
  --lr_warmup_steps=0 \
  --output_dir=${OUTPUT_DIR} \
  --push_to_hub \
  --hub_model_id=${HUB_MODEL_ID} \
  --report_to=wandb \
  --checkpointing_steps=250 \
  --validation_prompt="a remote sensing image of a forest" \
  --seed=23


