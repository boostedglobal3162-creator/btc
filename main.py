import json
import asyncio
import os
import pandas as pd
from datetime import datetime
from binance import AsyncClient, BinanceSocketManager
from analyzer import BTCAnalyzer
from notifier import TelegramNotifier
from logger import SignalLogger
from utils import apply_system_fixes
from news_fetcher import NewsSentinel
from dotenv import load_dotenv

# Environment variables loading
load_dotenv()

async def news_loop(sentinel, notifier):
    """Background task to fetch news every 5 minutes."""
    print("[News] Global Sentinel başlatıldı. Haberler takip ediliyor...")
    while True:
        try:
            news = await sentinel.fetch_latest_news()
            if news:
                print(f"🗞️ Flaşı Haber: {news['title']}")
                await notifier.send_news_alert(news)
        except Exception as e:
            print(f"[News Loop Error] {e}")
        await asyncio.sleep(300) # 5 dakikada bir kontrol

async def run_agent():
    """V5: Global Sentinel Agent with Real-Time News + MTF Analysis."""
    with open("config.json", "r") as f:
        config = json.load(f)

    analyzer = BTCAnalyzer(config)
    notifier = TelegramNotifier(config)
    logger = SignalLogger()
    sentinel = NewsSentinel(os.getenv("CRYPTO_PANIC_API_KEY"))
    
    # Start News Loop as background task
    asyncio.create_task(news_loop(sentinel, notifier))
    
    cols = ["open", "high", "low", "close", "volume"]
    df_1m = pd.DataFrame(columns=cols)
    df_5m = pd.DataFrame(columns=cols)
    
    print("💎 TradeKing V5 (Global Sentinel) Başlatılıyor...")

    while True:
        try:
            # Server compatibility: Trying global 'com' instead of regional 'me'
            client = await AsyncClient.create(tld='com')
            
            # --- 📚 Warm-up ---
            print("[Buffer] Warm-up: 1m ve 5m geçmiş verileri yükleniyor...")
            k1m = await client.get_historical_klines("BTCUSDT", "1m", "300 minutes ago UTC")
            k5m = await client.get_historical_klines("BTCUSDT", "5m", "1000 minutes ago UTC")
            
            def process_klines(klines):
                rows = []
                for k in klines:
                    rows.append({
                        "t": pd.to_datetime(k[0], unit='ms'),
                        "open": float(k[1]), "high": float(k[2]), "low": float(k[3]), "close": float(k[4]), "volume": float(k[5])
                    })
                return pd.DataFrame(rows).drop_duplicates('t').set_index("t")

            df_1m = process_klines(k1m)
            df_5m = process_klines(k5m)

            bm = BinanceSocketManager(client)
            ms = bm.multiplex_socket(['btcusdt@kline_1m', 'btcusdt@kline_5m'])
            
            print("[Monitor] V5 Aktif. Grafik + Haber Taraması Başladı.")

            async with ms as tscm:
                while True:
                    res = await tscm.recv()
                    if not res or 'data' not in res: continue
                    
                    k = res['data']['k']
                    itv = k['i']
                    timestamp = pd.to_datetime(k['t'], unit='ms')
                    vals = [float(k['o']), float(k['h']), float(k['l']), float(k['c']), float(k['v'])]
                    is_closed = k['x']

                    target_df = df_1m if itv == '1m' else df_5m
                    
                    if timestamp in target_df.index:
                        target_df.at[timestamp, 'open'] = vals[0]
                        target_df.at[timestamp, 'high'] = vals[1]
                        target_df.at[timestamp, 'low'] = vals[2]
                        target_df.at[timestamp, 'close'] = vals[3]
                        target_df.at[timestamp, 'volume'] = vals[4]
                    else:
                        new_row = pd.DataFrame([vals], columns=cols, index=[timestamp])
                        if itv == '1m':
                            df_1m = pd.concat([df_1m, new_row]).iloc[-301:]
                        else:
                            df_5m = pd.concat([df_5m, new_row]).iloc[-251:]

                    # Analysis on 1m
                    if itv == '1m' and len(df_1m) >= 201 and len(df_5m) >= 51:
                        df_1m = analyzer.calculate_indicators(df_1m)
                        df_5m = analyzer.calculate_indicators(df_5m)
                        
                        signal_data, signal_type = analyzer.check_signals_v4(df_1m, df_5m)

                        if signal_type:
                            print(f"🔥 SINYAL: BTC {signal_type}")
                            await notifier.send_signal_msg(signal_type, signal_data)
                            logger.log_signal(signal_data, signal_type)

                        if is_closed:
                            print(f"🕒 [{datetime.now().strftime('%H:%M:%S')}] BTC: {vals[3]:.2f} | V5 Sentinel Online")

        except Exception as e:
            print(f"⚠️ [Core Error] {e}. Kurtarma aktif...")
            await asyncio.sleep(10)
        finally:
            if 'client' in locals():
                await client.close_connection()

if __name__ == "__main__":
    apply_system_fixes()
    try:
        asyncio.run(run_agent())
    except KeyboardInterrupt:
        print("\nAjan güvenli bir şekilde kapatıldı.")
