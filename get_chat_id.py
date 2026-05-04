import requests
import time

def get_updates(token):
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    r = requests.get(url)
    return r.json()

if __name__ == "__main__":
    token = input("Lütfen Telegram Bot Token girin: ")
    print("Botunuzu Telegram'da bulun ve ona herhangi bir mesaj gönderin...")
    
    while True:
        data = get_updates(token)
        if data["ok"] and data["result"]:
            last_msg = data["result"][-1]
            chat_id = last_msg["message"]["chat"]["id"]
            username = last_msg["message"]["chat"].get("first_name", "User")
            print(f"\n✅ Merhaba {username}! Senin Chat ID: {chat_id}")
            print(f"Bunu config.json'daki telegramChatId kısmına yazabilirsin.")
            break
        time.sleep(2)
