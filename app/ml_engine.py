import ccxt
import pandas as pd
import pandas_ta as ta
import numpy as np
import joblib
import os
from datetime import datetime
from app.config import SYMBOL, MODEL_PATH

class MLEngine:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
            print(f"[ML] Model loaded from {MODEL_PATH}")
        else:
            print(f"[ML] No model found at {MODEL_PATH}. Run train_model.py first.")

    def fetch_ohlcv(self, symbol: str = None, limit: int = 5000):
        if symbol is None:
            symbol = SYMBOL
        exchange = ccxt.binance()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='5m', limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Основные индикаторы
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(20).std()

        # RSI
        df['rsi'] = ta.momentum.rsi(df['close'], window=14)

        # EMA
        df['ema20'] = ta.trend.ema_indicator(df['close'], window=20)
        df['ema50'] = ta.trend.ema_indicator(df['close'], window=50)

        # Bollinger Bands
        bb = ta.volatility.BollingerBands(close=df['close'], window=20, window_dev=2)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_middle'] = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_width'] = bb.bollinger_wband()

        # ATR
        df['atr'] = ta.volatility.atr(df['high'], df['low'], df['close'], window=14)

        # Volume features
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
        df['volume_ma'] = df['volume'].rolling(20).mean()

        df = df.dropna()
        return df

    def predict(self, symbol: str = None):
        if self.model is None:
            self.load_model()
            if self.model is None:
                return None

        try:
            df = self.fetch_ohlcv(symbol, limit=500)
            df = self.add_features(df)

            if len(df) < 50:
                print("[ML] Not enough data")
                return None

            latest = df.iloc[-1]
            features = [col for col in df.columns if col not in ['timestamp', 'close', 'open', 'high', 'low']]

            X = df[features].iloc[-1:].values

            prob = self.model.predict_proba(X)[0]
            confidence = max(prob)
            direction = "LONG" if prob[1] > prob[0] else "SHORT"

            result = {
                "direction": direction,
                "confidence": float(confidence),
                "close": float(latest['close']),
                "rsi": float(latest['rsi']),
                "ema20": float(latest['ema20']),
                "ema50": float(latest['ema50']),
                "volume_ratio": float(latest['volume_ratio']),
                # Bollinger Bands для calculate_risk
                "bb_upper": float(latest['bb_upper']),
                "bb_middle": float(latest['bb_middle']),
                "bb_lower": float(latest['bb_lower']),
                "bb_width": float(latest.get('bb_width', 0)),
                "atr": float(latest.get('atr', latest['close'] * 0.004))
            }

            print(f"[ML] Predict: {direction} | Conf: {confidence:.4f} | Price: {latest['close']:.2f}")
            return result

        except Exception as e:
            print(f"[ML ERROR] {e}")
            return None


# Для теста
if __name__ == "__main__":
    ml = MLEngine()
    result = ml.predict()
    print(result)
