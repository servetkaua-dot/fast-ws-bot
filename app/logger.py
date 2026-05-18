import json
from datetime import datetime
from app.config import SIGNALS_LOG_PATH

def save_signal(signal: dict):
    try:
        with open(SIGNALS_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(signal, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[Logger Error] {e}")

def log_signal(signal: dict):
    print(f"[LOG] {signal['direction']} {signal['symbol']} | Conf: {signal.get('confidence',0):.3f}")
