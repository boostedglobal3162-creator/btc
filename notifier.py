import requests
import os
from datetime import datetime, timedelta

class TelegramNotifier:
    """V4: High-Confidence Notifier with MTF and Score Details."""
    def __init__(self, config):
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.spam_interval = config.get("spamIntervalSec", 300)
        self.last_notif = {}  

    def can_notify(self, signal_type):
        """Prevents notification fatigue by checking interval."""
        if signal_type not in self.last_notif:
            return True
        last_time = self.last_notif[signal_type]
        return (datetime.now() - last_time) > timedelta(seconds=self.spam_interval)

    async def send_signal_msg(self, signal_type, data):
        """Sends rich V4 formatted Telegram messages."""
        if not self.token or "YOUR" in self.token: return False
        if not self.can_notify(signal_type): return False

        emoji = "🟢" if signal_type == "AL" else "🔴"
        score_val = data.get("score", 0)
        trend_val = data.get("trend", "N/A")
        
        score_str = f"\nGüven Skoru: `{score_val}/100`" if signal_type == "AL" else ""
        trend_str = f"\n5m Trend: `{'✅ Bullish' if trend_val == 'BULLISH' else '⚠️ Mixed'}`" if signal_type == "AL" else ""
        
        title = "AL SINYALI (Onaylı)" if signal_type == "AL" else "SAT / KAR AL"
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        v_str = f"{data['vol']:.2%}" if data.get('vol') else "0.00%"
        
        msg = (
            f"{emoji} *BTC {title}*{score_str}{trend_str}\n\n"
            f"Fiyat: `{data['price']:.2f}` USDT\n"
            f"RSI: `{data['rsi']:.2f}`\n"
            f"EMA50: `{data['ema']:.2f}`\n"
            f"MACD Delta: `{data['macd']:.2f}`\n"
            f"Volatility (5m): `{v_str}`\n"
            f"Zaman: `{timestamp}`\n"
            f"\n_V4 Professional MTF Agent_"
        )

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        try:
            r = requests.post(url, json={"chat_id": self.chat_id, "text": msg, "parse_mode": "Markdown"}, timeout=10)
            if r.status_code == 200:
                self.last_notif[signal_type] = datetime.now()
                return True
            else:
                print(f"[Notifier] Telegram Error {r.status_code}: {r.text}")
        except Exception as e:
            print(f"[Notifier] Exception: {e}")
        return False

    async def send_news_alert(self, news_data):
        """Sends standalone high-impact news notification."""
        if not self.token or "YOUR" in self.token: return False

        title = news_data.get("title", "Market Update")
        sentiment = news_data.get("sentiment", "Neutral")
        url = news_data.get("url", "https://cryptopanic.com")
        source = news_data.get("source", "CryptoPanic")

        msg = (
            f"🗞️ *FLAŞ HABER (BTC)*\n\n"
            f"*{title}*\n\n"
            f"Duyarlılık: `{sentiment}`\n"
            f"Kaynak: `{source}`\n"
            f"[Haberi Oku]({url})\n"
            f"\n_TradeKing News Sentinel_"
        )

        url_api = f"https://api.telegram.org/bot{self.token}/sendMessage"
        try:
            requests.post(url_api, json={"chat_id": self.chat_id, "text": msg, "parse_mode": "Markdown", "disable_web_page_preview": False}, timeout=10)
            return True
        except Exception as e:
            print(f"[News Notifier Error] {e}")
            return False
