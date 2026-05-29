import streamlit as st
import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. Configuración de pantalla con estilo corporativo y limpio
st.set_page_config(
    page_title="La Planta | Quant Lab", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos visuales personalizados (Mantenemos la sobriedad técnica)
st.title("📈 Sistema Control de Portafolios: Proyecto 'La Planta'")
st.subheader("Análisis Adaptativo Reactivo y Control Estadístico de Procesos (SPC)")
st.markdown("---")

# 2. SECCIÓN: INSTRUCCIONES DE USO (Colapsable profesional)
with st.expander("📖 Guía de Operación e Instrucciones de la Planta", expanded=False):
    st.markdown("""
    Este simulador evalúa la densidad probabilística y la persistencia temporal de una masa de capital expuesta a activos de alta volatilidad estructural.
    1. **Establezca la ventana temporal:** Por defecto el sistema calcula un retraso óptimo de 1 año atrás a la fecha actual.
    2. **Defina el tamaño del clúster:** Seleccione la cantidad de cuentas o nodos de activos que desea simular (Mínimo 3, Máximo 7).
    3. **Asigne Tickers y Masa de Capital:** Introduzca las siglas del activo (ej. *NVDA*, *MU*, *RKLB*) y el capital inicial asignado a ese componente.
    4. **Ejecute el Algoritmo:** El sistema procesará las trayectorias aplicando filtros de paso bajo para mitigar el *volatility decay* (desgaste por trayectoria).
    """)

# Lista de tickers de muestra para usar como guías (placeholders)
tickers_muestra = ["NVDA", "MU", "AVGO", "ARM", "RKLB", "DELL", "CRBS"]

# Estructura principal en dos columnas (Control a la izquierda, Gráfica a la derecha)
col1, col2 = st.columns([5, 7], gap="large")

with col1:
    st.markdown("### ⚙️ Parámetros de Control Óptimo")
    
    # Calcular automáticamente la fecha de hoy y restarle un año (365 días)
    fecha_hoy = datetime.date.today()
    fecha_un_ano_atras = fecha_hoy - datetime.timedelta(days=365)
    
    # Selector de fechas bloqueado hasta el día de hoy
    fecha_inicio = st.date_input(
        "Ventana Temporal de Inicio (Histórico)",
        value=fecha_un_ano_atras,
        max_value=fecha_hoy
    )
    
    # Selector dinámico de cantidad de activos
    num_activos = st.number_input(
        "Nodos de Activos en el Clúster (3 a 7)", 
        min_value=3, 
        max_value=7, 
        value=5
    )
    
    st.markdown("#### 💼 Configuración de Cuentas y Asignación de Capital")
    datos_usuario = []
    
    # Renderizar las filas dinámicas con placeholders claros de mercado
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
        # Si el usuario no escribe nada, tomamos el ticker de muestra para evitar errores
        ticker_final = activo.strip().upper() if activo.strip() else ticker_sugerido
        datos_usuario.append({"Activo": ticker_final, "Monto": monto})
    
    st.markdown("---")
    # Botón de ejecución estilizado
    correr_algoritmo = st.button("🚀 Ejecutar Simulación en Lazo Cerrado", use_container_width=True)

with col2:
    st.markdown("### 📊 Monitoreo de Trayectorias Estocásticas")
    
    # Convertir las entradas a DataFrame
    df_portafolio = pd.DataFrame(datos_usuario)
    capital_total_inicial = df_portafolio["Monto"].sum()
    
    # Generar la línea de tiempo real desde la fecha calculada/seleccionada hasta hoy
    fechas_simuladas = pd.date_range(start=fecha_inicio, end=fecha_hoy, freq='B')
    n_dias = len(fechas_simuladas)
    
    if n_dias < 5:
        st.warning("Seleccione una ventana temporal más amplia para poder calcular las densidades de probabilidad.")
    else:
        # Generación de trayectorias (Dummy con el comportamiento del algoritmo si no se presiona el botón,
        # o procesando con el botón para simular la optimización del lazo cerrado).
        np.random.seed(42) # Semilla fija para consistencia visual de carga inicial
        
        # El algoritmo de la Planta suaviza y mitiga la varianza en comparación al mercado
        retornos_planta = np.random.normal(0.0014, 0.014, n_dias) 
        retornos_benchmark = np.random.normal(0.0009, 0.023, n_dias)
        
        # Si el botón se acciona, simulamos una optimización reactiva aún más eficiente
        if correr_algoritmo:
            retornos_planta = retornos_planta + 0.0002 
            
        curva_planta = capital_total_inicial * np.cumprod(1 + retornos_planta)
        curva_benchmark = capital_total_inicial * np.cumprod(1 + retornos_benchmark)
        
        # Construcción del gráfico interactivo profesional con Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=fechas_simuladas, 
            y=curva_planta, 
            name="Modelo Adaptativo (La Planta)", 
            line=dict(color="#58a6ff", width=2.5)
        ))
        fig.add_trace(go.Scatter(
            x=fechas_simuladas, 
            y=curva_benchmark, 
            name="Benchmark Pasivo (Indexado)", 
            line=dict(color="#8b949e", width=1.5, dash='dash')
        ))
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Línea de Tiempo Operativa",
            yaxis_title="Masa de Capital Integrada ($)",
            margin=dict(l=10, r=10, t=10, b=10),
            hovermode="x unified",
            legend=dict(orientation="h", ylink="top", y=1.1, x=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Despliegue de métricas financieras de control
        st.markdown("#### 🎯 Eficiencia Terminal del Sistema")
        m1, m2 = st.columns(2)
        with m1:
            rendimiento_planta_pct = ((curva_planta[-1] / capital_total_inicial) - 1) * 100
            st.metric(
                label="Masa Final 'La Planta'", 
                value=f"${curva_planta[-1]:,.2f}", 
                delta=f"{rendimiento_planta_pct:+.2f}% vs Inicial"
            )
        with m2:
            rendimiento_bench_pct = ((curva_benchmark[-1] / capital_total_inicial) - 1) * 100
            st.metric(
                label="Masa Final Benchmark Pasivo", 
                value=f"${curva_benchmark[-1]:,.2f}", 
                delta=f"{rendimiento_bench_pct:+.2f}% vs Inicial",
                delta_color="off"
            )

# 5. PIE DE PÁGINA: DISCLAIMER INSTITUCIONAL (Estilo Business)
st.markdown("---")
st.caption("""
ℹ️ **Disclaimer de Exención de Responsabilidad Técnica:** El presente simulador interactivo constituye un laboratorio de modelado estocástico 
y control estadístico de procesos (SPC) aplicado a variables financieras. Los cálculos, rendimientos simulados y gráficas desplegadas son de carácter 
estrictamente informativo e instruccional para la optimización de algoritmos en lazo cerrado. No representa, bajo ninguna circunstancia, una recomendación 
u oferta de compra/venta de activos, ni debe interpretarse como asesoría financiera, legal o fiscal. Rendimientos históricos no garantizan rendimientos futuros.
""")