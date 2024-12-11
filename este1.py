import streamlit as st
import math

# Funciones de cálculo
def calcular_temperatura_celcius(tamb, g, tonc):
    return tamb + g * (tonc - 20) / 800

def calcular_p(pmp, cp, tc, g):
    return pmp * (1 + (cp / 100) * (tc - 25)) * g / 1000

def calcular_u(vmp, ct, tc):
    return vmp * (1 + (ct / 100) * (tc - 25))

def calcular_i(imp, ci, tc, g):
    return imp * (1 + (ci / 100) * (tc - 25)) * g / 1000

def calcular_inversor(pmax, p, rtmin, u, rtmax, imax, i):
    no_ps = pmax / p
    no_min_ps = rtmin / u
    no_max_ps = rtmax / u
    no_max_par = imax / i
    return no_ps, no_min_ps, no_max_ps, no_max_par

# Configurar la página
st.set_page_config(page_title="Calculadora Fotovoltaica", layout="wide")

# Estilos personalizados
st.markdown(
    """
    <style>
        .header {
            font-size: 2em;
            font-weight: bold;
            color: #FFFFFF;
            margin-bottom: 20px;
        }
        .result-card {
            background-color: #1E1E2E;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            color: #FFFFFF;
            font-size: 1.5em;
            margin: 10px;
        }
        .result-card .value {
            font-size: 2em;
            font-weight: bold;
        }
        .icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .sidebar .sidebar-content {
            background-color: #1E1E2E;
            padding: 20px;
            border-radius: 10px;
            color: #FFFFFF;
        }
        body {
            background-color: #0F0F1A;
            color: #FFFFFF;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Header
st.markdown("<div class='header'>Calculadora Fotovoltaica</div>", unsafe_allow_html=True)

# Parámetros de entrada
with st.sidebar:
    st.markdown("<div class='header'>Parámetros de Entrada</div>", unsafe_allow_html=True)
    tamb = st.number_input("Temperatura ambiente (Tamb, °C):", value=25.0)
    g = st.number_input("Radiación solar (G, W/m^2):", value=1000.0)
    cp = st.number_input("Coeficiente de potencia (CP, %):", value=-0.4)
    ct = st.number_input("Coeficiente de tensión (Ct, %):", value=-0.3)
    ci = st.number_input("Coeficiente de corriente (CI, %):", value=0.05)
    
    tonc = st.number_input("TONC (°C):", value=45.0)
    st.markdown("<div class='header'>Inversor</div>", unsafe_allow_html=True)
    pmax = st.number_input("Potencia máxima del inversor (Pmax, W):", value=5000.0)
    rtmin = st.number_input("Rango térmico mínimo del inversor (Rtmin, V):", value=200.0)
    rtmax = st.number_input("Rango térmico máximo del inversor (Rtmax, V):", value=600.0)
    imax = st.number_input("Corriente máxima del inversor (Imax, A):", value=20.0)
    st.markdown("<div class='header'>Datos de la Placa</div>", unsafe_allow_html=True)
    pmp = st.number_input("Potencia máxima de la placa (Pmp, W):", value=300.0)
    vmp = st.number_input("Voltaje máximo de la placa (Vmp, V):", value=37.0)
    imp = st.number_input("Corriente máxima de la placa (Imp, A):", value=8.0)

# Cálculos
tc = calcular_temperatura_celcius(tamb, g, tonc)
p = calcular_p(pmp, cp, tc, g)
u = calcular_u(vmp, ct, tc)
i = calcular_i(imp, ci, tc, g)
no_ps, no_min_ps, no_max_ps, no_max_par = calcular_inversor(pmax, p, rtmin, u, rtmax, imax, i)

# Mostrar resultados en tarjetas
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"<div class='result-card'><div class='icon'>🌡️</div><div class='value'>{tc:.2f} °C</div><div>Temperatura de Celula</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='result-card'><div class='icon'>⚡️</div><div class='value'>{u:.2f} Vcc</div><div>Tensión</div></div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='result-card' style='background-color: #00D1B2; color: #000000;'><div class='icon'>🔋</div><div class='value'>{p:.2f} W</div><div>Potencia</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='result-card'><div class='icon'>💡</div><div class='value'>{i:.2f} A</div><div>Intensidad</div></div>", unsafe_allow_html=True)

# Mostrar cálculos del inversor
st.write("### Cálculos del Inversor")

col3, col4 = st.columns(2)

with col3:
    st.markdown(f"<div class='result-card'><div class='icon'>🛰️</div><div class='value'>{no_ps:.2f} / {math.ceil(no_ps)}</div><div># Paneles Solares</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='result-card'><div class='icon'>📊</div><div class='value'>{no_min_ps:.2f} / {math.ceil(no_min_ps)}</div><div>Número Mínimo Paneles Serie</div></div>", unsafe_allow_html=True)

with col4:
    st.markdown(f"<div class='result-card'><div class='icon'>📊</div><div class='value'>{no_max_ps:.2f} / {math.floor(no_max_ps)}</div><div># Máximo Paneles Serie</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='result-card'><div class='icon'>📊</div><div class='value'>{no_max_par:.2f} / {math.floor(no_max_par)}</div><div># Máximo Paralelo</div></div>", unsafe_allow_html=True)

# Cálculo de Número de Serie y Paralelo con los resultados de Potencia, Tensión e Intensidad
st.write("### Cálculo de Número de Serie y Paralelo")

# Entrada de número de series y paralelos
num_series = st.number_input("Número de Series (Número de paneles por serie):", min_value=1, value=math.ceil(no_min_ps), step=1)
num_paralelos = st.number_input("Número de Paralelos (Número de series conectadas en paralelo):", min_value=1, value=math.floor(no_max_par), step=1)

# Cálculos adicionales para la Tensión Total, Corriente Total y Potencia Total
vt = num_series * u  # Tensión total (Serie)
imp_total = num_paralelos * i  # Corriente total (Paralelo)
p_total = vt * imp_total  # Potencia total

# Mostrar resultados adicionales en una tarjeta
col5, col6 = st.columns(2)

with col5:
    st.markdown(f"""
    <div class='result-card'>
        <div class='icon'>🔌</div>
        <div class='value'>{vt:.2f} V</div>
        <div>Tensión Total (VT)</div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div class='result-card'>
        <div class='icon'>🔋</div>
        <div class='value'>{imp_total:.2f} A</div>
        <div>Corriente Total (IMP)</div>
    </div>
    """, unsafe_allow_html=True)

# Mostrar la Potencia Total
st.markdown(f"""
<div class='result-card' style='background-color: #ff0000; color: #000000;'>
    <div class='icon'>⚡️</div>
    <div class='value'>{p_total:.2f} W</div>
    <div>Potencia Total (P)</div>
</div>
""", unsafe_allow_html=True)

# Footer
st.write("---")
st.caption("Calculadora Fotovoltaica - Diseñada por Rubysnen Roberto Vidal")