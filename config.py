import os
from dotenv import load_dotenv
load_dotenv()

SYMBOL = os.getenv("SYMBOL", "ETH/USDT")
BINANCE_WS_SYMBOL = os.getenv("BINANCE_WS_SYMBOL", "ethusdt").lower()
PRICE_MOVE_LIMIT = float(os.getenv("PRICE_MOVE_LIMIT", "0.0025"))
VOLUME_MULTIPLIER = float(os.getenv("VOLUME_MULTIPLIER", "1.8"))
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", "180"))
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.55"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

MODEL_PATH = "models/model.pkl"
LAST_SIGNAL_PATH = "data/last_signal.json"
SIGNALS_LOG_PATH = "data/signals_log.jsonl"
