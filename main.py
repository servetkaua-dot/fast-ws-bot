import asyncio
import time
from datetime import datetime

from app.config import (
    SYMBOL, 
    COOLDOWN_SECONDS, 
    MIN_CONFIDENCE,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID
)

from app.binance_ws import VolumeTrigger
from app.ml_engine import MLEngine
from app.signal_engine import build_trade_signal
from app.telegram import send_telegram
from app.anti_duplicate import is_duplicate
from app.logger import log_signal, save_signal

# Глобальные переменные для контроля
last_ml_time = 0
ml_running = False
ml = MLEngine()  # инициализация модели один раз


async def on_volume_trigger(event: dict):
    global last_ml_time, ml_running

    now = time.time()

    # === Защита от одновременного запуска ===
    if ml_running:
        print("[SKIP] ML already running")
        return

    # === Cooldown ===
    if now - last_ml_time < COOLDOWN_SECONDS:
        print(f"[SKIP] cooldown {int(now - last_ml_time)}s")
        return

    ml_running = True
    last_ml_time = now

    try:
        print(f"[ML] Starting prediction for {SYMBOL}...")

        raw = ml.predict(SYMBOL)
        if not raw:
            print("[NO SIGNAL] Model returned nothing")
            return

        signal = build_trade_signal(raw)

        if not signal:
            print(f"[NO SIGNAL] Low confidence or invalid | Conf: {raw.get('confidence',0):.3f}")
            return

        # Проверка на дубликат
        if is_duplicate(signal["symbol"], signal["direction"]):
            print("[DUPLICATE] Signal already sent recently")
            return

        # Логирование и отправка
        log_signal(signal)
        save_signal(signal)
        
        telegram_text = f"""
🟢 <b>NEW SIGNAL</b>

Symbol: <b>{signal['symbol']}</b>
Direction: <b>{signal['direction']}</b>
Entry: <b>{signal['entry']}</b>
Stop Loss: <b>{signal['stop_loss']}</b>
TP1: <b>{signal['tp1']}</b>
TP2: <b>{signal['tp2']}</b>
Confidence: <b>{signal['confidence']*100:.1f}%</b>
        """.strip()

        await send_telegram(telegram_text)

        print(f"[SUCCESS] Signal sent → {signal['direction']} {signal['symbol']}")

    except Exception as e:
        print(f"[ML ERROR] {e}")
    finally:
        ml_running = False


async def main():
    print(f"[START] HS ML Bot started → {SYMBOL} | {datetime.utcnow().isoformat()}")
    
    trigger = VolumeTrigger()
    await trigger.listen(on_volume_trigger)


if __name__ == "__main__":
    asyncio.run(main())
