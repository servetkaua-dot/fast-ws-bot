import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from app.config import SYMBOL
from app.ml_engine import MLEngine
from app.signal_engine import build_trade_signal, format_signal
raw = MLEngine().predict(SYMBOL)
signal = build_trade_signal(raw)
print("RAW:", raw)
print("SIGNAL:", signal)
if signal: print(format_signal(signal))
