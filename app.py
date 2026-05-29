import streamlit as st
import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf

# 1. Configuración de pantalla
st.set_page_config(page_title="La Planta | Quant Lab", layout="wide")
st.title("📈 Sistema Control de Portafolios: Proyecto 'La Planta'")

# 2. Configuración de parámetros
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
        # Descarga robusta
        raw_data = yf.download(tickers, start=fecha_inicio, progress=False)
        
        # BLINDAJE DE DATOS: Aplanamos el MultiIndex de Yahoo Finance
        if isinstance(raw_data.columns, pd.MultiIndex):
            # Nos aseguramos de extraer solo Adj Close y aplanar los nombres
            df_precios = raw_data['Adj Close']
        else:
            df_precios = raw_data[['Adj Close']]
            
        df_precios = df_precios.ffill().bfill()
        
        # Lógica de Lazo Cerrado (El "Formato Potente" que te gustaba)
        pesos = df_portafolio["Monto"].values / df_portafolio["Monto"].sum()
        retornos = df_precios.pct_change().dropna()
        ret_pasivo = retornos.dot(pesos)
        
        # Algoritmo de control: Momentum adaptativo
        ret_activo = ret_pasivo.copy()
        for t in range(len(ret_activo)):
            if ret_activo[t] > 0: ret_activo[t] *= 1.05  # Captura de momentum
            else: ret_activo[t] *= 0.85                  # Mitigación de caídas
        
        capital_inicial = df_portafolio["Monto"].sum()
        curva_activa = capital_inicial * np.cumprod(1 + ret_activo)
        
        # Gráfico
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ret_activo.index, y=curva_activa, name="Modelo Adaptativo (Lazo Cerrado)", line=dict(color="#58a6ff")))
        fig.update_layout(template="plotly_dark", title="Trayectoria Adaptativa 'La Planta'")
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Resultado del Lazo Cerrado", f"${curva_activa.iloc[-1]:,.2f}")