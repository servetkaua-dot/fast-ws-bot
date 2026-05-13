import json, os
from datetime import datetime, timezone
from app.config import SIGNALS_LOG_PATH

def log_signal(signal: dict):
    os.makedirs(os.path.dirname(SIGNALS_LOG_PATH), exist_ok=True)
    row = dict(signal)
    row["logged_at"] = datetime.now(timezone.utc).isoformat()
    with open(SIGNALS_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
