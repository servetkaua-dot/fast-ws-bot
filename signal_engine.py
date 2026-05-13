from app.config import MIN_CONFIDENCE
from app.risk import calculate_risk

def build_trade_signal(raw: dict) -> dict | None:
    direction = raw["direction"]
    close = raw["close"]
    rsi = raw["rsi"]
    ema20 = raw["ema20"]
    ema50 = raw["ema50"]
    volume_ratio = raw["volume_ratio"]
    confidence = raw["confidence"]

    if confidence < MIN_CONFIDENCE:
        return None

    if direction == "LONG":
        if rsi > 82: return None
        if close < ema20 and close < ema50: return None

    if direction == "SHORT":
        if rsi < 18: return None
        if close > ema20 and close > ema50: return None

    if volume_ratio < 0.6:
        return None

    return calculate_risk(dict(raw))

def format_signal(signal: dict) -> str:
    return (
        f"🔥 {signal['symbol']}\n"
        f"Direction: {signal['direction']}\n"
        f"Entry: {signal.get('entry')}\n"
        f"Stop Loss: {signal.get('stop_loss')}\n"
        f"TP1: {signal.get('tp1')}\n"
        f"TP2: {signal.get('tp2')}\n"
        f"Confidence: {signal.get('confidence')}"
    )
