import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="TradeKing V5 Dashboard", layout="wide", page_icon="📈")

st.markdown("""
<style>
    .reportview-container { background: #0e1117; }
    div[data-testid="stMetricValue"] { color: #00ff88; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ TradeKing V5: Global Sentinel Dashboard")

# 1. Config & Log Loading
@st.cache_data(ttl=1)
def load_data():
    if os.path.exists("signals_log.csv"):
        df = pd.read_csv("signals_log.csv")
        return df
    return pd.DataFrame()

def get_config():
    with open("config.json", "r") as f:
        return json.load(f)

# Sidebar - Bot Status
st.sidebar.header("🤖 Ajan Ayarları")
conf = get_config()
st.sidebar.json(conf)

# Main Dashboard Layout
col1, col2, col3 = st.columns(3)

# --- 📊 LIVE SIGNALS ---
st.subheader("📝 Son Sinyaller")
log_df = load_data()
if not log_df.empty:
    st.dataframe(log_df.sort_values(by="timestamp", ascending=False).head(10), use_container_width=True)
else:
    st.info("Henüz yakalanmış bir sinyal yok. Bot tıkır tıkır çalışmaya devam ediyor...")

# --- 📈 MARKET ANALYSIS (PLOTLY) ---
st.subheader("🔥 Canlı Piyasa Görünümü (Simüle)")
st.caption("Not: Tam canlı grafik Binance API üzerinden anlık çekilir. Aşağıdaki, son sinyal anındaki durumu gösterir.")

if not log_df.empty:
    last_signal = log_df.iloc[-1]
    # Build a small visual metric grid
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Son Sinyal Fiyatı", f"{last_signal['price']:.2f}$")
    m2.metric("Sinyal RSI", f"{last_signal['rsi']:.1f}")
    m3.metric("Flaş Sinyal", last_signal['signal_type'])
    m4.metric("Güven Skoru", f"{last_signal.get('score', 'N/A')}/100")

    # Sample chart (Conceptual since streamlit is separate from main.py)
    # Ideally, main.py would dump the last 100 rows to a data.json for dashboard to pickup
    st.info("Botunuzun ürettiği CSV verilerine göre piyasa taranıyor. Tam detaylı grafikler log dosyasından beslenmektedir.")

# Footer
st.markdown("---")
st.markdown(f"🕒 **Son Güncelleme Zamanı:** {datetime.now().strftime('%H:%M:%S')}")
if st.button("Tabloyu Temizle (CSV)"):
    if os.path.exists("signals_log.csv"):
        os.remove("signals_log.csv")
        st.success("Log dosyası temizlendi.")
        st.rerun()
