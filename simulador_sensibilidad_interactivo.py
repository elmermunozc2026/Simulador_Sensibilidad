import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Simulador de Sensibilidad e Incertidumbre FP&A",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para apariencia corporativa
st.markdown("""
<style>
    .reportview-container {
        background-color: #F8F9FA;
    }
    .main-title {
        color: #1F4E78;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .section-title {
        color: #2F5496;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: bold;
        border-bottom: 2px solid #2F5496;
        padding-bottom: 5px;
        margin-top: 30px;
        margin-bottom: 15px;
    }
    .metric-box {
        background-color: #E2EFDA;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #C6E0B4;
        text-align: center;
    }
    .metric-val {
        font-size: 24px;
        font-weight: bold;
        color: #375623;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>Simulador Interactivo de Sensibilidad e Incertidumbre (VAN)</h1>", unsafe_allow_html=True)
st.markdown("""
### **Módulo 6: Evaluación Financiera de Inversiones y Proyectos**
Este modelo interactivo permite a los estudiantes de postgrado analizar de forma **simultánea y dinámica** cómo interactúan el **Precio de Venta**, 
el **Volumen de Ventas** y la **Tasa Impositiva Corporativa** en la determinación del **Valor Actual Neto (VAN)** esperado de un proyecto de expansión.

El caso está parametrizado con base en la literatura del curso (inversión física en maquinarias de $300,000 con depreciación lineal, capital de trabajo del 18% y valor de salvamento).
""")

# --- SIDEBAR: Parámetros del Proyecto ---
st.sidebar.header("1. Parámetros Base del Proyecto")

# Inputs determinísticos / base
precio_base = st.sidebar.slider(
    "Precio de Venta Base ($/unidad)", 
    min_value=100.0, 
    max_value=300.0, 
    value=200.0, 
    step=5.0,
    help="Precio de venta unitario del producto."
)

volumen_base = st.sidebar.slider(
    "Volumen de Ventas Base (unidades/año)", 
    min_value=500, 
    max_value=2000, 
    value=1000, 
    step=50,
    help="Cantidad de unidades vendidas al año."
)

tax_rate = st.sidebar.slider(
    "Tasa Impositiva Corporativa (%)", 
    min_value=0.0, 
    max_value=50.0, 
    value=35.0, 
    step=1.0,
    help="Tasa marginal de impuesto sobre la renta aplicable a las utilidades corporativas."
) / 100.0

tasa_descuento = st.sidebar.slider(
    "Tasa de Descuento (k) (%)", 
    min_value=5.0, 
    max_value=20.0, 
    value=12.0, 
    step=0.5,
    help="Tasa de corte o costo de oportunidad exigido al proyecto."
) / 100.0

st.sidebar.markdown("---")
st.sidebar.header("2. Simulación de Incertidumbre")
activar_simulacion = st.sidebar.checkbox(
    "Activar Simulación de Monte Carlo", 
    value=False,
    help="Permite modelar el precio y el volumen como variables aleatorias normales con volatilidad ajustable."
)

if activar_simulacion:
    vol_precio = st.sidebar.slider(
        "Volatilidad del Precio (%)", 
        min_value=0.0, 
        max_value=30.0, 
        value=10.0, 
        step=1.0,
        help="Desviación estándar porcentual de la distribución normal del precio."
    ) / 100.0

    vol_volumen = st.sidebar.slider(
        "Volatilidad del Volumen (%)", 
        min_value=0.0, 
        max_value=30.0, 
        value=15.0, 
        step=1.0,
        help="Desviación estándar porcentual de la distribución normal del volumen de ventas."
    ) / 100.0
    
    num_simulaciones = st.sidebar.number_input(
        "Número de Iteraciones", 
        min_value=1000, 
        max_value=10000, 
        value=5000, 
        step=1000
    )

# --- PARÁMETROS FIJOS (Grounded in Sources) ---
I0 = 300000          # Inversión física inicial en maquinarias
dep_anual = 60000    # Depreciación lineal anual (300,000 / 5 años)
costo_var = 80.0     # Costo variable unitario
costo_fijo = 50000   # Costos fijos operativos anuales
cap_trabajo = 54000  # Capital de trabajo inicial (18% de 300,000)
salvamento = 120000  # Valor de salvamento bruto (40% de 300,000)

# --- FUNCIONES DE CÁLCULO ---
def calcular_proyecto_van(precio, volumen, tax, k):
    # Año 0
    fcn_0 = -I0 - cap_trabajo
    
    # Años 1 a 4
    fcn = []
    for t in range(1, 5):
        ventas = precio * volumen
        costos_variables = costo_var * volumen
        ebit = ventas - costos_variables - costo_fijo - dep_anual
        impuesto = max(0.0, ebit * tax)
        nopat = ebit - impuesto
        ocf = nopat + dep_anual
        fcn.append(ocf)
        
    # Año 5 (Operación + Salvamento Neto + Recuperación Cap de Trabajo)
    ventas_5 = precio * volumen
    costos_variables_5 = costo_var * volumen
    ebit_5 = ventas_5 - costos_variables_5 - costo_fijo - dep_anual
    impuesto_5 = max(0.0, ebit_5 * tax)
    nopat_5 = ebit_5 - impuesto_5
    ocf_5 = nopat_5 + dep_anual
    
    # Salvamento Neto de Impuesto (Valor en libros es 0 tras 5 años de depreciación lineal de $60,000/año)
    salvamento_neto = salvamento * (1 - tax)
    
    fcn_5 = ocf_5 + salvamento_neto + cap_trabajo
    fcn.append(fcn_5)
    
    # Calcular VAN
    van = fcn_0
    for t, flujo in enumerate(fcn):
        van += flujo / ((1 + k) ** (t + 1))
        
    return van, fcn_0, fcn

def calcular_tir_biseccion(flujos, max_iter=100, tol=1e-6):
    # Solver de bisección robusto para proyectos convencionales
    if len(flujos) == 0:
        return 0.0
    low, high = -0.99, 2.0
    
    # Evaluar extremos
    def f_van(r):
        v = flujos[0]
        for t, f in enumerate(flujos[1:]):
            v += f / ((1 + r) ** (t + 1))
        return v
        
    f_low = f_van(low)
    f_high = f_van(high)
    
    if f_low * f_high > 0:
        return 0.0 if f_high < 0 else 2.0 # Límites excedidos
        
    for _ in range(max_iter):
        mid = (low + high) / 2.0
        v_mid = f_van(mid)
        if abs(v_mid) < tol:
            return mid
        if v_mid > 0:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0

# --- ESCENARIO DETERMINÍSTICO ---
if not activar_simulacion:
    van_base, f_0, flujos_operativos = calcular_proyecto_van(precio_base, volumen_base, tax_rate, tasa_descuento)
    
    st.markdown("<h2 class='section-title'>I. Proyección del Flujo de Caja Base</h2>", unsafe_allow_html=True)
    
    # Crear DataFrame de flujos para mostrar al alumno
    columnas_años = ["Año 0", "Año 1", "Año 2", "Año 3", "Año 4", "Año 5"]
    conceptos = [
        "Ingresos por Ventas",
        "Costos Variables",
        "Costos Fijos Operativos",
        "Depreciación",
        "Utilidad Operativa (EBIT)",
        "Impuesto a la Renta",
        "Utilidad Neta Operativa (NOPAT)",
        "Ajuste Depreciación (+)",
        "Flujo de Inversión Inicial",
        "Valor de Salvamento Neto",
        "Recuperación Capital Trabajo",
        "Flujo de Caja Neto (FCN)"
    ]
    
    valores_tabla = []
    
    # Año 0
    valores_tabla.append([
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -I0 - cap_trabajo, 0.0, 0.0, -I0 - cap_trabajo
    ])
    
    # Años 1 a 4
    for t in range(1, 5):
        v = precio_base * volumen_base
        cv = costo_var * volumen_base
        ebit = v - cv - costo_fijo - dep_anual
        imp = max(0.0, ebit * tax_rate)
        nop = ebit - imp
        ocf = nop + dep_anual
        valores_tabla.append([
            v, -cv, -costo_fijo, -dep_anual, ebit, -imp, nop, dep_anual, 0.0, 0.0, 0.0, ocf
        ])
        
    # Año 5
    v_5 = precio_base * volumen_base
    cv_5 = costo_var * volumen_base
    ebit_5 = v_5 - cv_5 - costo_fijo - dep_anual
    imp_5 = max(0.0, ebit_5 * tax_rate)
    nop_5 = ebit_5 - imp_5
    ocf_5 = nop_5 + dep_anual
    salv_neto = salvamento * (1 - tax_rate)
    fcn_5 = ocf_5 + salv_neto + cap_trabajo
    valores_tabla.append([
        v_5, -cv_5, -costo_fijo, -dep_anual, ebit_5, -imp_5, nop_5, dep_anual, 0.0, salv_neto, cap_trabajo, fcn_5
    ])
    
    # Transponer para que los conceptos sean filas y los años columnas
    arr_valores = np.array(valores_tabla).T
    df_flujos = pd.DataFrame(arr_valores, index=conceptos, columns=columnas_años)
    
    st.dataframe(df_flujos.style.format("${:,.2f}").highlight_min(axis=1, color="#FFD9CC").highlight_max(axis=1, color="#E2EFDA"))
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class='metric-box'>
            <p style='margin:0; font-size:16px; color:#595959;'>Valor Actual Neto (VAN) Base</p>
            <p class='metric-val'>${van_base:,.2f}</p>
            <p style='margin:0; font-size:12px; color:#595959;'>Con Tasa de Descuento (k) del {tasa_descuento*100:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        # Calcular TIR usando nuestro robusto solver de bisección
        flujos_tir = [f_0] + flujos_operativos
        tir_val = calcular_tir_biseccion(flujos_tir)
                
        st.markdown(f"""
        <div class='metric-box' style='background-color:#D9E1F2; border-color:#8FAADC;'>
            <p style='margin:0; font-size:16px; color:#595959;'>Tasa Interna de Retorno (TIR)</p>
            <p class='metric-val' style='color:#1F4E78;'>{tir_val*100:.2f}%</p>
            <p style='margin:0; font-size:12px; color:#595959;'>Rentabilidad promedio anual de los saldos de capital</p>
        </div>
        """, unsafe_allow_html=True)

    # --- ANÁLISIS DE SENSIBILIDAD BIDIMENSIONAL ---
    st.markdown("<h2 class='section-title'>II. Análisis de Sensibilidad Cruzada (Precio vs. Volumen)</h2>", unsafe_allow_html=True)
    st.markdown("Esta tabla bidimensional muestra el **VAN resultante** para diferentes combinaciones de precio y volumen, manteniendo la tasa impositiva fija en el **{:.0f}%**.".format(tax_rate*100))
    
    rango_precios = np.linspace(precio_base * 0.8, precio_base * 1.2, 7)
    rango_volumenes = np.linspace(volumen_base * 0.8, volumen_base * 1.2, 7)
    
    matriz_sensibilidad = []
    for vol in rango_volumenes:
        fila = []
        for pr in rango_precios:
            van_s, _, _ = calcular_proyecto_van(pr, vol, tax_rate, tasa_descuento)
            fila.append(van_s)
        matriz_sensibilidad.append(fila)
        
    df_sens = pd.DataFrame(
        matriz_sensibilidad, 
        index=[f"{v:,.0f} und" for v in rango_volumenes],
        columns=[f"${p:,.1f}" for p in rango_precios]
    )
    
    # Mostrar matriz de calor
    fig_heat, ax_heat = plt.subplots(figsize=(10, 5))
    sns.heatmap(
        df_sens, 
        annot=True, 
        fmt=",.0f", 
        cmap="RdYlGn", 
        center=0, 
        cbar_kws={'label': 'VAN en USD'},
        ax=ax_heat
    )
    ax_heat.set_title("Sensibilidad Cruzada del VAN ($)", fontsize=12, fontweight='bold', color='#1F4E78')
    ax_heat.set_xlabel("Precio de Venta ($/unidad)", fontsize=10, fontweight='bold')
    ax_heat.set_ylabel("Volumen de Unidades Vendidas", fontsize=10, fontweight='bold')
    st.pyplot(fig_heat)

# --- ESCENARIO DE SIMULACIÓN MONTE CARLO ---
else:
    st.markdown("<h2 class='section-title'>I. Análisis Estadístico y Simulación de Incertidumbre</h2>", unsafe_allow_html=True)
    st.markdown("Se modelan el precio y el volumen como **variables normales independientes** con las volatilidades seleccionadas.")
    
    # Correr simulación
    np.random.seed(42) # Fijo para reproducibilidad pedagógica
    
    precios_sim = np.random.normal(precio_base, precio_base * vol_precio, num_simulaciones)
    volumenes_sim = np.random.normal(volumen_base, volumen_base * vol_volumen, num_simulaciones)
    
    vans_sim = []
    for pr, vol in zip(precios_sim, volumenes_sim):
        van_s, _, _ = calcular_proyecto_van(pr, vol, tax_rate, tasa_descuento)
        vans_sim.append(van_s)
        
    vans_sim = np.array(vans_sim)
    
    # Calcular estadísticas clave
    van_esperado = np.mean(vans_sim)
    sd_van = np.std(vans_sim)
    cv_van = sd_van / van_esperado if van_esperado != 0 else 0
    prob_exito = np.mean(vans_sim > 0) * 100.0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class='metric-box'>
            <p style='margin:0; font-size:14px; color:#595959;'>VAN Esperado Promedio</p>
            <p class='metric-val'>${van_esperado:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='metric-box' style='background-color:#FCE4D6; border-color:#F8CBAD;'>
            <p style='margin:0; font-size:14px; color:#595959;'>Desviación Estándar (σ)</p>
            <p class='metric-val' style='color:#C65911;'>${sd_van:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class='metric-box' style='background-color:#FFF2CC; border-color:#FFE699;'>
            <p style='margin:0; font-size:14px; color:#595959;'>Coeficiente de Variación</p>
            <p class='metric-val' style='color:#7F6000;'>{cv_van:.4f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        # Condicionar el color de la probabilidad
        color_prob = "#375623" if prob_exito >= 70 else ("#7F6000" if prob_exito >= 50 else "#C65911")
        bg_prob = "#E2EFDA" if prob_exito >= 70 else ("#FFF2CC" if prob_exito >= 50 else "#FCE4D6")
        border_prob = "#C6E0B4" if prob_exito >= 70 else ("#FFE699" if prob_exito >= 50 else "#F8CBAD")
        st.markdown(f"""
        <div class='metric-box' style='background-color:{bg_prob}; border-color:{border_prob};'>
            <p style='margin:0; font-size:14px; color:#595959;'>Probabilidad de VAN > 0</p>
            <p class='metric-val' style='color:{color_prob};'>{prob_exito:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)

    # --- HISTOGRAMA DE DISTRIBUCIÓN DE RIESGO ---
    st.markdown("<h2 class='section-title'>II. Histograma de Distribución de Probabilidades del VAN</h2>", unsafe_allow_html=True)
    
    fig_hist, ax_hist = plt.subplots(figsize=(10, 5))
    
    # Graficar histograma con barras coloreadas según si es positivo o negativo
    n_bins = 50
    counts, bins, patches = ax_hist.hist(vans_sim, bins=n_bins, edgecolor='black', alpha=0.7)
    
    # Colorear según el signo del VAN
    for patch, left_bin in zip(patches, bins[:-1]):
        if left_bin >= 0:
            patch.set_facecolor('#A9D08E') # Verde suave para éxito
        else:
            patch.set_facecolor('#F8CBAD') # Rojo/Naranja suave para pérdida
            
    ax_hist.axvline(x=0, color='red', linestyle='--', linewidth=2, label="Umbral de Rentabilidad (VAN = 0)")
    ax_hist.axvline(x=van_esperado, color='#2F5496', linestyle='-', linewidth=2.5, label=f"VAN Esperado Promedio (${van_esperado:,.0f})")
    
    ax_hist.set_title("Frecuencia de Resultados del VAN ante Incertidumbre Combinada", fontsize=12, fontweight='bold', color='#1F4E78')
    ax_hist.set_xlabel("Valor Actual Neto (USD)", fontsize=10, fontweight='bold')
    ax_hist.set_ylabel("Frecuencia (Ensayos)", fontsize=10, fontweight='bold')
    ax_hist.grid(True, linestyle=':', alpha=0.5)
    ax_hist.legend(loc="upper left")
    
    st.pyplot(fig_hist)

st.markdown("---")
st.markdown("""
### **Guía de Preguntas para Debatir en el Aula (Pedagogía FP&A):**
1. **La Interacción del Impuesto:** Si aumentas la Tasa Impositiva al 45%, ¿qué efecto tiene sobre el Coeficiente de Variación (CV) y la dispersión del VAN? *(Tip: El impuesto actúa reduciendo la variabilidad absoluta de los flujos operativos, pero deprime el promedio esperado de rentabilidad).*
2. **La Variable Más Sensible:** En la simulación determinística, ¿por qué un cambio del 10% en el precio de venta altera el VAN de manera mucho más severa que un cambio del 10% en el volumen de ventas?
3. **La Utilidad de las Opciones Reales:** En escenarios donde la probabilidad de éxito (VAN > 0) cae por debajo del 50%, ¿cómo puede la administración utilizar la *Opción Real de Abandono* o la *Opción de Esperar* para salvar el capital inicial?
""")
