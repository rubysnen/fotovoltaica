# =========================================================
# POLYMARKET BOT COMPLETO
# EMA + RSI + STREAMLIT + PY_CLOB_CLIENT
# =========================================================

# INSTALAR:
# pip install streamlit pandas pandas-ta plotly requests py-clob-client

# EJECUTAR:
# streamlit run app.py

# =========================================================
# IMPORTS
# =========================================================

import streamlit as st
import pandas as pd
import pandas_ta as ta
import requests
import plotly.graph_objects as go
import time

from py_clob_client.client import ClobClient

# =========================================================
# CONFIG STREAMLIT
# =========================================================

st.set_page_config(
    page_title="Polymarket BTC Bot",
    layout="wide"
)

st.title("📈 POLYMARKET BTC BOT")

# =========================================================
# CONFIG POLYMARKET
# =========================================================

HOST = "https://clob.polymarket.com"

CHAIN_ID = 137

# ============================================
# TUS DATOS
# ============================================

PRIVATE_KEY = "TU_PRIVATE_KEY"

FUNDER = "TU_DIRECCION_WALLET"

# TOKEN YES DEL MERCADO
TOKEN_ID = "TOKEN_ID"

# =========================================================
# CONECTAR POLYMARKET
# =========================================================

try:

    client = ClobClient(
        HOST,
        key=PRIVATE_KEY,
        chain_id=CHAIN_ID,
        signature_type=1,
        funder=FUNDER
    )

    api_creds = client.create_or_derive_api_creds()

    client.set_api_creds(api_creds)

    st.success("✅ Conectado a Polymarket")

except Exception as e:

    st.error(f"❌ Error conexión: {e}")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ CONFIGURACIÓN")

symbol = st.sidebar.selectbox(
    "Par",
    ["BTCUSDT"]
)

interval = st.sidebar.selectbox(
    "Temporalidad",
    ["5m", "15m", "1h"],
    index=1
)

ema_fast = st.sidebar.slider(
    "EMA Rápida",
    5,
    50,
    20
)

ema_slow = st.sidebar.slider(
    "EMA Lenta",
    10,
    200,
    50
)

rsi_period = st.sidebar.slider(
    "RSI",
    5,
    30,
    14
)

capital = st.sidebar.number_input(
    "Capital",
    value=100.0
)

order_size = st.sidebar.number_input(
    "Tamaño Orden",
    value=5.0
)

enable_real_orders = st.sidebar.checkbox(
    "ACTIVAR ÓRDENES REALES"
)

# =========================================================
# OBTENER DATOS BTC
# =========================================================

@st.cache_data(ttl=30)
def get_data():

    url = (
        f"https://api.binance.com/api/v3/klines"
        f"?symbol={symbol}&interval={interval}&limit=150"
    )

    response = requests.get(url)

    data = response.json()

    df = pd.DataFrame(data)

    df = df.iloc[:, :6]

    df.columns = [
        "time",
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    numeric_cols = [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    df[numeric_cols] = df[numeric_cols].astype(float)

    df["time"] = pd.to_datetime(
        df["time"],
        unit="ms"
    )

    return df

# =========================================================
# INDICADORES
# =========================================================

def indicators(df):

    df["EMA_FAST"] = ta.ema(
        df["close"],
        length=ema_fast
    )

    df["EMA_SLOW"] = ta.ema(
        df["close"],
        length=ema_slow
    )

    df["RSI"] = ta.rsi(
        df["close"],
        length=rsi_period
    )

    return df

# =========================================================
# SEÑALES
# =========================================================

def signals(df):

    last = df.iloc[-1]
    prev = df.iloc[-2]

    buy_signal = (
        prev["EMA_FAST"] < prev["EMA_SLOW"]
        and last["EMA_FAST"] > last["EMA_SLOW"]
        and last["RSI"] > 50
    )

    sell_signal = (
        prev["EMA_FAST"] > prev["EMA_SLOW"]
        and last["EMA_FAST"] < last["EMA_SLOW"]
        and last["RSI"] < 50
    )

    return buy_signal, sell_signal

# =========================================================
# CREAR ORDEN POLYMARKET
# =========================================================

def buy_yes():

    try:

        order = client.create_order(
            token_id=TOKEN_ID,
            side="BUY",
            price=0.55,
            size=order_size
        )

        result = client.post_order(order)

        st.success("🟢 ORDEN YES EJECUTADA")

        st.write(result)

    except Exception as e:

        st.error(f"ERROR ORDEN: {e}")

# =========================================================
# CARGAR DATOS
# =========================================================

with st.spinner("Analizando BTC..."):

    df = get_data()

    df = indicators(df)

    buy_signal, sell_signal = signals(df)

# =========================================================
# MÉTRICAS
# =========================================================

current_price = df["close"].iloc[-1]

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "BTC",
        f"${current_price:,.2f}"
    )

with col2:

    st.metric(
        "RSI",
        round(df["RSI"].iloc[-1], 2)
    )

with col3:

    trend = (
        "ALCISTA"
        if df["EMA_FAST"].iloc[-1] >
        df["EMA_SLOW"].iloc[-1]
        else "BAJISTA"
    )

    st.metric(
        "TENDENCIA",
        trend
    )

# =========================================================
# SEÑALES
# =========================================================

if buy_signal:

    st.success("🟢 SEÑAL COMPRA")

    if enable_real_orders:

        buy_yes()

elif sell_signal:

    st.error("🔴 SEÑAL VENTA")

else:

    st.warning("🟡 SIN SEÑAL")

# =========================================================
# CHART
# =========================================================

fig = go.Figure()

fig.add_trace(
    go.Candlestick(
        x=df["time"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="BTC"
    )
)

fig.add_trace(
    go.Scatter(
        x=df["time"],
        y=df["EMA_FAST"],
        mode="lines",
        name="EMA FAST"
    )
)

fig.add_trace(
    go.Scatter(
        x=df["time"],
        y=df["EMA_SLOW"],
        mode="lines",
        name="EMA SLOW"
    )
)

fig.update_layout(
    height=700,
    xaxis_rangeslider_visible=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================================================
# RSI CHART
# =========================================================

st.subheader("RSI")

st.line_chart(df["RSI"])

# =========================================================
# ÚLTIMAS VELAS
# =========================================================

st.subheader("Últimas Velas")

st.dataframe(
    df.tail(10),
    use_container_width=True
)

# =========================================================
# INFO MERCADO
# =========================================================

st.subheader("Mercado Polymarket")

st.write(f"TOKEN_ID: {TOKEN_ID}")

# =========================================================
# AUTO REFRESH
# =========================================================

refresh = st.checkbox("Auto Refresh")

if refresh:

    time.sleep(30)

    st.rerun()