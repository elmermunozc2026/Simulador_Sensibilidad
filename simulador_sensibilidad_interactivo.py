import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Simulador de Sensibilidad e Incertidumbre FP&A",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# ESTILOS CSS CORPORATIVOS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .reportview-container { background-color: #F8F9FA; }
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
    div[data-testid="stSidebar"] .stNumberInput label {
        font-size: 11px !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TÍTULO PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<h1 class='main-title'>Simulador Interactivo de Sensibilidad e Incertidumbre (VAN)</h1>",
            unsafe_allow_html=True)
st.markdown("""
### **Módulo 6: Evaluación Financiera de Inversiones y Proyectos**
Este modelo interactivo permite analizar de forma **simultánea y dinámica** cómo interactúan el
**Precio de Venta**, el **Volumen de Ventas**, los **Costos** y la **Tasa Impositiva Corporativa**
en la determinación del **Valor Actual Neto (VAN)** esperado de un proyecto de inversión.
""")

# ─────────────────────────────────────────────────────────────────────────────
# HELPER: SINCRONIZACIÓN SLIDER ↔ NUMBER_INPUT  (sidebar)
# ─────────────────────────────────────────────────────────────────────────────
def synced_sidebar(label, key, min_val, max_val, default, step,
                   fmt="%.2f", help_text="", is_int=False):
    """
    Renderiza number_input + slider sincronizados en el SIDEBAR.
    Devuelve el valor actual.
    """
    key_num = f"{key}_num"
    key_sld = f"{key}_sld"

    if key not in st.session_state:
        st.session_state[key] = default

    def on_num():
        st.session_state[key] = st.session_state[key_num]

    def on_sld():
        st.session_state[key] = st.session_state[key_sld]

    cur = st.session_state[key]

    if is_int:
        st.sidebar.number_input(label, min_value=int(min_val), max_value=int(max_val),
                                value=int(cur), step=int(step),
                                key=key_num, on_change=on_num, help=help_text)
        st.sidebar.slider("", min_value=int(min_val), max_value=int(max_val),
                          value=int(st.session_state[key]), step=int(step),
                          key=key_sld, on_change=on_sld,
                          label_visibility="collapsed")
    else:
        st.sidebar.number_input(label, min_value=float(min_val), max_value=float(max_val),
                                value=float(cur), step=float(step), format=fmt,
                                key=key_num, on_change=on_num, help=help_text)
        st.sidebar.slider("", min_value=float(min_val), max_value=float(max_val),
                          value=float(st.session_state[key]), step=float(step),
                          key=key_sld, on_change=on_sld,
                          label_visibility="collapsed")

    return st.session_state[key]


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR – SECCIÓN 1: PARÁMETROS BASE DEL PROYECTO
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.header("1. Parámetros Base del Proyecto")

n_periodos = int(synced_sidebar(
    "Número de Períodos (años)", "n_periodos",
    1, 20, 5, 1, "%d",
    "Horizonte de evaluación del proyecto en años.", is_int=True
))

st.sidebar.markdown("---")

precio_base = synced_sidebar(
    "Precio de Venta Base ($/unidad)", "precio_base",
    50.0, 500.0, 200.0, 5.0, "%.1f",
    "Precio de venta unitario del producto."
)

costo_var = synced_sidebar(
    "Costo Variable Unitario ($/unidad)", "costo_var",
    10.0, 400.0, 80.0, 5.0, "%.1f",
    "Costo variable por unidad producida/vendida."
)

volumen_base = int(synced_sidebar(
    "Volumen de Ventas Base (unidades/año)", "volumen_base",
    100, 5000, 1000, 50, "%d",
    "Cantidad de unidades vendidas al año.", is_int=True
))

costo_fijo = synced_sidebar(
    "Costo Fijo Anual ($)", "costo_fijo",
    0.0, 500000.0, 50000.0, 5000.0, "%.0f",
    "Costos fijos operativos anuales totales."
)

st.sidebar.markdown("---")

tax_rate_pct = synced_sidebar(
    "Tasa Impositiva Corporativa (%)", "tax_rate_pct",
    0.0, 60.0, 35.0, 1.0, "%.1f",
    "Tasa marginal de impuesto sobre la renta corporativa."
)
tax_rate = tax_rate_pct / 100.0

