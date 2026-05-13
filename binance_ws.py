import json, time, websockets
from app.config import BINANCE_WS_SYMBOL, PRICE_MOVE_LIMIT, VOLUME_MULTIPLIER

WS_URL = f"wss://fstream.binance.com/ws/{BINANCE_WS_SYMBOL}@kline_1m"

class VolumeTrigger:
    def __init__(self):
        self.volumes = []

    async def listen(self, on_trigger):
        print("[WS] connecting:", WS_URL)
        while True:
            try:
                async with websockets.connect(WS_URL, ping_interval=20, ping_timeout=20) as ws:
                    print("[WS] connected")
                    async for msg in ws:
                        data = json.loads(msg)
                        k = data.get("k", {})
                        if not k: continue
                        close = float(k["c"]); open_ = float(k["o"]); volume = float(k["v"])
                        self.volumes.append(volume); self.volumes = self.volumes[-30:]
                        if len(self.volumes) < 20: continue
                        avg = sum(self.volumes[:-1]) / max(len(self.volumes[:-1]), 1)
                        volume_ratio = volume / avg if avg else 0
                        price_move = (close - open_) / open_ if open_ else 0
                        if abs(price_move) >= PRICE_MOVE_LIMIT and volume_ratio >= VOLUME_MULTIPLIER:
                            side = "UP" if price_move > 0 else "DOWN"
                            print("[TRIGGER]", side, round(price_move*100, 3), "vol", round(volume_ratio, 2))
                            await on_trigger({"side": side, "price_move": price_move, "volume_ratio": volume_ratio, "close": close, "time": time.time()})
            except Exception as e:
                print("[WS ERROR]", e)
                time.sleep(5)
