import sys
from trade_tracker import TradeTracker

tracker = TradeTracker()

if len(sys.argv) < 3:
    print("Использование: python mark_trade.py WIN или LOSS")
    sys.exit(1)

result = sys.argv[1].upper()
print(f"Отмечаем последнюю сделку как: {result}")

# Берём последний сигнал
import json
with open("last_signal.json", "r") as f:
    signal = json.load(f)

tracker.add_trade(signal, result)
tracker.print_stats()
