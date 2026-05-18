import json
import time
from app.config import LAST_SIGNAL_PATH

last_signals = {}

def is_duplicate(symbol: str, direction: str, cooldown_minutes: int = 30) -> bool:
    key = f"{symbol}_{direction}"
    now = time.time()

    if key in last_signals and now - last_signals[key] < cooldown_minutes * 60:
        return True

    last_signals[key] = now
    return False
