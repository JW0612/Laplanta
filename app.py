import streamlit as st
import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf

# Configuración inicial
st.set_page_config(page_title="La Planta | Quant Lab", layout="wide")
st.title("📈 Sistema Control de Portafolios: Proyecto 'La Planta'")

# Inicializar historial con la clave 'texto'
if "historial_comentarios" not in st.session_state:
    st.session_state.historial_comentarios = [
        {"usuario": "Sistema", "texto": "Laboratorio de control estocástico iniciado."}
    ]

# Configuración de parámetros
col1, col2 = st.columns([5, 7])
with col1:
    fecha_inicio = st.date_input("Fecha de Inicio", value=datetime.date.today() - datetime.timedelta(days=365))
    num_activos = st.number_input("Nodos de Activos", min_value=3, max_value=7, value=5)
    datos_usuario = []
    for i in range(int(num_activos)):
        t = st.text_input(f"Activo {i+1}", value="NVDA", key=f"t{i}")
        m = st.number_input(f"Capital ($)", value=10000, key=f"m{i}")
        datos_usuario.append({"Activo": t.upper(), "Monto": m})
    correr = st.button("🚀 Ejecutar Simulación en Lazo Cerrado")

with col2:
    if correr:
        df_portafolio = pd.DataFrame(datos_usuario)
        tickers = df_portafolio["Activo"].tolist()
        
        # 1. DESCARGA Y APLANADO DE DATOS (BLINDAJE)
        raw_data = yf.download(tickers, start=fecha_inicio, progress=False)
        
        # Si 'Adj Close' no está en el primer nivel, buscamos en los niveles internos
        if 'Adj Close' not in raw_data.columns:
            # Aplanar MultiIndex si existe
            df_precios = raw_data.xs('Adj Close', axis=1, level=0, drop_level=True)
        else:
            df_precios = raw_data['Adj Close']
            
        df_precios = df_precios.ffill().bfill()
        
        # 2. LÓGICA DE CONTROL (LAZO CERRADO)
        pesos = df_portafolio["Monto"].values / df_portafolio["Monto"].sum()
        retornos = df_precios.pct_change().dropna()
        ret_pasivo = retornos.dot(pesos)
        
        # Algoritmo: Momentum adaptativo
        ret_activo = ret_pasivo.copy()
        for t in range(len(ret_activo)):
            if ret_activo[t] > 0: ret_activo[t] *= 1.05 
            else: ret_activo[t] *= 0.85                  
        
        capital_inicial = df_portafolio["Monto"].sum()
        curva_activa = capital_inicial * np.cumprod(1 + ret_activo)
        
        # 3. VISUALIZACIÓN
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ret_activo.index, y=curva_activa, name="Modelo Adaptativo", line=dict(color="#58a6ff")))
        fig.update_layout(template="plotly_dark", title="Trayectoria Adaptativa 'La Planta'")
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Resultado del Lazo Cerrado", f"${curva_activa.iloc[-1]:,.2f}")

    # 4. BITÁCORA DE COMENTARIOS (CORREGIDA)
    st.markdown("### 💬 Bitácora Técnica")
    with st.form("comentarios_form", clear_on_submit=True):
        usr = st.text_input("Usuario")
        txt = st.text_area("Comentario")
        if st.form_submit_button("Registrar"):
            st.session_state.historial_comentarios.insert(0, {"usuario": usr, "texto": txt})
    
    for c in st.session_state.historial_comentarios:
        # Usamos 'texto' tal como se definió al insertar
        st.markdown(f"**{c['usuario']}**: {c['texto']}")