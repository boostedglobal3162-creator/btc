import csv
import os
from datetime import datetime

class SignalLogger:
    def __init__(self, filename="signals_log.csv"):
        self.filename = filename
        self._init_file()

    def _init_file(self):
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "price", "rsi", "ema50", "macd", "volatility", "signal_type", "score", "trend"])

    def log_signal(self, data, signal_type):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        v_str = f"{data['vol']:.2%}" if data.get('vol') else "0.00%"
        score = data.get('score', 'N/A')
        trend = data.get('trend', 'N/A')
        with open(self.filename, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, data['price'], f"{data['rsi']:.2f}", f"{data['ema']:.2f}", f"{data['macd']:.2f}", v_str, signal_type, score, trend])
        print(f"[{timestamp}] Logged: {signal_type} (Score: {score})")
