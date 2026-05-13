import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from app.config import SYMBOL
from app.ml_engine import MLEngine
if __name__ == "__main__":
    MLEngine().train(SYMBOL)
