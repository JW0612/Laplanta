import streamlit as st
import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf

# 1. Configuración de pantalla
st.set_page_config(page_title="La Planta | Quant Lab", layout="wide")

st.title("📈 Sistema Control de Portafolios: Proyecto 'La Planta'")
st.subheader("Simulación de Portafolio Pasivo (Sin inyección de capital)")
st.markdown("---")

# ... (Sección de parámetros y captura de tickers sigue igual que antes) ...

with col2:
    st.markdown("### 📊 Monitoreo de Trayectorias")
    
    if correr_algoritmo:
        # ... (La parte de descarga y limpieza de yfinance se mantiene igual) ...
        
        # 1. Calcular Retornos Diarios Reales
        retornos_diarios = datos_mercado.pct_change().dropna()
        pesos = df_portafolio["Monto"].values / capital_total_inicial
        
        # 2. CALCULO PASIVO PURO: 
        # Aquí eliminamos los bucles for que multiplicaban retornos.
        # El retorno del portafolio es simplemente el promedio ponderado de los activos.
        retornos_pasivos = retornos_diarios.dot(pesos)
        
        # 3. Construcción de la curva basada 100% en el mercado
        curva_pasiva = capital_total_inicial * np.cumprod(1 + retornos_pasivos.values)
        fechas_reales = retornos_diarios.index
        
        # Gráfico
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=fechas_reales, 
            y=curva_pasiva, 
            name="Portafolio Pasivo Real (Sin inyección)", 
            line=dict(color="#58a6ff", width=2.5)
        ))
        
        fig.update_layout(template="plotly_dark", ...) # (Layout igual al anterior)
        st.plotly_chart(fig, use_container_width=True)
        
        # Métricas
        rendimiento_pct = ((curva_pasiva[-1] / capital_total_inicial) - 1) * 100
        st.metric("Rendimiento Final", f"${curva_pasiva[-1]:,.2f}", f"{rendimiento_pct:+.2f}%")

# ... (El resto del código de comentarios y footer queda igual) ...