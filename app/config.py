import os
from dotenv import load_dotenv

load_dotenv()

SYMBOL = os.getenv("SYMBOL", "ETH/USDT")
BINANCE_WS_SYMBOL = os.getenv("BINANCE_WS_SYMBOL", "ethusdt").lower()

# Volume Trigger
VOLUME_MULTIPLIER = float(os.getenv("VOLUME_MULTIPLIER", 2.8))
PRICE_MOVE_LIMIT = float(os.getenv("PRICE_MOVE_LIMIT", 0.0005))
MIN_VOLUME_THRESHOLD = float(os.getenv("MIN_VOLUME_THRESHOLD", 450000))

# ML & Trading
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", 600))
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", 0.58))

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# Paths
MODEL_PATH = "models/model.pkl"
SIGNALS_LOG_PATH = "data/signals_log.json"
LAST_SIGNAL_PATH = "data/last_signal.json"