tasa_desc_pct = synced_sidebar(
    "Tasa de Descuento / WACC (%)", "tasa_desc_pct",
    1.0, 40.0, 12.0, 0.5, "%.1f",
    "Tasa de corte o costo de oportunidad exigido al proyecto."
)
tasa_descuento = tasa_desc_pct / 100.0

st.sidebar.markdown("---")

tipo_cambio = synced_sidebar(
    "Tipo de Cambio (moneda local / USD)", "tipo_cambio",
    0.5, 20.0, 1.0, 0.05, "%.2f",
    "Unidades de moneda local por cada USD. Use 1.0 si trabaja en USD."
)

inversion_inicial = synced_sidebar(
    "Inversión Inicial ($)", "inversion_inicial",
    10000.0, 5000000.0, 300000.0, 10000.0, "%.0f",
    "Desembolso de capital inicial (CAPEX) en el período 0."
)

cap_trabajo_pct = synced_sidebar(
    "Capital de Trabajo (% de Inversión)", "cap_trabajo_pct",
    0.0, 50.0, 18.0, 1.0, "%.1f",
    "Capital de trabajo inicial como porcentaje de la inversión física."
)
cap_trabajo = inversion_inicial * cap_trabajo_pct / 100.0

salvamento_pct = synced_sidebar(
    "Valor de Salvamento (% de Inversión)", "salvamento_pct",
    0.0, 100.0, 40.0, 5.0, "%.1f",
    "Valor residual al final del horizonte como % de la inversión inicial."
)
salvamento = inversion_inicial * salvamento_pct / 100.0

dep_anual = inversion_inicial / n_periodos if n_periodos > 0 else 0.0

st.sidebar.markdown("---")
st.sidebar.caption(
    f"📌 Depreciación lineal automática: **${dep_anual:,.0f}/año** ({n_periodos} períodos)"
)
st.sidebar.caption(
    f"📌 Capital de trabajo: **${cap_trabajo:,.0f}** "
    f"({cap_trabajo_pct:.0f}% de ${inversion_inicial:,.0f})"
)
st.sidebar.caption(
    f"📌 Valor de salvamento: **${salvamento:,.0f}** "
    f"({salvamento_pct:.0f}% de ${inversion_inicial:,.0f})"
)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR – SECCIÓN 2: SIMULACIÓN DE INCERTIDUMBRE
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.header("2. Simulación de Incertidumbre")

activar_simulacion = st.sidebar.checkbox(
    "Activar Simulación de Monte Carlo", value=False,
    help="Modela precio y volumen como variables aleatorias normales con volatilidad ajustable."
)

vol_precio = 0.10
vol_volumen = 0.15
num_simulaciones = 5000

if activar_simulacion:
    vol_precio = synced_sidebar(
        "Volatilidad del Precio (%)", "vol_precio",
        1.0, 50.0, 10.0, 1.0, "%.1f",
        "Desviación estándar porcentual de la distribución normal del precio."
    ) / 100.0

    vol_volumen = synced_sidebar(
        "Volatilidad del Volumen (%)", "vol_volumen",
        1.0, 50.0, 15.0, 1.0, "%.1f",
        "Desviación estándar porcentual de la distribución normal del volumen."
    ) / 100.0

    num_simulaciones = int(synced_sidebar(
        "Número de Iteraciones", "num_simulaciones",
        500, 20000, 5000, 500, "%d",
        "Cantidad de escenarios aleatorios a simular.", is_int=True
    ))

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR – SECCIÓN 3: ANÁLISIS DE TORNADO
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.header("3. Análisis de Tornado")
st.sidebar.markdown("**Variación para escenarios (%):**")

var_pesimista_pct = synced_sidebar(
    "Variación Pesimista (%)", "var_pesimista_pct",
    5.0, 50.0, 20.0, 5.0, "%.0f",
    "Porcentaje de reducción para el escenario pesimista de cada variable."
)

var_optimista_pct = synced_sidebar(
    "Variación Optimista (%)", "var_optimista_pct",
    5.0, 50.0, 20.0, 5.0, "%.0f",
    "Porcentaje de incremento para el escenario optimista de cada variable."
)

st.sidebar.markdown("**Ajuste fino por variable:**")

var_precio_pes = st.sidebar.number_input(
    "Precio – Var. Pesimista (%)", 1.0, 80.0, float(var_pesimista_pct), 1.0, key="vp_pes")
