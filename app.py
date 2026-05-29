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

# Instrucciones
with st.expander("📖 Guía de Operación"):
    st.markdown("Este sistema calcula el rendimiento pasivo de un clúster de activos basado en datos reales de mercado.")

tickers_muestra = ["NVDA", "MU", "AVGO", "ARM", "RKLB"]
col1, col2 = st.columns([5, 7], gap="large")

with col1:
    fecha_inicio = st.date_input("Fecha de Inicio", value=datetime.date.today() - datetime.timedelta(days=365))
    num_activos = st.number_input("Nodos de Activos", min_value=3, max_value=7, value=5)
    
    datos_usuario = []
    for i in range(int(num_activos)):
        ticker = st.text_input(f"Activo {i+1}", value=tickers_muestra[i % len(tickers_muestra)], key=f"t{i}")
        monto = st.number_input(f"Capital ($)", value=10000, key=f"m{i}")
        datos_usuario.append({"Activo": ticker.upper(), "Monto": monto})
    
    correr_algoritmo = st.button("🚀 Ejecutar Simulación Pasiva")

with col2:
    if correr_algoritmo:
        df_portafolio = pd.DataFrame(datos_usuario)
        capital_total_inicial = df_portafolio["Monto"].sum()
        tickers_a_descargar = df_portafolio["Activo"].tolist()
        
        with st.spinner("Descargando datos..."):
            try:
                # Descarga directa
                df = yf.download(tickers_a_descargar, start=fecha_inicio, end=datetime.date.today(), progress=False)
                
                # Aplanamiento de columnas seguro
                if isinstance(df.columns, pd.MultiIndex):
                    datos_mercado = pd.DataFrame(index=df.index)
                    for t in tickers_a_descargar:
                        col = [c for c in df.columns if 'Adj Close' in c and t in c]
                        if col: datos_mercado[t] = df[col[0]]
                else:
                    datos_mercado = df[['Adj Close']] if 'Adj Close' in df.columns else df[['Close']]
                
                datos_mercado = datos_mercado.ffill().bfill()
                
                # Cálculo pasivo: Rendimiento ponderado directo
                retornos = datos_mercado.pct_change().dropna()
                pesos = df_portafolio["Monto"].values / capital_total_inicial
                retornos_pasivos = retornos.dot(pesos)
                curva_pasiva = capital_total_inicial * np.cumprod(1 + retornos_pasivos.values)
                
                # Gráfico
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=retornos.index, y=curva_pasiva, name="Portafolio Pasivo", line=dict(color="#58a6ff", width=2.5)))
                
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis_title="Fecha",
                    yaxis_title="Capital ($)",
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Métricas
                rendimiento_pct = ((curva_pasiva[-1] / capital_total_inicial) - 1) * 100
                st.metric("Rendimiento Final Acumulado", f"${curva_pasiva[-1]:,.2f}", f"{rendimiento_pct:+.2f}%")
                
            except Exception as e:
                st.error(f"Error: {e}")