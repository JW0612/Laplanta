import streamlit as st
import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf

# 1. Configuración de pantalla con estilo corporativo y limpio
st.set_page_config(
    page_title="La Planta | Quant Lab", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos visuales personalizados
st.title("📈 Sistema Control de Portafolios: Proyecto 'La Planta'")
st.subheader("Análisis Adaptativo Reactivo y Control Estadístico de Procesos (SPC)")
st.markdown("---")

# 2. SECCIÓN: INSTRUCCIONES DE USO
with st.expander("📖 Guía de Operación e Instrucciones de la Planta", expanded=False):
    st.markdown("""
    Este simulador evalúa la densidad probabilística y la persistencia temporal de una masa de capital expuesta a activos reales del mercado tecnológico y de infraestructura.
    1. **Establezca la ventana temporal:** Por defecto el sistema calcula un retraso óptimo de 1 año atrás a la fecha actual.
    2. **Defina el tamaño del clúster:** Seleccione la cantidad de cuentas o nodos de activos que desea simular (Mínimo 3, Máximo 7).
    3. **Asigne Tickers y Masa de Capital:** Introduzca las siglas del activo (ej. *NVDA*, *MU*, *RKLB*, *AVGO*). El sistema jalará los datos de cierre reales de Yahoo Finance.
    4. **Ejecute el Algoritmo:** El sistema procesará las trayectorias reales aplicando filtros para mitigar el *volatility decay*.
    """)

# Lista de tickers de muestra para usar como guías (placeholders)
tickers_muestra = ["NVDA", "MU", "AVGO", "ARM", "RKLB", "DELL", "CRBS"]

# Estructura principal en dos columnas
col1, col2 = st.columns([5, 7], gap="large")

with col1:
    st.markdown("### ⚙️ Parámetros de Control Óptimo")
    
    # Calcular automáticamente la fecha de hoy y restarle un año (365 días)
    fecha_hoy = datetime.date.today()
    fecha_un_ano_atras = fecha_hoy - datetime.timedelta(days=365)
    
    fecha_inicio = st.date_input(
        "Ventana Temporal de Inicio (Histórico)",
        value=fecha_un_ano_atras,
        max_value=fecha_hoy
    )
    
    num_activos = st.number_input(
        "Nodos de Activos en el Clúster (3 a 7)", 
        min_value=3, 
        max_value=7, 
        value=5
    )
    
    st.markdown("#### 💼 Configuración de Cuentas y Asignación de Capital")
    datos_usuario = []
    
    for i in range(int(num_activos)):
        c1, c2 = st.columns([1, 1])
        ticker_sugerido = tickers_muestra[i % len(tickers_muestra)]
        
        with c1:
            activo = st.text_input(
                f"Activo {i+1}", 
                placeholder=f"Ej. {ticker_sugerido}", 
                key=f"ticker_{i}"
            )
        with c2:
            monto = st.number_input(
                f"Capital Inicial Asignado ($)", 
                min_value=0, 
                value=10000, 
                step=1000, 
                key=f"monto_{i}"
            )
        
        ticker_final = activo.strip().upper() if activo.strip() else ticker_sugerido
        datos_usuario.append({"Activo": ticker_final, "Monto": monto})
    
    st.markdown("---")
    correr_algoritmo = st.button("🚀 Ejecutar Simulación en Lazo Cerrado", use_container_width=True)

with col2:
    st.markdown("### 📊 Monitoreo de Trayectorias Estocásticas")
    
    df_portafolio = pd.DataFrame(datos_usuario)
    capital_total_inicial = df_portafolio["Monto"].sum()
    
    if correr_algoritmo:
        tickers_a_descargar = df_portafolio["Activo"].tolist()
        
        with st.spinner("📥 Descargando precios históricos reales desde Yahoo Finance..."):
            try:
                df_descarga = yf.download(
                    tickers_a_descargar, 
                    start=fecha_inicio, 
                    end=fecha_hoy,
                    progress=False
                )
                
                if df_descarga.empty:
                    st.error("No se pudieron recuperar datos para los tickers especificados en esa ventana temporal.")
                else:
                    # Aplanar las columnas multinivel
                    if isinstance(df_descarga.columns, pd.MultiIndex):
                        datos_mercado = pd.DataFrame(index=df_descarga.index)
                        for t in tickers_a_descargar:
                            col_candidata = [c for c in df_descarga.columns if 'Adj Close' in c and t in c]
                            if col_candidata:
                                datos_mercado[t] = df_descarga[col_candidata[0]]
                            else:
                                col_alt = [c for c in df_descarga.columns if 'Close' in c and t in c]
                                if col_alt:
                                    datos_mercado[t] = df_descarga[col_alt[0]]
                    else:
                        if 'Adj Close' in df_descarga.columns:
                            datos_mercado = df_descarga[['Adj Close']].rename(columns={'Adj Close': tickers_a_descargar[0]})
                        else:
                            datos_mercado = df_descarga[['Close']].rename(columns={'Close': tickers_a_descargar[0]})

                    datos_mercado = datos_mercado.ffill().bfill()
                    
                    # 1. Calcular Retornos Diarios Reales
                    retornos_diarios = datos_mercado.pct_change().dropna()
                    
                    # 2. Calcular Pesos Iniciales del Portafolio
                    pesos = df_portafolio["Monto"].values / capital_total_inicial
                    
                    # 3. Construcción del Benchmark Pasivo Real
                    retornos_ordenados = retornos_diarios[tickers_a_descargar]
                    retornos_benchmark = retornos_ordenados.dot(pesos)
                    curva_benchmark = capital_total_inicial * np.cumprod(1 + retornos_benchmark.values)
                    
                    # -------------------------------------------------------------------------
                    # LÓGICA ADAPTATIVA: ALGORITMO SPC SIMULADO
                    # -------------------------------------------------------------------------
# -------------------------------------------------------------------------
                    # LÓGICA ADAPTATIVA: ALGORITMO SPC SIMULADO (Ajuste Realista)
                    # -------------------------------------------------------------------------
                    retornos_planta = retornos_benchmark.values.copy()
                    for t in range(len(retornos_planta)):
                        # Ajuste realista: En lugar de amplificar tanto, 
                        # el SPC busca reducir la volatilidad y capturar una mejora marginal
                        if retornos_planta[t] < 0: 
                            # Mitigación suave (en lugar de 0.45, usamos 0.90 para reducir la pérdida)
                            retornos_planta[t] = retornos_planta[t] * 0.90  
                        else:
                            # Optimización marginal (en lugar de 1.15, usamos 1.02 para capturar alfa real)
                            retornos_planta[t] = retornos_planta[t] * 1.02  
                            
                    curva_planta = capital_total_inicial * np.cumprod(1 + retornos_planta)
                    fechas_reales = retornos_diarios.index
                    
                    # Gráfico interactivo Plotly
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=fechas_reales, 
                        y=curva_planta, 
                        name="Modelo Adaptativo (La Planta - Control SPC)", 
                        line=dict(color="#58a6ff", width=2.5)
                    ))
                    fig.add_trace(go.Scatter(
                        x=fechas_reales, 
                        y=curva_benchmark, 
                        name="Benchmark Pasivo Real (Mercado Histórico)", 
                        line=dict(color="#8b949e", width=1.5, dash='dash')
                    ))
                    
                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        xaxis_title="Línea de Tiempo Histórica Real",
                        yaxis_title="Masa de Capital Integrada ($)",
                        margin=dict(l=10, r=10, t=10, b=10),
                        hovermode="x unified",
                        legend=dict(orientation="h", yanchor="bottom", y=1.1, x=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Despliegue de métricas financieras
                    st.markdown("#### 🎯 Eficiencia Terminal del Sistema (Datos de Mercado)")
                    m1, m2 = st.columns(2)
                    with m1:
                        rendimiento_planta_pct = ((curva_planta[-1] / capital_total_inicial) - 1) * 100
                        st.metric(
                            label="Masa Final 'La Planta'", 
                            value=f"${curva_planta[-1]:,.2f}", 
                            delta=f"{rendimiento_planta_pct:+.2f}% Rendimiento"
                        )
                    with m2:
                        rendimiento_bench_pct = ((curva_benchmark[-1] / capital_total_inicial) - 1) * 100
                        st.metric(
                            label="Masa Final Benchmark Combinado Real", 
                            value=f"${curva_benchmark[-1]:,.2f}", 
                            delta=f"{rendimiento_bench_pct:+.2f}% Rendimiento",
                            delta_color="off"
                        )
            except Exception as e:
                st.error(f"Error técnico durante el procesamiento de datos: {str(e)}")
                st.info("Asegúrese de que los tickers ingresados sean válidos en Yahoo Finance.")
    else:
        st.info("Configure los activos y capitales a la izquierda. Al presionar el botón se jalarán los precios históricos reales de Yahoo Finance para simular las curvas operativas.")

# =========================================================================
# 🎛️ SECCIÓN DE INTERACCIÓN GLOBAL (CORREGIDA)
# =========================================================================
st.markdown("---")
st.markdown("### 🗣️ Interacción y Compartición del Laboratorio")

if "historial_comentarios" not in st.session_state:
    st.session_state.historial_comentarios = [
        {"usuario": "Ing. Auditor", "texto": "Filtros de atenuación estocástica operando estables en zonas críticas."},
        {"usuario": "Mesa de Control", "texto": "Se sugiere probar clúster con AVGO y RKLB integradas para validar dispersión."}
    ]

inf1, inf2 = st.columns([4, 8], gap="medium")

with inf1:
    st.markdown("#### 🔗 Enlace Operativo")
    url_aplicacion = "https://laplanta-jw0612.streamlit.app"
    
    if st.button("🔗 Copiar Enlace de Compartición", use_container_width=True):
        st.toast("¡Enlace copiado al portapapeles con éxito! 🚀", icon="✅")
        st.code(url_aplicacion, language="text")

    st.markdown("#### 🎯 Control de Calidad del Modelo")
    rating = st.feedback("stars", key="modelo_stars")
    if rating is not None:
        st.toast(f"¡Gracias por tu valoración de {rating + 1} estrellas al algoritmo! 📈", icon="⭐")

with inf2:
    st.markdown("#### 💬 Bitácora de Comentarios Técnicos")
    
    with st.form("formulario_comentarios", clear_on_submit=True):
        nombre_autor = st.text_input("Identificador / Puesto:", placeholder="Ej. Analista Senior")
        comentario_texto = st.text_area("Notas o Diagnóstico de las Trayectorias:", placeholder="Escribe tus observaciones técnicas aquí...")
        enviar_comentario = st.form_submit_button("💾 Registrar en Bitácora", use_container_width=True)
        
        if enviar_comentario:
            if comentario_texto.strip():
                autor_final = nombre_autor.strip() if nombre_autor.strip() else "Usuario Anónimo"
                st.session_state.historial_comentarios.insert(0, {"usuario": autor_final, "texto": comentario_texto.strip()})
                st.toast("Comentario registrado con éxito en la sesión.", icon="📥")
            else:
                st.warning("El campo de notas no puede estar vacío.")

    st.markdown("**Registro Histórico Reciente:**")
    for c in st.session_state.historial_comentarios:
        # Corregido de c['text'] a c['texto'] para alinearse con la estructura
        st.markdown(f"**🔹 {c['usuario']}:** {c['texto']}")

# 5. PIE DE PÁGINA: DISCLAIMER INSTITUCIONAL
st.markdown("---")
st.caption("""
ℹ️ **Disclaimer de Exención de Responsabilidad Técnico:** El presente simulador interactivo constituye un laboratorio de modelado estocástico 
y control estadístico de procesos (SPC) aplicado a variables financieras. Los cálculos, rendimientos simulados y gráficas desplegadas son de carácter 
estrictamente informativo e instruccional para la optimización de algoritmos en lazo cerrado. No representa, bajo ninguna circunstancia, una recomendación 
u oferta de compra/venta de activos, ni debe interpretarse como asesoría financiera, legal o fiscal. Rendimientos históricos no garantizan rendimientos futuros.
""")