var_precio_opt = st.sidebar.number_input(
    "Precio – Var. Optimista (%)", 1.0, 80.0, float(var_optimista_pct), 1.0, key="vp_opt")
var_cv_pes = st.sidebar.number_input(
    "Costo Variable – Var. Pesimista (%)", 1.0, 80.0, float(var_pesimista_pct), 1.0, key="vcv_pes")
var_cv_opt = st.sidebar.number_input(
    "Costo Variable – Var. Optimista (%)", 1.0, 80.0, float(var_optimista_pct), 1.0, key="vcv_opt")
var_vol_pes = st.sidebar.number_input(
    "Volumen – Var. Pesimista (%)", 1.0, 80.0, float(var_pesimista_pct), 1.0, key="vvol_pes")
var_vol_opt = st.sidebar.number_input(
    "Volumen – Var. Optimista (%)", 1.0, 80.0, float(var_optimista_pct), 1.0, key="vvol_opt")
var_cf_pes = st.sidebar.number_input(
    "Costo Fijo – Var. Pesimista (%)", 1.0, 80.0, float(var_pesimista_pct), 1.0, key="vcf_pes")
var_cf_opt = st.sidebar.number_input(
    "Costo Fijo – Var. Optimista (%)", 1.0, 80.0, float(var_optimista_pct), 1.0, key="vcf_opt")

# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES DE CÁLCULO FINANCIERO (REUTILIZABLES)
# ─────────────────────────────────────────────────────────────────────────────

def calcular_flujos(precio, volumen, tax, k, n, I0, dep, cap_trab, salv, cv, cf, tc):
    """Calcula flujos de caja netos para n períodos. Retorna (van, fcn_0, flujos_op)."""
    fcn_0 = -(I0 + cap_trab)
    flujos_op = []
    for t in range(1, n + 1):
        ventas   = precio * volumen * tc
        costos_v = cv * volumen * tc
        ebit     = ventas - costos_v - cf - dep
        impuesto = max(0.0, ebit * tax)
        nopat    = ebit - impuesto
        ocf      = nopat + dep
        if t == n:
            ocf += salv * (1 - tax) + cap_trab
        flujos_op.append(ocf)

    van = fcn_0
    for t, flujo in enumerate(flujos_op):
        van += flujo / ((1 + k) ** (t + 1))
    return van, fcn_0, flujos_op


def calcular_tir_biseccion(flujos_completos, max_iter=200, tol=1e-8):
    """Solver de bisección robusto para TIR."""
    if len(flujos_completos) < 2:
        return 0.0

    def f_van(r):
        v = flujos_completos[0]
        for t, f in enumerate(flujos_completos[1:]):
            v += f / ((1 + r) ** (t + 1))
        return v

    low, high = -0.9999, 5.0
    if f_van(low) * f_van(high) > 0:
        return 0.0 if f_van(high) < 0 else 5.0

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


def calcular_van_tornado(param_nombre, factor_pes, factor_opt,
                         precio, volumen, tax, k, n, I0, dep,
                         cap_trab, salv, cv, cf, tc):
    """Calcula VAN pesimista y optimista para una variable (OAT)."""
    base = dict(precio=precio, volumen=volumen, tax=tax, k=k, n=n,
                I0=I0, dep=dep, cap_trab=cap_trab, salv=salv, cv=cv, cf=cf, tc=tc)

    def van_con(**ov):
        p = {**base, **ov}
        v, _, _ = calcular_flujos(p["precio"], p["volumen"], p["tax"], p["k"],
                                   p["n"], p["I0"], p["dep"], p["cap_trab"],
                                   p["salv"], p["cv"], p["cf"], p["tc"])
        return v

    if param_nombre == "Precio de Venta":
        return van_con(precio=precio * factor_pes), van_con(precio=precio * factor_opt)
    elif param_nombre == "Costo Variable":
        return van_con(cv=cv * factor_opt), van_con(cv=cv * factor_pes)
    elif param_nombre == "Volumen de Ventas":
        return van_con(volumen=volumen * factor_pes), van_con(volumen=volumen * factor_opt)
    elif param_nombre == "Costo Fijo":
        return van_con(cf=cf * factor_opt), van_con(cf=cf * factor_pes)
    elif param_nombre == "Tasa de Descuento":
        return van_con(k=k * factor_opt), van_con(k=k * factor_pes)
    elif param_nombre == "Inversión Inicial":
        return van_con(I0=I0 * factor_opt), van_con(I0=I0 * factor_pes)
    elif param_nombre == "Valor de Salvamento":
        return van_con(salv=salv * factor_pes), van_con(salv=salv * factor_opt)
    return 0.0, 0.0


