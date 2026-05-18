import pandas as pd
from datetime import datetime
from app.config import MIN_CONFIDENCE
from app.ml_engine import fetch_ohlcv


def calculate_risk(raw: dict) -> dict:
    """Динамический расчёт SL/TP через ATR"""
    symbol = raw["symbol"]
    direction = raw["direction"]
    entry = raw["close"]

    try:
        df = fetch_ohlcv(symbol, "5m", limit=150)
        
        # ATR
        tr = pd.concat([
            df['high'] - df['low'],
            (df['high'] - df['close'].shift()).abs(),
            (df['low'] - df['close'].shift()).abs()
        ], axis=1).max(axis=1)
        
        atr = tr.rolling(14).mean().iloc[-1]

        if pd.isna(atr) or atr <= 0:
            atr = entry * 0.008  # fallback

        risk = atr * 1.65
        tp1_dist = atr * 2.4
        tp2_dist = atr * 4.1

        if direction == "LONG":
            sl = entry - risk
            tp1 = entry + tp1_dist
            tp2 = entry + tp2_dist
        else:
            sl = entry + risk
            tp1 = entry - tp1_dist
            tp2 = entry - tp2_dist

        return {
            "symbol": symbol,
            "direction": direction,
            "entry": round(entry, 4),
            "stop_loss": round(sl, 4),
            "tp1": round(tp1, 4),
            "tp2": round(tp2, 4),
            "confidence": raw["confidence"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except:
        # Fallback
        risk_pct = 0.012
        tp1_pct = 0.022
        tp2_pct = 0.045
        if direction == "LONG":
            return {
                "symbol": symbol, "direction": direction, "entry": round(entry, 4),
                "stop_loss": round(entry * (1 - risk_pct), 4),
                "tp1": round(entry * (1 + tp1_pct), 4),
                "tp2": round(entry * (1 + tp2_pct), 4),
                "confidence": raw["confidence"],
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "symbol": symbol, "direction": direction, "entry": round(entry, 4),
                "stop_loss": round(entry * (1 + risk_pct), 4),
                "tp1": round(entry * (1 - tp1_pct), 4),
                "tp2": round(entry * (1 - tp2_pct), 4),
                "confidence": raw["confidence"],
                "timestamp": datetime.utcnow().isoformat()
            }


def build_trade_signal(raw: dict):
    direction = raw.get("direction")
    close = raw.get("close")
    rsi = raw.get("rsi", 50)
    ema20 = raw.get("ema20")
    ema50 = raw.get("ema50")
    volume_ratio = raw.get("volume_ratio", 0)
    confidence = raw.get("confidence", 0)

    if confidence < MIN_CONFIDENCE:
        return None

    # Фильтры
    if direction == "LONG":
        if rsi > 82 or (close < ema20 and close < ema50):
            return None
    elif direction == "SHORT":
        if rsi < 18 or (close > ema20 and close > ema50):
            return None

    if volume_ratio < 0.35:
        return None

    return calculate_risk(raw)


def format_signal(signal: dict) -> str:
    return f"""
🟢 <b>NEW SIGNAL</b> 🟢

Symbol: <b>{signal['symbol']}</b>
Direction: <b>{signal['direction']}</b>
Entry: <b>{signal['entry']}</b>
Stop Loss: <b>{signal['stop_loss']}</b>
TP1: <b>{signal['tp1']}</b>
TP2: <b>{signal['tp2']}</b>
Confidence: <b>{signal['confidence']*100:.1f}%</b>
    """.strip()
