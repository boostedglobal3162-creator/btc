import requests
import json
import asyncio
from datetime import datetime

class NewsSentinel:
    """V5: Monitors CryptoPanic for high-impact market news and sentiment."""
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://cryptopanic.com/api/v1/posts/"
        self.last_news_id = None

    async def fetch_latest_news(self):
        """Fetches latest Bitcoin news and filters for significance."""
        if not self.api_key or "YOUR" in self.api_key:
            return None

        params = {
            "auth_token": self.api_key,
            "currencies": "BTC",
            "filter": "important", # Only important news
            "public": "true"
        }

        try:
            # Using requests in a non-blocking way if possible, or simple loop
            response = requests.get(self.base_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                if not results: return None
                
                latest = results[0]
                if latest['id'] != self.last_news_id:
                    self.last_news_id = latest['id']
                    return self.process_news_item(latest)
            return None
        except Exception as e:
            print(f"[News Error] {e}")
            return None

    def process_news_item(self, item):
        """Parses news item and prepares data for notification."""
        title = item.get("title")
        url = item.get("url")
        votes = item.get("votes", {})
        
        # Simple sentiment logic
        positive = votes.get("bullish", 0) + votes.get("positive", 0)
        negative = votes.get("bearish", 0) + votes.get("negative", 0)
        
        sentiment = "Neutral"
        if positive > negative * 2 and positive > 5:
            sentiment = "Bullish 📈"
        elif negative > positive * 2 and negative > 5:
            sentiment = "Bearish 📉"

        return {
            "title": title,
            "url": url,
            "sentiment": sentiment,
            "source": item.get("domain"),
            "published_at": item.get("published_at")
        }
