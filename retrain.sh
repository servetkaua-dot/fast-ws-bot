#!/bin/bash
cd /root/fast-ws-bot-main
source .venv/bin/activate

echo "=== avomatic open: $(date) ===" >> logs/retrain.log
python train_model.py >> logs/retrain. log 2>&1
if [ $? -eq 0 ]; then
    echo "model ok train &(date)" >> logs/retrain.log
    echo "model good train" | systemd-cat -t retrain-bot
else
    echo "error $(date)" >> logs/retrain.log
