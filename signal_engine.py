import pandas as pd
from app.ml_engine import fetch_ohlcv

def build_trade_signal(raw_ml: dict):
    if not raw_ml or raw_ml.get("confidence", 0) < 0.58:
        return None

    symbol = raw_ml["symbol"]
    direction = raw_ml["direction"]
    entry = raw_ml["close"]

    # ATR-based levels
    df = fetch_ohlcv(symbol, limit=100)
    tr = pd.concat([
        df['high'] - df['low'],
        (df['high'] - df['close'].shift()).abs(),
        (df['low'] - df['close'].shift()).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(14).mean().iloc[-1]

    risk = atr * 1.6
    reward1 = atr * 2.2
    reward2 = atr * 3.8

    if direction == "LONG":
        sl = entry - risk
        tp1 = entry + reward1
        tp2 = entry + reward2
    else:
        sl = entry + risk
        tp1 = entry - reward1
        tp2 = entry - reward2

    return {
        "symbol": symbol,
        "direction": direction,
        "entry": round(entry, 4),
        "stop_loss": round(sl, 4),
        "tp1": round(tp1, 4),
        "tp2": round(tp2, 4),
        "confidence": raw_ml["confidence"],
        "timestamp": datetime.utcnow().isoformat()
    }
