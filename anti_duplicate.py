import json, os, time
from app.config import LAST_SIGNAL_PATH, COOLDOWN_SECONDS

def _load():
    try:
        with open(LAST_SIGNAL_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save(data):
    os.makedirs(os.path.dirname(LAST_SIGNAL_PATH), exist_ok=True)
    with open(LAST_SIGNAL_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def is_duplicate(symbol: str, direction: str) -> bool:
    now = time.time()
    key = f"{symbol}_{direction}"
    data = _load()
    if data.get("key") == key and now - float(data.get("time", 0)) < COOLDOWN_SECONDS:
        print("[SKIP] duplicate/cooldown", key)
        return True
    _save({"key": key, "time": now})
    return False
