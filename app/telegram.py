import asyncio
import aiohttp
from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

async def send_telegram(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Telegram] Token or Chat ID not set")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as resp:
                if resp.status != 200:
                    print(f"[Telegram Error] {resp.status} - {await resp.text()}")
    except Exception as e:
        print(f"[Telegram Exception] {e}")
      
