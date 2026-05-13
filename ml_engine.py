import os, joblib, ccxt
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from app.config import MODEL_PATH

EXCHANGE = ccxt.binance({"enableRateLimit": True})

def fetch_ohlcv(symbol: str, timeframe: str = "5m", limit: int = 120) -> pd.DataFrame:
    bars = EXCHANGE.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    return pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["returns"] = df["close"].pct_change()
    df["volatility"] = df["returns"].rolling(10).std().fillna(0)
    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()
    df["ema200"] = df["close"].ewm(span=200).mean()
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["rsi"] = (100 - (100 / (1 + rs))).fillna(50)
    mid = df["close"].rolling(20).mean()
    std = df["close"].rolling(20).std()
    df["boll_mid"] = mid
    df["boll_upper"] = mid + 2 * std
    df["boll_lower"] = mid - 2 * std
    df["boll_width"] = ((df["boll_upper"] - df["boll_lower"]) / df["close"]).fillna(0)
    avg_vol = df["volume"].rolling(20).mean()
    df["volume_ratio"] = (df["volume"] / avg_vol).replace([np.inf, -np.inf], 0).fillna(0)
    return df.dropna().reset_index(drop=True)

class MLEngine:
    def __init__(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
        else:
            self.model = RandomForestClassifier(n_estimators=80, max_depth=6, random_state=42)

    def train(self, symbol: str = "ETH/USDT"):
        df = add_features(fetch_ohlcv(symbol, limit=300))
        df["target"] = (df["close"].shift(-3) > df["close"]).astype(int)
        df = df.dropna()
        features = ["returns", "volatility", "rsi", "ema20", "ema50", "ema200", "boll_width", "volume_ratio"]
        self.model.fit(df[features], df["target"])
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(self.model, MODEL_PATH)
        print("[OK] model trained:", MODEL_PATH)

    def predict(self, symbol: str) -> dict:
        df = add_features(fetch_ohlcv(symbol, limit=120))
        features = ["returns", "volatility", "rsi", "ema20", "ema50", "ema200", "boll_width", "volume_ratio"]
        last = df.iloc[-1]
        if not hasattr(self.model, "classes_"):
            self.train(symbol)
        X = df[features].tail(1)
        pred = int(self.model.predict(X)[0])
        confidence = float(max(self.model.predict_proba(X)[0]))
        recent = df.tail(40)
        return {
            "symbol": symbol,
            "direction": "LONG" if pred == 1 else "SHORT",
            "confidence": round(confidence, 4),
            "close": float(last["close"]),
            "returns": float(last["returns"]),
            "volatility": float(last["volatility"]),
            "rsi": float(last["rsi"]),
            "ema20": float(last["ema20"]),
            "ema50": float(last["ema50"]),
            "ema200": float(last["ema200"]),
            "boll_mid": float(last["boll_mid"]),
            "boll_upper": float(last["boll_upper"]),
            "boll_lower": float(last["boll_lower"]),
            "boll_width": float(last["boll_width"]),
            "volume_ratio": float(last["volume_ratio"]),
            "recent_high": float(recent["high"].max()),
            "recent_low": float(recent["low"].min()),
        }
