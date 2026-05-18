import json
import time
import asyncio
import websockets
from datetime import datetime
from app.config import (
    BINANCE_WS_SYMBOL,
    VOLUME_MULTIPLIER,
    PRICE_MOVE_LIMIT,
    MIN_VOLUME_THRESHOLD  # добавь в .env
)

WS_URL = f"wss://fstream.binance.com/ws/{BINANCE_WS_SYMBOL}@trade"

class VolumeTrigger:
    def __init__(self):
        self.volumes = []
        self.prices = []
        self.last_trigger_time = 0
        self.min_volume_threshold = MIN_VOLUME_THRESHOLD  # например 500000 для ETH

    async def listen(self, on_trigger):
        print(f"[WS] Connecting to {WS_URL}")
        reconnect_delay = 1

        while True:
            try:
                async with websockets.connect(WS_URL, ping_interval=20, ping_timeout=20) as ws:
                    print("[WS] Connected")
                    reconnect_delay = 1

                    async for msg in ws:
                        data = json.loads(msg)
                        price = float(data['p'])
                        volume = float(data['q'])
                        is_buyer_maker = data.get('m', False)  # True = sell volume

                        self.volumes.append(volume)
                        self.prices.append(price)
                        if len(self.volumes) > 60:          # храним ~5 минут (при 5m tf)
                            self.volumes.pop(0)
                            self.prices.pop(0)

                        if len(self.volumes) < 20:          # минимум данных
                            continue

                        # === УМНЫЕ ФИЛЬТРЫ ===
                        avg_volume = sum(self.volumes[-20:]) / 20
                        volume_ratio = volume / avg_volume if avg_volume > 0 else 0

                        price_move = abs(price - self.prices[-2]) if len(self.prices) > 1 else 0

                        current_time = time.time()
                        if current_time - self.last_trigger_time < 60:  # анти-спам
                            continue

                        # Основные условия
                        if (volume_ratio >= VOLUME_MULTIPLIER and 
                            volume >= self.min_volume_threshold and
                            price_move >= PRICE_MOVE_LIMIT and
                            len(self.volumes) >= 20):

                            side = "UP" if not is_buyer_maker else "DOWN"  # buyer_maker = aggressive sell

                            print(f"[TRIGGER] {side} | VolRatio: {volume_ratio:.2f} | "
                                  f"PriceMove: {price_move:.6f} | Vol: {volume:,.0f}")

                            event = {
                                "side": side,
                                "price_move": price_move,
                                "volume_ratio": round(volume_ratio, 2),
                                "close": price,
                                "time": datetime.utcnow().isoformat(),
                                "volume": volume
                            }

                            self.last_trigger_time = current_time
                            await on_trigger(event)

            except Exception as e:
                print(f"[WS ERROR] {e}")
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, 60)
