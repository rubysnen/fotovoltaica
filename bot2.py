# =========================================================
# STREAMLIT BTC BOT
# EMA + RSI MANUAL
# COMPATIBLE CON STREAMLIT CLOUD
# =========================================================

# INSTALAR:
# pip install streamlit pandas plotly requests numpy

# EJECUTAR:
# streamlit run app.py

# =========================================================
# IMPORTS
# =========================================================

import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import numpy as np
import time

# =========================================================
# CONFIG STREAMLIT
# =========================================================

st.set_page_config(
    page_title="BTC Trading Bot",
    layout="wide"
)

st.title("📈 BTC EMA + RSI BOT")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Configuración")

symbol = st.sidebar.selectbox(
    "Par",
    ["BTCUSDT", "ETHUSDT"],
    index=0
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
    value=1000.0
)

# =========================================================
# OBTENER DATOS BINANCE
# =========================================================

@st.cache_data(ttl=30)
def get_data(symbol, interval):

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
# EMA MANUAL
# =========================================================

def calculate_ema(df):

    df["EMA_FAST"] = (
        df["close"]
        .ewm(span=ema_fast, adjust=False)
        .mean()
    )

    df["EMA_SLOW"] = (
        df["close"]
        .ewm(span=ema_slow, adjust=False)
        .mean()
    )

    return df

# =========================================================
# RSI MANUAL
# =========================================================

def calculate_rsi(df):

    delta = df["close"].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(rsi_period).mean()

    avg_loss = loss.rolling(rsi_period).mean()

    rs = avg_gain / avg_loss

    df["RSI"] = 100 - (100 / (1 + rs))

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
# CARGAR DATOS
# =========================================================

with st.spinner("Analizando mercado..."):

    df = get_data(symbol, interval)

    df = calculate_ema(df)

    df = calculate_rsi(df)

    buy_signal, sell_signal = signals(df)

# =========================================================
# MÉTRICAS
# =========================================================

current_price = df["close"].iloc[-1]

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Precio",
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
        "Tendencia",
        trend
    )

# =========================================================
# SEÑALES VISUALES
# =========================================================

if buy_signal:

    st.success("🟢 SEÑAL DE COMPRA")

elif sell_signal:

    st.error("🔴 SEÑAL DE VENTA")

else:

    st.warning("🟡 SIN SEÑAL")

# =========================================================
# PAPER TRADING
# =========================================================

st.subheader("💰 Paper Trading")

if "position" not in st.session_state:
    st.session_state.position = False

if "entry_price" not in st.session_state:
    st.session_state.entry_price = 0

if buy_signal and not st.session_state.position:

    st.session_state.position = True

    st.session_state.entry_price = current_price

    st.success(
        f"Compra simulada en ${current_price:,.2f}"
    )

if st.session_state.position:

    pnl = (
        (current_price - st.session_state.entry_price)
        / st.session_state.entry_price
    ) * 100

    st.info(f"PnL: {pnl:.2f}%")

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

st.subheader("📊 RSI")

st.line_chart(df["RSI"])

# =========================================================
# TABLA
# =========================================================

st.subheader("📄 Últimas Velas")

st.dataframe(
    df.tail(10),
    use_container_width=True
)

# =========================================================
# AUTO REFRESH
# =========================================================

refresh = st.checkbox("🔄 Auto Refresh")

if refresh:

    time.sleep(30)

    st.rerun()
