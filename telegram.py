import requests
from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram(text: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[WARN] Telegram token/chat_id missing")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
        print("[TELEGRAM]", r.text)
        return r.ok
    except Exception as e:
        print("[TELEGRAM ERROR]", e)
        return False