# ─────────────────────────────────────────────────────────────────────────────
# CÁLCULO BASE
# ─────────────────────────────────────────────────────────────────────────────
van_base, fcn_0_base, flujos_op_base = calcular_flujos(
    precio_base, volumen_base, tax_rate, tasa_descuento, n_periodos,
    inversion_inicial, dep_anual, cap_trabajo, salvamento,
    costo_var, costo_fijo, tipo_cambio
)
tir_val = calcular_tir_biseccion([fcn_0_base] + flujos_op_base)

# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN I – PROYECCIÓN DEL FLUJO DE CAJA BASE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<h2 class='section-title'>I. Proyección del Flujo de Caja Base</h2>",
            unsafe_allow_html=True)

columnas_años = ["Año 0"] + [f"Año {t}" for t in range(1, n_periodos + 1)]
conceptos = [
    "Ingresos por Ventas", "Costos Variables", "Costos Fijos Operativos",
    "Depreciación", "Utilidad Operativa (EBIT)", "Impuesto a la Renta",
    "Utilidad Neta Operativa (NOPAT)", "Ajuste Depreciación (+)",
    "Flujo de Inversión Inicial", "Valor de Salvamento Neto",
    "Recuperación Capital Trabajo", "Flujo de Caja Neto (FCN)"
]

valores_tabla = []
valores_tabla.append([
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    -(inversion_inicial + cap_trabajo), 0.0, 0.0,
    -(inversion_inicial + cap_trabajo)
])

for t in range(1, n_periodos + 1):
    v    = precio_base * volumen_base * tipo_cambio
    cv_t = costo_var * volumen_base * tipo_cambio
    ebit = v - cv_t - costo_fijo - dep_anual
    imp  = max(0.0, ebit * tax_rate)
    nop  = ebit - imp
    ocf  = nop + dep_anual
    salv_neto_t = salvamento * (1 - tax_rate) if t == n_periodos else 0.0
    cap_rec_t   = cap_trabajo if t == n_periodos else 0.0
    fcn_t = ocf + salv_neto_t + cap_rec_t
    valores_tabla.append([
        v, -cv_t, -costo_fijo, -dep_anual, ebit, -imp, nop,
        dep_anual, 0.0, salv_neto_t, cap_rec_t, fcn_t
    ])

df_flujos = pd.DataFrame(
    np.array(valores_tabla).T, index=conceptos, columns=columnas_años
)
st.dataframe(
    df_flujos.style
    .format("${:,.2f}")
    .highlight_min(axis=1, color="#FFD9CC")
    .highlight_max(axis=1, color="#E2EFDA"),
    use_container_width=True
)

# Métricas VAN y TIR
col1, col2 = st.columns(2)
with col1:
    color_van  = "#375623" if van_base >= 0 else "#C65911"
    bg_van     = "#E2EFDA" if van_base >= 0 else "#FCE4D6"
    border_van = "#C6E0B4" if van_base >= 0 else "#F8CBAD"
    decision   = "✅ ACEPTAR (VAN > 0)" if van_base >= 0 else "❌ RECHAZAR (VAN < 0)"
    st.markdown(f"""
    <div class='metric-box' style='background-color:{bg_van}; border-color:{border_van};'>
        <p style='margin:0; font-size:16px; color:#595959;'>Valor Actual Neto (VAN) Base</p>
        <p class='metric-val' style='color:{color_van};'>${van_base:,.2f}</p>
        <p style='margin:0; font-size:12px; color:#595959;'>
            Tasa de Descuento: {tasa_descuento*100:.1f}% | Períodos: {n_periodos} años
        </p>
        <p style='margin:0; font-size:13px; font-weight:bold; color:{color_van};'>{decision}</p>
    </div>""", unsafe_allow_html=True)

