#!/bin/bash

# =============================================
# HS ML Trading Bot - Launcher
# =============================================

PROJECT_DIR="/root/fast-ws-bot-main"
cd "$PROJECT_DIR"

# Активируем виртуальное окружение
source .venv/bin/activate

echo "========================================"
echo "🚀 HS ML Bot Starting..."
echo "📍 Directory: $PROJECT_DIR"
echo "📅 Time: $(date)"
echo "========================================"

# Запускаем бота
python main.py
