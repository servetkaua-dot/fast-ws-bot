import json
import os
from datetime import datetime
from collections import deque

class TradeTracker:
    def __init__(self, max_trades=200):
        self.file = "logs/trades.jsonl"
        self.trades = deque(maxlen=max_trades)
        self.load_trades()

    def load_trades(self):
        if os.path.exists(self.file):
            with open(self.file, 'r') as f:
                for line in f:
                    self.trades.append(json.loads(line.strip()))

    def add_trade(self, signal, result: str):  # result = "WIN" или "LOSS"
        trade = {
            "timestamp": datetime.utcnow().isoformat(),
            "symbol": signal["symbol"],
            "direction": signal["direction"],
            "entry": signal["entry"],
            "sl": signal.get("stop_loss"),
            "tp1": signal.get("tp1"),
            "tp2": signal.get("tp2"),
            "confidence": signal.get("confidence"),
            "result": result,          # WIN / LOSS
            "rr": signal.get("rr", 0)
        }
        self.trades.append(trade)
        
        with open(self.file, 'a') as f:
            f.write(json.dumps(trade) + '\n')

    def get_stats(self):
        if not self.trades:
            return {"total": 0, "win_rate": 0, "wins": 0, "losses": 0}
        
        wins = sum(1 for t in self.trades if t["result"] == "WIN")
        total = len(self.trades)
        win_rate = (wins / total * 100) if total > 0 else 0

        return {
            "total_trades": total,
            "wins": wins,
            "losses": total - wins,
            "win_rate": round(win_rate, 2),
            "avg_rr": round(sum(t.get("rr", 0) for t in self.trades) / total, 2) if total > 0 else 0
        }

    def print_stats(self):
        stats = self.get_stats()
        print(f"\n📊 СТАТИСТИКА ТОРГОВЛИ")
        print(f"Всего сделок: {stats.get('total_trades',0)}")
        print(f"Win Rate: {stats.get('win_rate')}% ({stats('wins',0)} WIN / {stats.get('losses',0)} LOSS)")
        print(f"Average RR: {stats.get('avg_rr',0)}")
        print("-" * 40)

# Для теста
if __name__ == "__main__":
    tracker = TradeTracker()
    tracker.print_stats()
