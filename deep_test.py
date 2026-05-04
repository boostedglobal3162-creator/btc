import pandas as pd
import json
import asyncio
from datetime import datetime, timedelta
from analyzer import BTCAnalyzer
from notifier import TelegramNotifier

async def run_force_test():
    print("🚀 [Force Test] Anti-Spam engelini aşarak bildirim zorlanıyor...")
    
    with open("config.json", "r") as f:
        config = json.load(f)

    analyzer = BTCAnalyzer(config)
    notifier = TelegramNotifier(config)
    
    # Anti-Spam filtresini BU TESTLİK sıfırlayalım ki gelsin
    notifier.last_notif = {} 

    print(f"📡 Kullanılan Chat ID: {config.get('telegramChatId')}")
    print(f"📡 Token Kontrol: {config.get('telegramToken')[:15]}...")

    # Suni Veri
    data = []
    base_p = 70000
    for i in range(210):
        data.append({"t": datetime.now(), "open": base_p, "high": base_p+10, "low": base_p-10, "close": base_p})
    df = pd.DataFrame(data).set_index("t")
    
    # DIP senaryosu
    df.loc[df.index[-1]] = [base_p, base_p, base_p*0.95, base_p*0.95]

    df = analyzer.calculate_indicators(df)
    signal_data, signal_type = analyzer.check_signals(df)

    if signal_type:
        print(f"✅ Strateji Yakaladı. Bildirim zorlanıyor...")
        result = await notifier.send_signal_msg("AL", signal_data)
        if result:
            print("💎 BAŞARILI! Telegram 'OK' yanıtı verdi.")
        else:
            print("❌ HATA: Telegram gönderimi başarısız. Lütfen Token/Chat ID doğruluğunu kontrol edin.")
            print("Not: config.json içindeki YOUR_TOKEN_HERE kısmına kendi tokeninizi yazdığınızdan emin olun.")

if __name__ == "__main__":
    asyncio.run(run_force_test())
