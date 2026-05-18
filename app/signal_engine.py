import pandas as pd
from datetime import datetime
from app.config import MIN_CONFIDENCE
from app.ml_engine import fetch_ohlcv


def calculate_risk(raw: dict) -> dict:
    """Динамический расчёт SL/TP через ATR"""
    symbol = raw["symbol"]
    direction = raw["direction"]
    entry = raw["close"]
def calculate_risk(raw: dict) -> dict | None:
    try:
        entry = raw.get("close", 0)
        direction = raw.get("direction")
        symbol = raw.get("symbol", SYMBOL)

        # Bollinger Bands (должны приходить из ml_engine)
        bb_upper = raw.get("bb_upper", entry * 1.008)
        bb_middle = raw.get("bb_middle", entry)
        bb_lower = raw.get("bb_lower", entry * 0.992)

        if direction == "SHORT":
            # Stop Loss — выше верхней Bollinger
            sl = bb_upper * 1.003
            # TP ближе к Bollinger
            tp1 = bb_middle * 0.997
            tp2 = bb_lower * 1.003

        else:  # LONG
            # Stop Loss — ниже нижней Bollinger
            sl = bb_lower * 0.997
            # TP ближе к Bollinger
            tp1 = bb_middle * 1.003
            tp2 = bb_upper * 0.997

        risk = abs(entry - sl)
        rr = abs(tp1 - entry) / risk if risk > 0 else 2.2

        return {
            "symbol": symbol,
            "direction": direction,
            "entry": round(entry, 4),
            "stop_loss": round(sl, 4),
            "tp1": round(tp1, 4),
            "tp2": round(tp2, 4),
            "confidence": raw.get("confidence", 0.0),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        print(f"[RISK ERROR] {e}")
        # Fallback (оставляем твой старый)
        risk_pct = 0.012
        tp1_pct = 0.022
        tp2_pct = 0.045
        if direction == "LONG":
            return {
                "symbol": symbol,
                "direction": direction,
                "entry": round(entry, 4),
                "stop_loss": round(entry * (1 - risk_pct), 4),
                "tp1": round(entry * (1 + tp1_pct), 4),
                "tp2": round(entry * (1 + tp2_pct), 4),
                "confidence": raw.get("confidence", 0.0),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:  # SHORT fallback
            return {
                "symbol": symbol,
                "direction": direction,
                "entry": round(entry, 4),
                "stop_loss": round(entry * (1 + risk_pct), 4),
                "tp1": round(entry * (1 - tp1_pct), 4),
                "tp2": round(entry * (1 - tp2_pct), 4),
                "confidence": raw.get("confidence", 0.0),
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
