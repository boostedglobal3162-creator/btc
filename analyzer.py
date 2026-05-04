import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands

class BTCAnalyzer:
    """Strategy engine (V4 Professional) with Multi-Timeframe Confirmation."""
    def __init__(self, config):
        self.config = config
        self.dip_percent = config.get("dipPercent", 3.0)
        self.rsi_threshold = config.get("rsiThreshold", 30)
        self.ema_50_p = config.get("emaPeriod", 50)
        self.ema_200_p = config.get("emaLongPeriod", 200)

        # MACD & BB Params
        self.macd_fast = config.get("macdFast", 12)
        self.macd_slow = config.get("macdSlow", 26)
        self.macd_signal = config.get("macdSignal", 9)
        self.bb_period = config.get("bbPeriod", 20)
        self.bb_std = config.get("bbStd", 2)

    def calculate_indicators(self, df):
        """Processes raw OHLCV data into V4 technical indicators."""
        if len(df) < 50: return df # Basic sanity check
        
        # Fundamental OHLCV
        df["rsi"] = RSIIndicator(df["close"], window=14).rsi()
        df["ema50"] = EMAIndicator(df["close"], window=self.ema_50_p).ema_indicator()
        df["ema200"] = EMAIndicator(df["close"], window=self.ema_200_p).ema_indicator()
        
        # Bollinger Bands
        bb = BollingerBands(df["close"], window=self.bb_period, window_dev=self.bb_std)
        df["bb_low"] = bb.bollinger_lband()
        df["bb_high"] = bb.bollinger_hband()

        # MACD
        macd_obj = MACD(df["close"], self.macd_fast, self.macd_slow, self.macd_signal)
        df["macd_diff"] = macd_obj.macd_diff()

        # Volume Moving Average (SMA20)
        df["vol_ma"] = df["volume"].rolling(window=20).mean()

        # Custom Volatility
        if len(df) >= 5:
            recent_p = df["close"].tail(5)
            df.loc[df.index[-1], "volatility"] = (recent_p.max() - recent_p.min()) / recent_p.min()

        return df

    def check_signals_v4(self, df_1m, df_5m):
        """High-Confidence scoring with MTF and Volume confirmation."""
        if len(df_1m) < 100 or len(df_5m) < 50: return None, None

        last1m = df_1m.iloc[-1]
        prev1m = df_1m.iloc[-2]
        
        # --- 📈 1M CORE DATA ---
        price = last1m["close"]
        rsi = last1m["rsi"]
        ema50 = last1m.get("ema50", 0)
        bb_low = last1m.get("bb_low", 0)
        macd_diff = last1m["macd_diff"]
        
        # --- 🔍 MULTI-TIMEFRAME (MTF) CHECK ---
        last5m = df_5m.iloc[-1]
        is_bullish_5m = price > last5m.get("ema50", 0) # 5m Trend confirmation
        
        # --- 🔥 SCORING LOGIC ---
        score = 0
        
        # Condition 1: RSI (40 pts)
        if rsi < self.rsi_threshold: score += 40
        elif rsi < 40: score += 15
        
        # Condition 2: Bollinger Band Low (20 pts)
        if price < bb_low: score += 20
        
        # Condition 3: Dip % (25 pts)
        candle_change = ((price - last1m["open"]) / last1m["open"]) * 100
        if (candle_change <= -self.dip_percent): score += 25
            
        # Condition 4: Volume Spike (+15 pts) - Crucial for "Blind Trust"
        if "volume" in last1m and "vol_ma" in last1m:
            if last1m["volume"] > last1m["vol_ma"] * 1.5: 
                score += 15
        
        # Condition 5: Multi-Timeframe Teyit (+15 pts)
        if is_bullish_5m: score += 15
        else: score -= 30 # Harsh penalty for counter-trend trading

        # Filter: Golden Cross Check (EMA50 > EMA200)
        is_golden = last1m.get("ema50", 0) > last1m.get("ema200", 0)
        if is_golden: score += 10

        # FINAL BUY DECISION (Score > 75 for High Confidence)
        if score >= 75:
            return {
                "price": price, "rsi": rsi, "ema": ema50, 
                "macd": macd_diff, "vol": last1m.get("volatility", 0), 
                "score": score, "type": "AL", "trend": "BULLISH" if is_bullish_5m else "MIXED"
            }, f"AL (Confidence Score: {score})"

        # --- SELL LOGIC ---
        # Logic: Price < EMA50 (1m) AND RSI > 60 AND MACD Cross Negative
        if price < ema50 and rsi > 60 and (prev1m["macd_diff"] > 0 and macd_diff < 0):
            return {
                "price": price, "rsi": rsi, "ema": ema50, 
                "macd": macd_diff, "vol": last1m.get("volatility", 0), "type": "SAT"
            }, "SAT"

        return None, None
