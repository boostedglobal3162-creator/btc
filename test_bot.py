from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()

def send_test_message():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    print(f"Test mesajı gönderiliyor... (Chat ID: {chat_id})")
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "🛡️ TradeKing Test Mesajı: Botunuz başarıyla bağlandı!",
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ BAŞARILI! Telegram botunuza mesaj gelmiş olmalı.")
        else:
            print(f"❌ HATA! Telegram'dan hata döndü: {response.text}")
            print("\nİpucu: Botunuzun token'ı doğru mu? Bot'a /start mesajı attınız mı?")
    except Exception as e:
        print(f"❌ KRİTİK HATA: {e}")

if __name__ == "__main__":
    send_test_message()