with col2:
    color_tir  = "#1F4E78" if tir_val >= tasa_descuento else "#C65911"
    bg_tir     = "#D9E1F2" if tir_val >= tasa_descuento else "#FCE4D6"
    border_tir = "#8FAADC" if tir_val >= tasa_descuento else "#F8CBAD"
    tir_dec    = f"✅ TIR > WACC ({tasa_descuento*100:.1f}%)" if tir_val >= tasa_descuento \
                 else f"❌ TIR < WACC ({tasa_descuento*100:.1f}%)"
    st.markdown(f"""
    <div class='metric-box' style='background-color:{bg_tir}; border-color:{border_tir};'>
        <p style='margin:0; font-size:16px; color:#595959;'>Tasa Interna de Retorno (TIR)</p>
        <p class='metric-val' style='color:{color_tir};'>{tir_val*100:.2f}%</p>
        <p style='margin:0; font-size:12px; color:#595959;'>Rentabilidad promedio anual del proyecto</p>
        <p style='margin:0; font-size:13px; font-weight:bold; color:{color_tir};'>{tir_dec}</p>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN II – SENSIBILIDAD CRUZADA / MONTE CARLO
# ─────────────────────────────────────────────────────────────────────────────
if not activar_simulacion:
    st.markdown(
        "<h2 class='section-title'>II. Análisis de Sensibilidad Cruzada (Precio vs. Volumen)</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"Tabla bidimensional del **VAN** para combinaciones de precio y volumen "
        f"(tasa impositiva fija: **{tax_rate*100:.0f}%**, períodos: **{n_periodos} años**)."
    )

    rango_precios   = np.linspace(precio_base * 0.8, precio_base * 1.2, 7)
    rango_volumenes = np.linspace(volumen_base * 0.8, volumen_base * 1.2, 7)

    matriz = []
    for vol in rango_volumenes:
        fila = []
        for pr in rango_precios:
            van_s, _, _ = calcular_flujos(
                pr, vol, tax_rate, tasa_descuento, n_periodos,
                inversion_inicial, dep_anual, cap_trabajo, salvamento,
                costo_var, costo_fijo, tipo_cambio
            )
            fila.append(van_s)
        matriz.append(fila)

    df_sens = pd.DataFrame(
        matriz,
        index=[f"{v:,.0f} und" for v in rango_volumenes],
        columns=[f"${p:,.1f}" for p in rango_precios]
    )

    fig_heat, ax_heat = plt.subplots(figsize=(11, 5))
    sns.heatmap(df_sens, annot=True, fmt=",.0f", cmap="RdYlGn",
                center=0, cbar_kws={"label": "VAN en USD"}, ax=ax_heat)
    ax_heat.set_title("Sensibilidad Cruzada del VAN ($)", fontsize=12,
                      fontweight="bold", color="#1F4E78")
    ax_heat.set_xlabel("Precio de Venta ($/unidad)", fontsize=10, fontweight="bold")
    ax_heat.set_ylabel("Volumen de Unidades Vendidas", fontsize=10, fontweight="bold")
    st.pyplot(fig_heat)
    plt.close(fig_heat)

else:
    st.markdown(
        "<h2 class='section-title'>II. Análisis Estadístico – Simulación de Incertidumbre (Monte Carlo)</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"Se modelan precio y volumen como **variables normales independientes** "
        f"con las volatilidades seleccionadas. Períodos evaluados: **{n_periodos} años**."
    )

    np.random.seed(42)
    precios_sim  = np.random.normal(precio_base,  precio_base  * vol_precio,  num_simulaciones)
    volumenes_sim = np.random.normal(volumen_base, volumen_base * vol_volumen, num_simulaciones)

    vans_sim = np.array([
        calcular_flujos(pr, vol, tax_rate, tasa_descuento, n_periodos,
                        inversion_inicial, dep_anual, cap_trabajo, salvamento,
                        costo_var, costo_fijo, tipo_cambio)[0]
        for pr, vol in zip(precios_sim, volumenes_sim)
    ])

    van_esperado = np.mean(vans_sim)
    sd_van       = np.std(vans_sim)
    cv_van       = sd_van / abs(van_esperado) if van_esperado != 0 else 0
    prob_exito   = np.mean(vans_sim > 0) * 100.0
    van_p5       = np.percentile(vans_sim, 5)
    van_p95      = np.percentile(vans_sim, 95)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class='metric-box'>
            <p style='margin:0;font-size:13px;color:#595959;'>VAN Esperado Promedio</p>
            <p class='metric-val'>${van_esperado:,.2f}</p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='metric-box' style='background-color:#FCE4D6;border-color:#F8CBAD;'>
            <p style='margin:0;font-size:13px;color:#595959;'>Desviación Estándar (σ)</p>
            <p class='metric-val' style='color:#C65911;'>${sd_van:,.2f}</p></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='metric-box' style='background-color:#FFF2CC;border-color:#FFE699;'>
            <p style='margin:0;font-size:13px;color:#595959;'>Coeficiente de Variación</p>
            <p class='metric-val' style='color:#7F6000;'>{cv_van:.4f}</p></div>""", unsafe_allow_html=True)
    with c4:
        cp = "#375623" if prob_exito >= 70 else ("#7F6000" if prob_exito >= 50 else "#C65911")
        bp = "#E2EFDA" if prob_exito >= 70 else ("#FFF2CC" if prob_exito >= 50 else "#FCE4D6")
        ep = "#C6E0B4" if prob_exito >= 70 else ("#FFE699" if prob_exito >= 50 else "#F8CBAD")
        st.markdown(f"""<div class='metric-box' style='background-color:{bp};border-color:{ep};'>
            <p style='margin:0;font-size:13px;color:#595959;'>Probabilidad VAN > 0</p>
            <p class='metric-val' style='color:{cp};'>{prob_exito:.2f}%</p></div>""", unsafe_allow_html=True)

    st.markdown(f"**Intervalo de confianza 90%:** ${van_p5:,.2f} ↔ ${van_p95:,.2f}")

    st.markdown("<h2 class='section-title'>Histograma de Distribución de Probabilidades del VAN</h2>",
                unsafe_allow_html=True)
    fig_hist, ax_hist = plt.subplots(figsize=(11, 5))
    counts, bins, patches = ax_hist.hist(vans_sim, bins=60, edgecolor="black", alpha=0.75)
    for patch, lb in zip(patches, bins[:-1]):
        patch.set_facecolor("#A9D08E" if lb >= 0 else "#F8CBAD")
    ax_hist.axvline(0, color="red", linestyle="--", linewidth=2,
                    label="Umbral de Rentabilidad (VAN = 0)")
    ax_hist.axvline(van_esperado, color="#2F5496", linestyle="-", linewidth=2.5,
                    label=f"VAN Esperado (${van_esperado:,.0f})")
    ax_hist.axvline(van_p5,  color="orange", linestyle=":", linewidth=1.5,
                    label=f"Percentil 5% (${van_p5:,.0f})")
    ax_hist.axvline(van_p95, color="green",  linestyle=":", linewidth=1.5,
                    label=f"Percentil 95% (${van_p95:,.0f})")
    ax_hist.set_title("Frecuencia de Resultados del VAN – Simulación Monte Carlo",
                      fontsize=12, fontweight="bold", color="#1F4E78")
    ax_hist.set_xlabel("Valor Actual Neto (USD)", fontsize=10, fontweight="bold")
    ax_hist.set_ylabel("Frecuencia (Ensayos)", fontsize=10, fontweight="bold")
    ax_hist.grid(True, linestyle=":", alpha=0.5)
    ax_hist.legend(loc="upper left", fontsize=9)
    st.pyplot(fig_hist)
    plt.close(fig_hist)

# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN III – ANÁLISIS DE SENSIBILIDAD: GRÁFICO DE TORNADO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<h2 class='section-title'>III. Análisis de Sensibilidad – Gráfico de Tornado</h2>",
    unsafe_allow_html=True
)
st.markdown(
    f"Impacto de cada variable clave sobre el VAN variando una a la vez (**OAT**) "
    f"en −{var_pesimista_pct:.0f}% / +{var_optimista_pct:.0f}% respecto al valor base. "
    f"**VAN Base de referencia: ${van_base:,.2f}**"
)

# Definición de variables y sus factores
variables_tornado = [
    {"nombre": "Precio de Venta",    "fp": 1 - var_precio_pes/100, "fo": 1 + var_precio_opt/100,
     "pp": var_precio_pes, "po": var_precio_opt},
    {"nombre": "Costo Variable",     "fp": 1 - var_cv_pes/100,     "fo": 1 + var_cv_opt/100,
     "pp": var_cv_pes,     "po": var_cv_opt},
    {"nombre": "Volumen de Ventas",  "fp": 1 - var_vol_pes/100,    "fo": 1 + var_vol_opt/100,
     "pp": var_vol_pes,    "po": var_vol_opt},
    {"nombre": "Costo Fijo",         "fp": 1 - var_cf_pes/100,     "fo": 1 + var_cf_opt/100,
     "pp": var_cf_pes,     "po": var_cf_opt},
    {"nombre": "Tasa de Descuento",  "fp": 1 - var_pesimista_pct/100, "fo": 1 + var_optimista_pct/100,
     "pp": var_pesimista_pct, "po": var_optimista_pct},
    {"nombre": "Inversión Inicial",  "fp": 1 - var_pesimista_pct/100, "fo": 1 + var_optimista_pct/100,
     "pp": var_pesimista_pct, "po": var_optimista_pct},
    {"nombre": "Valor de Salvamento","fp": 1 - var_pesimista_pct/100, "fo": 1 + var_optimista_pct/100,
     "pp": var_pesimista_pct, "po": var_optimista_pct},
]

