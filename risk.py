def calculate_risk(signal: dict) -> dict:
    direction = signal["direction"]
    close = float(signal["close"])
    boll_mid = float(signal["boll_mid"])
    boll_upper = float(signal["boll_upper"])
    boll_lower = float(signal["boll_lower"])
    recent_high = float(signal["recent_high"])
    recent_low = float(signal["recent_low"])
    buffer = close * 0.001

    if direction == "LONG":
        entry = min(close, boll_mid)
        stop_loss = recent_low - buffer
        risk = max(entry - stop_loss, close * 0.001)
        tp1 = max(boll_upper, entry + risk)
        tp2 = max(recent_high, entry + risk * 2)
    elif direction == "SHORT":
        entry = max(close, boll_mid)
        stop_loss = recent_high + buffer
        risk = max(stop_loss - entry, close * 0.001)
        tp1 = min(boll_lower, entry - risk)
        tp2 = min(recent_low, entry - risk * 2)
    else:
        entry = close; stop_loss = None; tp1 = None; tp2 = None

    signal.update({
        "entry": round(entry, 4),
        "stop_loss": round(stop_loss, 4) if stop_loss else None,
        "tp1": round(tp1, 4) if tp1 else None,
        "tp2": round(tp2, 4) if tp2 else None,
    })
    return signal
