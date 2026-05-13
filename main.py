import asyncio, time
from app.config import SYMBOL, COOLDOWN_SECONDS
from app.binance_ws import VolumeTrigger
from app.ml_engine import MLEngine
from app.signal_engine import build_trade_signal, format_signal
from app.telegram import send_telegram
from app.anti_duplicate import is_duplicate
from app.logger import log_signal

ml = MLEngine()
last_ml_time = 0
ml_running = False

async def on_volume_trigger(event: dict):
    global last_ml_time, ml_running
    now = time.time()
    if ml_running:
        print("[SKIP] ML already running"); return
    if now - last_ml_time < COOLDOWN_SECONDS:
        print("[SKIP] cooldown"); return
    ml_running = True; last_ml_time = now
    try:
        raw = ml.predict(SYMBOL)
        raw["trigger"] = event
        signal = build_trade_signal(raw)
        if not signal:
            print("[NO SIGNAL]", raw["symbol"], raw["direction"], raw["confidence"]); return
        if is_duplicate(signal["symbol"], signal["direction"]): return
        log_signal(signal)
        send_telegram(format_signal(signal))
    except Exception as e:
        print("[ML ERROR]", e)
    finally:
        ml_running = False

async def main():
    print("[START] WS ML bot:", SYMBOL)
    trigger = VolumeTrigger()
    await trigger.listen(on_volume_trigger)

if __name__ == "__main__":
    asyncio.run(main())