# Calcular VAN pesimista / optimista para cada variable
resultados_tornado = []
for var in variables_tornado:
    vp, vo = calcular_van_tornado(
        var["nombre"], var["fp"], var["fo"],
        precio_base, volumen_base, tax_rate, tasa_descuento, n_periodos,
        inversion_inicial, dep_anual, cap_trabajo, salvamento,
        costo_var, costo_fijo, tipo_cambio
    )
    resultados_tornado.append({
        "Variable": var["nombre"],
        "VAN Pesimista": vp,
        "VAN Optimista": vo,
        "Rango": abs(vo - vp),
        "Var Pes %": var["pp"],
        "Var Opt %": var["po"],
    })

resultados_tornado.sort(key=lambda x: x["Rango"], reverse=True)

# ── Tabla de resultados ─────────────────────────────────────────────────────
df_tornado  = pd.DataFrame(resultados_tornado)
df_display  = df_tornado[["Variable", "VAN Pesimista", "VAN Optimista",
                           "Rango", "Var Pes %", "Var Opt %"]].copy()
df_display.index = range(1, len(df_display) + 1)

def color_van_cell(val):
    """Colorea celdas de VAN según signo. Compatible con map() y applymap()."""
    if isinstance(val, (int, float)):
        return "background-color: #E2EFDA" if val >= 0 else "background-color: #FCE4D6"
    return ""

# Compatibilidad pandas ≥ 2.1 (map) y < 2.1 (applymap)
styler = df_display.style.format({
    "VAN Pesimista": "${:,.2f}",
    "VAN Optimista": "${:,.2f}",
    "Rango":         "${:,.2f}",
    "Var Pes %":     "{:.0f}%",
    "Var Opt %":     "{:.0f}%",
}).background_gradient(subset=["Rango"], cmap="Blues")

try:
    styler = styler.map(color_van_cell, subset=["VAN Pesimista", "VAN Optimista"])
except AttributeError:
    styler = styler.applymap(color_van_cell, subset=["VAN Pesimista", "VAN Optimista"])

st.dataframe(styler, use_container_width=True)

# ── Gráfico de Tornado ──────────────────────────────────────────────────────
vars_plot    = [r["Variable"]      for r in reversed(resultados_tornado)]
van_pes_plot = [r["VAN Pesimista"] for r in reversed(resultados_tornado)]
van_opt_plot = [r["VAN Optimista"] for r in reversed(resultados_tornado)]

n_vars = len(vars_plot)
y_pos  = np.arange(n_vars)

COLOR_PES  = "#C00000"
COLOR_OPT  = "#1F4E78"
COLOR_BASE = "#FFD966"

fig_tornado, ax_tornado = plt.subplots(figsize=(12, max(5, n_vars * 0.9)))

for i, (pes, opt, _) in enumerate(zip(van_pes_plot, van_opt_plot, vars_plot)):
    width = abs(opt - pes)
    if pes < van_base:
        ax_tornado.barh(i, van_base - pes, left=pes, height=0.55,
                        color=COLOR_PES, alpha=0.85, zorder=3)
    if opt > van_base:
        ax_tornado.barh(i, opt - van_base, left=van_base, height=0.55,
                        color=COLOR_OPT, alpha=0.85, zorder=3)
    ax_tornado.text(pes - width * 0.01, i, f"${pes:,.0f}",
                    va="center", ha="right", fontsize=8, color=COLOR_PES, fontweight="bold")
    ax_tornado.text(opt + width * 0.01, i, f"${opt:,.0f}",
                    va="center", ha="left",  fontsize=8, color=COLOR_OPT, fontweight="bold")

