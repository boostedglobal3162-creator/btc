# BTCAlertAgent (V3 Professional) 🚀

Real-time Bitcoin (BTC/USDT) monitoring, multi-indicator technical analysis, and automated Telegram alert system.

## 📁 Key Components

- `main.py`: The async event loop for real-time WebSocket streaming and buffer management.
- `analyzer.py`: Technical strategy engine (RSI, EMA, MACD, Bollinger, Scoring).
- `notifier.py`: Robust Telegram delivery system with anti-spam and scoring logic.
- `utils.py`: System utilities, SSL/DNS fixes, and helper functions.
- `logger.py`: Performance CSV logging.
- `config.json`: Centralized parameter management.

## 📊 V3 Strategy: Multi-Indicator Scoring

Unlike binary alerts, V3 uses a **Weighted Scoring System (0-100)**:
- **RSI Overbought/Oversold** (Up to 40 pts)
- **Bollinger Band Lower Breakout** (Up to 30 pts)
- **Dip Threshold Analysis** (Up to 25 pts)
- **Candle Recovery (Green check)** (10 pts)
- **Trend Filter (EMA50)**: -20 penalty if below trend.

*A total score of **≥ 70** triggers an "AL" alert.*

## 🚀 Setup & Usage

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Credentials**:
   - Update `config.json` with your Telegram Bot Token and Chat ID.
   - Use `get_chat_id.py` if you don't know your Chat ID.

3. **Run Monitoring Agent**:
   ```bash
   python main.py
   ```

## 🛡️ Resilience Features

- **Initial Buffer Warm-up**: Fetches 250 minutes of historical data on startup so indicators work instantly.
- **WebSocket Recovery**: Auto-reconnects on network drops.
- **Memory Management**: Maintain a rolling window of 300 candles to keep memory footprint low.
