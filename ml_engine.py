import os
import joblib
import pandas as pd
import numpy as np
import lightgbm as lgb
from datetime import datetime
from app.config import MODEL_PATH
import ccxt

EXCHANGE = ccxt.binance({"enableRateLimit": True})

def fetch_ohlcv(symbol: str, timeframe: str = "5m", limit: int = 2000):
    bars = EXCHANGE.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["returns"] = df["close"].pct_change()
    df["volatility"] = df["returns"].rolling(14).std()
    
    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()
    df["ema200"] = df["close"].ewm(span=200).mean()
    
    df["rsi"] = 100 - (100 / (1 + (df["returns"].clip(lower=0).rolling(14).mean() / 
                                 df["returns"].clip(upper=0).abs().rolling(14).mean())))
    
    # Bollinger
    mid = df["close"].rolling(20).mean()
    std = df["close"].rolling(20).std()
    df["boll_width"] = (mid + 2*std - (mid - 2*std)) / df["close"]
    
    df["volume_ratio"] = df["volume"] / df["volume"].rolling(30).mean()
    
    # === Новый сильный target ===
    future_bars = 6  # ~30 минут
    df["future_return"] = df["close"].shift(-future_bars) / df["close"] - 1
    df["target"] = (df["future_return"] > 0.0018).astype(int)   # > 0.18% профита

    return df.dropna().reset_index(drop=True)

class MLEngine:
    def __init__(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
            print(f"[ML] Model loaded: {MODEL_PATH}")
        else:
            self.model = None
            print("[ML] No model found. Train first.")

    def train(self, symbol: str = None):
        if not symbol:
            from app.config import SYMBOL
            symbol = SYMBOL

        print(f"[ML] Training on {symbol}...")
        df = fetch_ohlcv(symbol, limit=5000)
        df = add_features(df)

        features = ["returns", "volatility", "rsi", "ema20", "ema50", "boll_width", "volume_ratio"]
        X = df[features]
        y = df["target"]

        train_data = lgb.Dataset(X, label=y)

        params = {
            'objective': 'binary',
            'metric': 'auc',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'verbose': -1,
            'random_state': 42
        }

        self.model = lgb.train(params, train_data, num_boost_round=300)
        
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(self.model, MODEL_PATH)
        print(f"[OK] Model trained and saved: {MODEL_PATH}")

    def predict(self, symbol: str) -> dict:
        if self.model is None:
            self.train(symbol)

        df = fetch_ohlcv(symbol, limit=500)
        df = add_features(df)
        if len(df) < 10:
            return None

        features = ["returns", "volatility", "rsi", "ema20", "ema50", "boll_width", "volume_ratio"]
        X = df[features].iloc[-1:].copy()

        prob = float(self.model.predict(X)[0])
        pred = 1 if prob > 0.58 else 0   # можно поднять до 0.6+

        direction = "LONG" if pred == 1 else "SHORT"
        confidence = prob if direction == "LONG" else (1 - prob)

        last = df.iloc[-1]

        return {
            "symbol": symbol,
            "direction": direction,
            "confidence": round(confidence, 4),
            "close": round(float(last["close"]), 4),
            # ... остальные фичи по желанию
        }