ax_tornado.axvline(van_base, color=COLOR_BASE, linewidth=2.5, linestyle="--", zorder=4,
                   label=f"VAN Base: ${van_base:,.0f}")
ax_tornado.axvline(0, color="gray", linewidth=1.0, linestyle=":", zorder=2, label="VAN = 0")

ax_tornado.set_yticks(y_pos)
ax_tornado.set_yticklabels(vars_plot, fontsize=10, fontweight="bold")
ax_tornado.set_xlabel("Valor Actual Neto (USD)", fontsize=11, fontweight="bold")
ax_tornado.set_title(
    f"Gráfico de Tornado – Sensibilidad del VAN\n"
    f"(Variación −{var_pesimista_pct:.0f}% / +{var_optimista_pct:.0f}% | "
    f"{n_periodos} períodos | WACC: {tasa_descuento*100:.1f}%)",
    fontsize=13, fontweight="bold", color="#1F4E78", pad=15
)
ax_tornado.grid(True, axis="x", linestyle=":", alpha=0.5, zorder=1)

patch_pes  = mpatches.Patch(color=COLOR_PES,  alpha=0.85, label="Escenario Pesimista")
patch_opt  = mpatches.Patch(color=COLOR_OPT,  alpha=0.85, label="Escenario Optimista")
line_base  = plt.Line2D([0], [0], color=COLOR_BASE, linewidth=2.5,
                         linestyle="--", label=f"VAN Base: ${van_base:,.0f}")
ax_tornado.legend(handles=[patch_pes, patch_opt, line_base],
                  loc="lower right", fontsize=9, framealpha=0.9)
ax_tornado.spines["top"].set_visible(False)
ax_tornado.spines["right"].set_visible(False)
plt.tight_layout()
st.pyplot(fig_tornado)
plt.close(fig_tornado)

# ── Interpretación automática ───────────────────────────────────────────────
st.markdown("#### 📊 Interpretación del Tornado")
var_critica  = resultados_tornado[0]
var_menor    = resultados_tornado[-1]

ci1, ci2 = st.columns(2)
with ci1:
    st.info(
        f"🔴 **Variable más crítica:** {var_critica['Variable']}\n\n"
        f"Rango de impacto: **${var_critica['Rango']:,.2f}**\n\n"
        f"VAN Pesimista: ${var_critica['VAN Pesimista']:,.2f} | "
        f"VAN Optimista: ${var_critica['VAN Optimista']:,.2f}"
    )
with ci2:
    st.success(
        f"🟢 **Variable menos crítica:** {var_menor['Variable']}\n\n"
        f"Rango de impacto: **${var_menor['Rango']:,.2f}**\n\n"
        f"VAN Pesimista: ${var_menor['VAN Pesimista']:,.2f} | "
        f"VAN Optimista: ${var_menor['VAN Optimista']:,.2f}"
    )

jerarquia = " > ".join([r["Variable"] for r in resultados_tornado])
st.markdown(f"**Jerarquía de sensibilidad (mayor → menor impacto):**\n\n`{jerarquia}`")

# ─────────────────────────────────────────────────────────────────────────────
# PIE DE PÁGINA – GUÍA PEDAGÓGICA
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
### **Guía de Preguntas para Debatir en el Aula (Pedagogía FP&A):**
1. **La Variable Más Sensible:** Según el Tornado, ¿por qué **{resultados_tornado[0]['Variable']}**
   tiene el mayor impacto sobre el VAN? ¿Qué estrategias gerenciales pueden mitigar ese riesgo?
2. **La Interacción del Impuesto:** Si aumentas la Tasa Impositiva al 45%, ¿qué efecto tiene
   sobre el Coeficiente de Variación (CV) y la dispersión del VAN?
3. **Períodos de Evaluación:** Con **{n_periodos} períodos**, ¿cómo cambia el VAN si se extiende
   el horizonte? ¿Qué supuestos implica esa extensión?
4. **La Utilidad de las Opciones Reales:** En escenarios donde la probabilidad de éxito
   (VAN > 0) cae por debajo del 50%, ¿cómo puede la administración utilizar la
   *Opción Real de Abandono* o la *Opción de Esperar* para salvar el capital inicial?
5. **Limitación del OAT:** El análisis Tornado varía una variable a la vez, ignorando
   correlaciones. ¿Cómo complementaría este análisis con la Simulación de Monte Carlo?
""")