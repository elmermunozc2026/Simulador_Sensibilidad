import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import io

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Simulador de Sensibilidad e Incertidumbre FP&A",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# DICCIONARIO DE TEXTOS (ES / EN)
# ─────────────────────────────────────────────────────────────────────────────
TEXTS = {
    "es": {
        "page_title":        "Simulador Interactivo de Sensibilidad e Incertidumbre (VAN)",
        "subtitle":          "### **Módulo 6: Evaluación Financiera de Inversiones y Proyectos**\nEste modelo interactivo permite analizar de forma **simultánea y dinámica** cómo interactúan el **Precio de Venta**, el **Volumen de Ventas**, los **Costos** y la **Tasa Impositiva Corporativa** en la determinación del **Valor Actual Neto (VAN)** esperado de un proyecto de inversión.",
        "lang_label":        "🌐 Idioma / Language",
        # Sidebar sección 1
        "s1_header":         "1. Parámetros Base del Proyecto",
        "n_periodos":        "Número de Períodos (años)",
        "precio_base":       "Precio de Venta Base ($/unidad)",
        "costo_var":         "Costo Variable Unitario ($/unidad)",
        "volumen_base":      "Volumen de Ventas Base (unidades/año)",
        "costo_fijo":        "Costo Fijo Anual ($)",
        "tax_rate":          "Tasa Impositiva Corporativa (%)",
        "wacc":              "Tasa de Descuento / WACC (%)",
        "tipo_cambio":       "Tipo de Cambio (moneda local / USD)",
        "inversion":         "Inversión Inicial ($)",
        "cap_trabajo":       "Capital de Trabajo (% de Inversión)",
        "salvamento":        "Valor de Salvamento (% de Inversión)",
        "dep_caption":       "📌 Depreciación lineal automática: **${dep:,.0f}/año** ({n} períodos)",
        "ct_caption":        "📌 Capital de trabajo: **${ct:,.0f}** ({pct:.0f}% de ${inv:,.0f})",
        "sv_caption":        "📌 Valor de salvamento: **${sv:,.0f}** ({pct:.0f}% de ${inv:,.0f})",
        # Sidebar sección 2
        "s2_header":         "2. Simulación de Incertidumbre",
        "mc_check":          "Activar Simulación de Monte Carlo",
        "vol_precio":        "Volatilidad del Precio (%)",
        "vol_volumen":       "Volatilidad del Volumen (%)",
        "num_iter":          "Número de Iteraciones",
        # Sidebar sección 3
        "s3_header":         "3. Análisis de Tornado",
        "var_escenarios":    "**Variación para escenarios (%):**",
        "var_pes":           "Variación Pesimista (%)",
        "var_opt":           "Variación Optimista (%)",
        "ajuste_fino":       "**Ajuste fino por variable:**",
        "precio_pes":        "Precio – Var. Pesimista (%)",
        "precio_opt":        "Precio – Var. Optimista (%)",
        "cv_pes":            "Costo Variable – Var. Pesimista (%)",
        "cv_opt":            "Costo Variable – Var. Optimista (%)",
        "vol_pes":           "Volumen – Var. Pesimista (%)",
        "vol_opt":           "Volumen – Var. Optimista (%)",
        "cf_pes":            "Costo Fijo – Var. Pesimista (%)",
        "cf_opt":            "Costo Fijo – Var. Optimista (%)",
        # Sección I
        "s1_title":          "I. Proyección del Flujo de Caja Base",
        "year":              "Año",
        "concepts": [
            "Ingresos por Ventas", "Costos Variables", "Costos Fijos Operativos",
            "Depreciación", "Utilidad Operativa (EBIT)", "Impuesto a la Renta",
            "Utilidad Neta Operativa (NOPAT)", "Ajuste Depreciación (+)",
            "Flujo de Inversión Inicial", "Valor de Salvamento Neto",
            "Recuperación Capital Trabajo", "Flujo de Caja Neto (FCN)"
        ],
        "van_label":         "Valor Actual Neto (VAN) Base",
        "van_sub":           "Tasa de Descuento: {k:.1f}% | Períodos: {n} años",
        "tir_label":         "Tasa Interna de Retorno (TIR)",
        "tir_sub":           "Rentabilidad promedio anual del proyecto",
        "accept":            "✅ ACEPTAR (VAN > 0)",
        "reject":            "❌ RECHAZAR (VAN < 0)",
        "tir_ok":            "✅ TIR > WACC ({k:.1f}%)",
        "tir_ko":            "❌ TIR < WACC ({k:.1f}%)",
        # Sección II determinística
        "s2_title_det":      "II. Análisis de Sensibilidad Cruzada (Precio vs. Volumen)",
        "s2_desc_det":       "Tabla bidimensional del **VAN** para combinaciones de precio y volumen (tasa impositiva fija: **{tax:.0f}%**, períodos: **{n} años**).",
        "heat_title":        "Sensibilidad Cruzada del VAN ($)",
        "heat_xlabel":       "Precio de Venta ($/unidad)",
        "heat_ylabel":       "Volumen de Unidades Vendidas",
        "heat_cbar":         "VAN en USD",
        # Sección II Monte Carlo
        "s2_title_mc":       "II. Análisis Estadístico – Simulación de Incertidumbre (Monte Carlo)",
        "s2_desc_mc":        "Se modelan precio y volumen como **variables normales independientes** con las volatilidades seleccionadas. Períodos evaluados: **{n} años**.",
        "van_esp":           "VAN Esperado Promedio",
        "std_label":         "Desviación Estándar (σ)",
        "cv_label":          "Coeficiente de Variación",
        "prob_label":        "Probabilidad VAN > 0",
        "ci_label":          "**Intervalo de confianza 90%:** ${p5:,.2f} ↔ ${p95:,.2f}",
        "hist_title":        "Frecuencia de Resultados del VAN – Simulación Monte Carlo",
        "hist_xlabel":       "Valor Actual Neto (USD)",
        "hist_ylabel":       "Frecuencia (Ensayos)",
        "hist_l0":           "Umbral de Rentabilidad (VAN = 0)",
        "hist_lm":           "VAN Esperado (${v:,.0f})",
        "hist_l5":           "Percentil 5% (${v:,.0f})",
        "hist_l95":          "Percentil 95% (${v:,.0f})",
        # Sección III Tornado
        "s3_title":          "III. Análisis de Sensibilidad – Gráfico de Tornado",
        "s3_desc":           "Impacto de cada variable clave sobre el VAN variando una a la vez (**OAT**) en −{pp:.0f}% / +{po:.0f}% respecto al valor base. **VAN Base de referencia: ${vb:,.2f}**",
        "col_var":           "Variable",
        "col_pes":           "VAN Pesimista",
        "col_opt":           "VAN Optimista",
        "col_rng":           "Rango",
        "col_pp":            "Var Pes %",
        "col_po":            "Var Opt %",
        "tornado_title":     "Gráfico de Tornado – Sensibilidad del VAN\n(Variación −{pp:.0f}% / +{po:.0f}% | {n} períodos | WACC: {k:.1f}%)",
        "tornado_xlabel":    "Valor Actual Neto (USD)",
        "leg_pes":           "Escenario Pesimista",
        "leg_opt":           "Escenario Optimista",
        "leg_base":          "VAN Base: ${v:,.0f}",
        "van_zero":          "VAN = 0",
        "interp_title":      "#### 📊 Interpretación del Tornado",
        "most_critical":     "🔴 **Variable más crítica:** {v}\n\nRango de impacto: **${r:,.2f}**\n\nVAN Pesimista: ${p:,.2f} | VAN Optimista: ${o:,.2f}",
        "least_critical":    "🟢 **Variable menos crítica:** {v}\n\nRango de impacto: **${r:,.2f}**\n\nVAN Pesimista: ${p:,.2f} | VAN Optimista: ${o:,.2f}",
        "hierarchy":         "**Jerarquía de sensibilidad (mayor → menor impacto):**\n\n`{h}`",
        # Descargas
        "dl_header":         "📥 Descargar Informes",
        "dl_excel":          "⬇️ Descargar Excel",
        "dl_excel_help":     "Descarga tabla de flujos y resultados del tornado en Excel",
        "dl_csv":            "⬇️ Descargar CSV (Tornado)",
        "dl_csv_help":       "Descarga la tabla de sensibilidad tornado en CSV",
        # Pie
        "footer": """### **Guía de Preguntas para Debatir en el Aula (Pedagogía FP&A):**
1. **La Variable Más Sensible:** Según el Tornado, ¿por qué **{v}** tiene el mayor impacto sobre el VAN? ¿Qué estrategias gerenciales pueden mitigar ese riesgo?
2. **La Interacción del Impuesto:** Si aumentas la Tasa Impositiva al 45%, ¿qué efecto tiene sobre el Coeficiente de Variación (CV) y la dispersión del VAN?
3. **Períodos de Evaluación:** Con **{n} períodos**, ¿cómo cambia el VAN si se extiende el horizonte?
4. **Opciones Reales:** En escenarios donde la probabilidad de éxito (VAN > 0) cae por debajo del 50%, ¿cómo puede la administración utilizar la *Opción Real de Abandono* o la *Opción de Esperar*?
5. **Limitación del OAT:** El análisis Tornado varía una variable a la vez, ignorando correlaciones. ¿Cómo complementaría este análisis con Monte Carlo?""",
        # Variable names for tornado
        "var_names": ["Precio de Venta", "Costo Variable", "Volumen de Ventas",
                      "Costo Fijo", "Tasa de Descuento", "Inversión Inicial", "Valor de Salvamento"],
    },
    "en": {
        "page_title":        "Interactive Sensitivity & Uncertainty Simulator (NPV)",
        "subtitle":          "### **Module 6: Financial Evaluation of Investments and Projects**\nThis interactive model allows **simultaneous and dynamic** analysis of how **Selling Price**, **Sales Volume**, **Costs** and **Corporate Tax Rate** interact in determining the expected **Net Present Value (NPV)** of an investment project.",
        "lang_label":        "🌐 Idioma / Language",
        # Sidebar section 1
        "s1_header":         "1. Base Project Parameters",
        "n_periodos":        "Number of Periods (years)",
        "precio_base":       "Base Selling Price ($/unit)",
        "costo_var":         "Unit Variable Cost ($/unit)",
        "volumen_base":      "Base Sales Volume (units/year)",
        "costo_fijo":        "Annual Fixed Cost ($)",
        "tax_rate":          "Corporate Tax Rate (%)",
        "wacc":              "Discount Rate / WACC (%)",
        "tipo_cambio":       "Exchange Rate (local currency / USD)",
        "inversion":         "Initial Investment ($)",
        "cap_trabajo":       "Working Capital (% of Investment)",
        "salvamento":        "Salvage Value (% of Investment)",
        "dep_caption":       "📌 Straight-line depreciation: **${dep:,.0f}/yr** ({n} periods)",
        "ct_caption":        "📌 Working capital: **${ct:,.0f}** ({pct:.0f}% of ${inv:,.0f})",
        "sv_caption":        "📌 Salvage value: **${sv:,.0f}** ({pct:.0f}% of ${inv:,.0f})",
        # Sidebar section 2
        "s2_header":         "2. Uncertainty Simulation",
        "mc_check":          "Activate Monte Carlo Simulation",
        "vol_precio":        "Price Volatility (%)",
        "vol_volumen":       "Volume Volatility (%)",
        "num_iter":          "Number of Iterations",
        # Sidebar section 3
        "s3_header":         "3. Tornado Analysis",
        "var_escenarios":    "**Scenario variation (%):**",
        "var_pes":           "Pessimistic Variation (%)",
        "var_opt":           "Optimistic Variation (%)",
        "ajuste_fino":       "**Fine-tune by variable:**",
        "precio_pes":        "Price – Pessimistic Var. (%)",
        "precio_opt":        "Price – Optimistic Var. (%)",
        "cv_pes":            "Variable Cost – Pessimistic Var. (%)",
        "cv_opt":            "Variable Cost – Optimistic Var. (%)",
        "vol_pes":           "Volume – Pessimistic Var. (%)",
        "vol_opt":           "Volume – Optimistic Var. (%)",
        "cf_pes":            "Fixed Cost – Pessimistic Var. (%)",
        "cf_opt":            "Fixed Cost – Optimistic Var. (%)",
        # Section I
        "s1_title":          "I. Base Cash Flow Projection",
        "year":              "Year",
        "concepts": [
            "Sales Revenue", "Variable Costs", "Fixed Operating Costs",
            "Depreciation", "Operating Income (EBIT)", "Income Tax",
            "Net Operating Profit (NOPAT)", "Depreciation Add-back (+)",
            "Initial Investment Outflow", "Net Salvage Value",
            "Working Capital Recovery", "Net Cash Flow (NCF)"
        ],
        "van_label":         "Base Net Present Value (NPV)",
        "van_sub":           "Discount Rate: {k:.1f}% | Periods: {n} years",
        "tir_label":         "Internal Rate of Return (IRR)",
        "tir_sub":           "Average annual return of the project",
        "accept":            "✅ ACCEPT (NPV > 0)",
        "reject":            "❌ REJECT (NPV < 0)",
        "tir_ok":            "✅ IRR > WACC ({k:.1f}%)",
        "tir_ko":            "❌ IRR < WACC ({k:.1f}%)",
        # Section II deterministic
        "s2_title_det":      "II. Cross Sensitivity Analysis (Price vs. Volume)",
        "s2_desc_det":       "Two-dimensional **NPV** table for price and volume combinations (fixed tax rate: **{tax:.0f}%**, periods: **{n} years**).",
        "heat_title":        "Cross NPV Sensitivity ($)",
        "heat_xlabel":       "Selling Price ($/unit)",
        "heat_ylabel":       "Sales Volume (units)",
        "heat_cbar":         "NPV in USD",
        # Section II Monte Carlo
        "s2_title_mc":       "II. Statistical Analysis – Uncertainty Simulation (Monte Carlo)",
        "s2_desc_mc":        "Price and volume are modeled as **independent normal variables** with the selected volatilities. Evaluated periods: **{n} years**.",
        "van_esp":           "Expected NPV (Mean)",
        "std_label":         "Standard Deviation (σ)",
        "cv_label":          "Coefficient of Variation",
        "prob_label":        "Probability NPV > 0",
        "ci_label":          "**90% Confidence Interval:** ${p5:,.2f} ↔ ${p95:,.2f}",
        "hist_title":        "NPV Distribution – Monte Carlo Simulation",
        "hist_xlabel":       "Net Present Value (USD)",
        "hist_ylabel":       "Frequency (Trials)",
        "hist_l0":           "Break-even Threshold (NPV = 0)",
        "hist_lm":           "Expected NPV (${v:,.0f})",
        "hist_l5":           "5th Percentile (${v:,.0f})",
        "hist_l95":          "95th Percentile (${v:,.0f})",
        # Section III Tornado
        "s3_title":          "III. Sensitivity Analysis – Tornado Chart",
        "s3_desc":           "Impact of each key variable on NPV varying one at a time (**OAT**) by −{pp:.0f}% / +{po:.0f}% from base values. **Base NPV reference: ${vb:,.2f}**",
        "col_var":           "Variable",
        "col_pes":           "Pessimistic NPV",
        "col_opt":           "Optimistic NPV",
        "col_rng":           "Range",
        "col_pp":            "Pes Var %",
        "col_po":            "Opt Var %",
        "tornado_title":     "Tornado Chart – NPV Sensitivity\n(Variation −{pp:.0f}% / +{po:.0f}% | {n} periods | WACC: {k:.1f}%)",
        "tornado_xlabel":    "Net Present Value (USD)",
        "leg_pes":           "Pessimistic Scenario",
        "leg_opt":           "Optimistic Scenario",
        "leg_base":          "Base NPV: ${v:,.0f}",
        "van_zero":          "NPV = 0",
        "interp_title":      "#### 📊 Tornado Interpretation",
        "most_critical":     "🔴 **Most critical variable:** {v}\n\nImpact range: **${r:,.2f}**\n\nPessimistic NPV: ${p:,.2f} | Optimistic NPV: ${o:,.2f}",
        "least_critical":    "🟢 **Least critical variable:** {v}\n\nImpact range: **${r:,.2f}**\n\nPessimistic NPV: ${p:,.2f} | Optimistic NPV: ${o:,.2f}",
        "hierarchy":         "**Sensitivity hierarchy (highest → lowest impact):**\n\n`{h}`",
        # Downloads
        "dl_header":         "📥 Download Reports",
        "dl_excel":          "⬇️ Download Excel",
        "dl_excel_help":     "Download cash flow table and tornado results as Excel",
        "dl_csv":            "⬇️ Download CSV (Tornado)",
        "dl_csv_help":       "Download tornado sensitivity table as CSV",
        # Footer
        "footer": """### **Discussion Questions for the Classroom (FP&A Pedagogy):**
1. **Most Sensitive Variable:** According to the Tornado, why does **{v}** have the greatest impact on NPV? What management strategies can mitigate that risk?
2. **Tax Interaction:** If you increase the Tax Rate to 45%, what effect does it have on the Coefficient of Variation (CV) and NPV dispersion?
3. **Evaluation Periods:** With **{n} periods**, how does NPV change if the horizon is extended?
4. **Real Options:** In scenarios where the probability of success (NPV > 0) falls below 50%, how can management use the *Abandonment Option* or *Option to Wait*?
5. **OAT Limitation:** The Tornado analysis varies one variable at a time, ignoring correlations. How would you complement this with Monte Carlo simulation?""",
        # Variable names for tornado
        "var_names": ["Selling Price", "Variable Cost", "Sales Volume",
                      "Fixed Cost", "Discount Rate", "Initial Investment", "Salvage Value"],
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# ESTILOS CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .reportview-container { background-color: #F8F9FA; }
    .main-title {
        color: #1F4E78; font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: bold; text-align: center; margin-bottom: 20px;
    }
    .section-title {
        color: #2F5496; font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: bold; border-bottom: 2px solid #2F5496;
        padding-bottom: 5px; margin-top: 30px; margin-bottom: 15px;
    }
    .metric-box {
        background-color: #E2EFDA; padding: 15px; border-radius: 8px;
        border: 1px solid #C6E0B4; text-align: center;
    }
    .metric-val { font-size: 24px; font-weight: bold; color: #375623; }
    div[data-testid="stSidebar"] .stNumberInput label { font-size: 11px !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SELECTOR DE IDIOMA (top of sidebar)
# ─────────────────────────────────────────────────────────────────────────────
lang_choice = st.sidebar.selectbox(
    "🌐 Idioma / Language",
    options=["Español", "English"],
    index=0,
    key="lang_select"
)
T = TEXTS["es"] if lang_choice == "Español" else TEXTS["en"]

# ─────────────────────────────────────────────────────────────────────────────
# HELPER: SINCRONIZACIÓN SLIDER ↔ NUMBER_INPUT (sidebar)
# ─────────────────────────────────────────────────────────────────────────────
def synced_sidebar(label, key, min_val, max_val, default, step,
                   fmt="%.2f", help_text="", is_int=False):
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
                          key=key_sld, on_change=on_sld, label_visibility="collapsed")
    else:
        st.sidebar.number_input(label, min_value=float(min_val), max_value=float(max_val),
                                value=float(cur), step=float(step), format=fmt,
                                key=key_num, on_change=on_num, help=help_text)
        st.sidebar.slider("", min_value=float(min_val), max_value=float(max_val),
                          value=float(st.session_state[key]), step=float(step),
                          key=key_sld, on_change=on_sld, label_visibility="collapsed")
    return st.session_state[key]

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR – SECCIÓN 1: PARÁMETROS BASE
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.header(T["s1_header"])

n_periodos = int(synced_sidebar(T["n_periodos"], "n_periodos", 1, 20, 5, 1, "%d",
                                 is_int=True))
st.sidebar.markdown("---")
precio_base   = synced_sidebar(T["precio_base"],  "precio_base",  50.0, 500.0,   200.0,  5.0,  "%.1f")
costo_var     = synced_sidebar(T["costo_var"],    "costo_var",    10.0, 400.0,    80.0,  5.0,  "%.1f")
volumen_base  = int(synced_sidebar(T["volumen_base"], "volumen_base", 100, 5000, 1000, 50, "%d", is_int=True))
costo_fijo    = synced_sidebar(T["costo_fijo"],   "costo_fijo",    0.0, 500000.0, 50000.0, 5000.0, "%.0f")
st.sidebar.markdown("---")
tax_rate_pct  = synced_sidebar(T["tax_rate"],     "tax_rate_pct",  0.0,  60.0,   35.0,  1.0,  "%.1f")
tax_rate      = tax_rate_pct / 100.0
tasa_desc_pct = synced_sidebar(T["wacc"],         "tasa_desc_pct", 1.0,  40.0,   12.0,  0.5,  "%.1f")
tasa_descuento = tasa_desc_pct / 100.0
st.sidebar.markdown("---")
tipo_cambio       = synced_sidebar(T["tipo_cambio"],  "tipo_cambio",      0.5, 20.0,      1.0,  0.05, "%.2f")
inversion_inicial = synced_sidebar(T["inversion"],    "inversion_inicial",10000.0, 5000000.0, 300000.0, 10000.0, "%.0f")
cap_trabajo_pct   = synced_sidebar(T["cap_trabajo"],  "cap_trabajo_pct",  0.0,  50.0,   18.0,  1.0,  "%.1f")
cap_trabajo       = inversion_inicial * cap_trabajo_pct / 100.0
salvamento_pct    = synced_sidebar(T["salvamento"],   "salvamento_pct",   0.0, 100.0,   40.0,  5.0,  "%.1f")
salvamento        = inversion_inicial * salvamento_pct / 100.0
dep_anual         = inversion_inicial / n_periodos if n_periodos > 0 else 0.0

st.sidebar.markdown("---")
st.sidebar.caption(T["dep_caption"].format(dep=dep_anual, n=n_periodos))
st.sidebar.caption(T["ct_caption"].format(ct=cap_trabajo, pct=cap_trabajo_pct, inv=inversion_inicial))
st.sidebar.caption(T["sv_caption"].format(sv=salvamento, pct=salvamento_pct, inv=inversion_inicial))

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR – SECCIÓN 2: SIMULACIÓN
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.header(T["s2_header"])
activar_simulacion = st.sidebar.checkbox(T["mc_check"], value=False)

vol_precio = 0.10
vol_volumen = 0.15
num_simulaciones = 5000

if activar_simulacion:
    vol_precio  = synced_sidebar(T["vol_precio"],  "vol_precio",  1.0, 50.0, 10.0, 1.0, "%.1f") / 100.0
    vol_volumen = synced_sidebar(T["vol_volumen"], "vol_volumen", 1.0, 50.0, 15.0, 1.0, "%.1f") / 100.0
    num_simulaciones = int(synced_sidebar(T["num_iter"], "num_simulaciones", 500, 20000, 5000, 500, "%d", is_int=True))

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR – SECCIÓN 3: TORNADO
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.header(T["s3_header"])
st.sidebar.markdown(T["var_escenarios"])

var_pesimista_pct = synced_sidebar(T["var_pes"], "var_pesimista_pct", 5.0, 50.0, 20.0, 5.0, "%.0f")
var_optimista_pct = synced_sidebar(T["var_opt"], "var_optimista_pct", 5.0, 50.0, 20.0, 5.0, "%.0f")

st.sidebar.markdown(T["ajuste_fino"])
var_precio_pes = st.sidebar.number_input(T["precio_pes"], 1.0, 80.0, float(var_pesimista_pct), 1.0, key="vp_pes")
var_precio_opt = st.sidebar.number_input(T["precio_opt"], 1.0, 80.0, float(var_optimista_pct), 1.0, key="vp_opt")
var_cv_pes     = st.sidebar.number_input(T["cv_pes"],     1.0, 80.0, float(var_pesimista_pct), 1.0, key="vcv_pes")
var_cv_opt     = st.sidebar.number_input(T["cv_opt"],     1.0, 80.0, float(var_optimista_pct), 1.0, key="vcv_opt")
var_vol_pes    = st.sidebar.number_input(T["vol_pes"],    1.0, 80.0, float(var_pesimista_pct), 1.0, key="vvol_pes")
var_vol_opt    = st.sidebar.number_input(T["vol_opt"],    1.0, 80.0, float(var_optimista_pct), 1.0, key="vvol_opt")
var_cf_pes     = st.sidebar.number_input(T["cf_pes"],     1.0, 80.0, float(var_pesimista_pct), 1.0, key="vcf_pes")
var_cf_opt     = st.sidebar.number_input(T["cf_opt"],     1.0, 80.0, float(var_optimista_pct), 1.0, key="vcf_opt")

# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES DE CÁLCULO
# ─────────────────────────────────────────────────────────────────────────────
def calcular_flujos(precio, volumen, tax, k, n, I0, dep, cap_trab, salv, cv, cf, tc):
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


def calcular_van_tornado(nombre_var, factor_pes, factor_opt,
                          precio, volumen, tax, k, n, I0, dep,
                          cap_trab, salv, cv, cf, tc):
    base = dict(precio=precio, volumen=volumen, tax=tax, k=k, n=n,
                I0=I0, dep=dep, cap_trab=cap_trab, salv=salv, cv=cv, cf=cf, tc=tc)
    def van_con(**ov):
        p = {**base, **ov}
        v, _, _ = calcular_flujos(p["precio"], p["volumen"], p["tax"], p["k"],
                                   p["n"], p["I0"], p["dep"], p["cap_trab"],
                                   p["salv"], p["cv"], p["cf"], p["tc"])
        return v
    # Usar nombres internos en inglés para lógica (independiente del idioma)
    vn = nombre_var
    if vn in ("Precio de Venta", "Selling Price"):
        return van_con(precio=precio * factor_pes), van_con(precio=precio * factor_opt)
    elif vn in ("Costo Variable", "Variable Cost"):
        return van_con(cv=cv * factor_opt), van_con(cv=cv * factor_pes)
    elif vn in ("Volumen de Ventas", "Sales Volume"):
        return van_con(volumen=volumen * factor_pes), van_con(volumen=volumen * factor_opt)
    elif vn in ("Costo Fijo", "Fixed Cost"):
        return van_con(cf=cf * factor_opt), van_con(cf=cf * factor_pes)
    elif vn in ("Tasa de Descuento", "Discount Rate"):
        return van_con(k=k * factor_opt), van_con(k=k * factor_pes)
    elif vn in ("Inversión Inicial", "Initial Investment"):
        return van_con(I0=I0 * factor_opt), van_con(I0=I0 * factor_pes)
    elif vn in ("Valor de Salvamento", "Salvage Value"):
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
# TÍTULO PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"<h1 class='main-title'>{T['page_title']}</h1>", unsafe_allow_html=True)
st.markdown(T["subtitle"])

# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN I – FLUJO DE CAJA BASE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"<h2 class='section-title'>{T['s1_title']}</h2>", unsafe_allow_html=True)

columnas_años = [f"{T['year']} 0"] + [f"{T['year']} {t}" for t in range(1, n_periodos + 1)]
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
    valores_tabla.append([v, -cv_t, -costo_fijo, -dep_anual, ebit, -imp, nop,
                           dep_anual, 0.0, salv_neto_t, cap_rec_t, fcn_t])

df_flujos = pd.DataFrame(np.array(valores_tabla).T,
                          index=T["concepts"], columns=columnas_años)
st.dataframe(
    df_flujos.style.format("${:,.2f}")
    .highlight_min(axis=1, color="#FFD9CC")
    .highlight_max(axis=1, color="#E2EFDA"),
    use_container_width=True
)

col1, col2 = st.columns(2)
with col1:
    cv  = "#375623" if van_base >= 0 else "#C65911"
    bv  = "#E2EFDA" if van_base >= 0 else "#FCE4D6"
    ev  = "#C6E0B4" if van_base >= 0 else "#F8CBAD"
    dec = T["accept"] if van_base >= 0 else T["reject"]
    st.markdown(f"""<div class='metric-box' style='background-color:{bv};border-color:{ev};'>
        <p style='margin:0;font-size:16px;color:#595959;'>{T['van_label']}</p>
        <p class='metric-val' style='color:{cv};'>${van_base:,.2f}</p>
        <p style='margin:0;font-size:12px;color:#595959;'>{T['van_sub'].format(k=tasa_descuento*100, n=n_periodos)}</p>
        <p style='margin:0;font-size:13px;font-weight:bold;color:{cv};'>{dec}</p>
    </div>""", unsafe_allow_html=True)
with col2:
    ct  = "#1F4E78" if tir_val >= tasa_descuento else "#C65911"
    bt  = "#D9E1F2" if tir_val >= tasa_descuento else "#FCE4D6"
    et  = "#8FAADC" if tir_val >= tasa_descuento else "#F8CBAD"
    tdc = T["tir_ok"].format(k=tasa_descuento*100) if tir_val >= tasa_descuento \
          else T["tir_ko"].format(k=tasa_descuento*100)
    st.markdown(f"""<div class='metric-box' style='background-color:{bt};border-color:{et};'>
        <p style='margin:0;font-size:16px;color:#595959;'>{T['tir_label']}</p>
        <p class='metric-val' style='color:{ct};'>{tir_val*100:.2f}%</p>
        <p style='margin:0;font-size:12px;color:#595959;'>{T['tir_sub']}</p>
        <p style='margin:0;font-size:13px;font-weight:bold;color:{ct};'>{tdc}</p>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN II – SENSIBILIDAD / MONTE CARLO
# ─────────────────────────────────────────────────────────────────────────────
if not activar_simulacion:
    st.markdown(f"<h2 class='section-title'>{T['s2_title_det']}</h2>", unsafe_allow_html=True)
    st.markdown(T["s2_desc_det"].format(tax=tax_rate*100, n=n_periodos))

    rango_precios   = np.linspace(precio_base * 0.8, precio_base * 1.2, 7)
    rango_volumenes = np.linspace(volumen_base * 0.8, volumen_base * 1.2, 7)
    matriz = []
    for vol in rango_volumenes:
        fila = []
        for pr in rango_precios:
            van_s, _, _ = calcular_flujos(pr, vol, tax_rate, tasa_descuento, n_periodos,
                                           inversion_inicial, dep_anual, cap_trabajo,
                                           salvamento, costo_var, costo_fijo, tipo_cambio)
            fila.append(van_s)
        matriz.append(fila)

    df_sens = pd.DataFrame(matriz,
                            index=[f"{v:,.0f} u" for v in rango_volumenes],
                            columns=[f"${p:,.1f}" for p in rango_precios])
    fig_heat, ax_heat = plt.subplots(figsize=(11, 5))
    sns.heatmap(df_sens, annot=True, fmt=",.0f", cmap="RdYlGn",
                center=0, cbar_kws={"label": T["heat_cbar"]}, ax=ax_heat)
    ax_heat.set_title(T["heat_title"], fontsize=12, fontweight="bold", color="#1F4E78")
    ax_heat.set_xlabel(T["heat_xlabel"], fontsize=10, fontweight="bold")
    ax_heat.set_ylabel(T["heat_ylabel"], fontsize=10, fontweight="bold")
    st.pyplot(fig_heat)
    plt.close(fig_heat)

else:
    st.markdown(f"<h2 class='section-title'>{T['s2_title_mc']}</h2>", unsafe_allow_html=True)
    st.markdown(T["s2_desc_mc"].format(n=n_periodos))

    np.random.seed(42)
    precios_sim   = np.random.normal(precio_base,  precio_base  * vol_precio,  num_simulaciones)
    volumenes_sim = np.random.normal(volumen_base, volumen_base * vol_volumen, num_simulaciones)
    vans_sim = np.array([
        calcular_flujos(pr, vol, tax_rate, tasa_descuento, n_periodos,
                        inversion_inicial, dep_anual, cap_trabajo, salvamento,
                        costo_var, costo_fijo, tipo_cambio)[0]
        for pr, vol in zip(precios_sim, volumenes_sim)
    ])
    van_esp  = np.mean(vans_sim)
    sd_van   = np.std(vans_sim)
    cv_van   = sd_van / abs(van_esp) if van_esp != 0 else 0
    prob_ok  = np.mean(vans_sim > 0) * 100.0
    van_p5   = np.percentile(vans_sim, 5)
    van_p95  = np.percentile(vans_sim, 95)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class='metric-box'><p style='margin:0;font-size:13px;color:#595959;'>{T['van_esp']}</p>
            <p class='metric-val'>${van_esp:,.2f}</p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='metric-box' style='background-color:#FCE4D6;border-color:#F8CBAD;'>
            <p style='margin:0;font-size:13px;color:#595959;'>{T['std_label']}</p>
            <p class='metric-val' style='color:#C65911;'>${sd_van:,.2f}</p></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='metric-box' style='background-color:#FFF2CC;border-color:#FFE699;'>
            <p style='margin:0;font-size:13px;color:#595959;'>{T['cv_label']}</p>
            <p class='metric-val' style='color:#7F6000;'>{cv_van:.4f}</p></div>""", unsafe_allow_html=True)
    with c4:
        cp = "#375623" if prob_ok >= 70 else ("#7F6000" if prob_ok >= 50 else "#C65911")
        bp = "#E2EFDA" if prob_ok >= 70 else ("#FFF2CC" if prob_ok >= 50 else "#FCE4D6")
        ep = "#C6E0B4" if prob_ok >= 70 else ("#FFE699" if prob_ok >= 50 else "#F8CBAD")
        st.markdown(f"""<div class='metric-box' style='background-color:{bp};border-color:{ep};'>
            <p style='margin:0;font-size:13px;color:#595959;'>{T['prob_label']}</p>
            <p class='metric-val' style='color:{cp};'>{prob_ok:.2f}%</p></div>""", unsafe_allow_html=True)

    st.markdown(T["ci_label"].format(p5=van_p5, p95=van_p95))

    fig_hist, ax_hist = plt.subplots(figsize=(11, 5))
    counts, bins, patches = ax_hist.hist(vans_sim, bins=60, edgecolor="black", alpha=0.75)
    for patch, lb in zip(patches, bins[:-1]):
        patch.set_facecolor("#A9D08E" if lb >= 0 else "#F8CBAD")
    ax_hist.axvline(0,       color="red",     linestyle="--", linewidth=2,   label=T["hist_l0"])
    ax_hist.axvline(van_esp, color="#2F5496", linestyle="-",  linewidth=2.5, label=T["hist_lm"].format(v=van_esp))
    ax_hist.axvline(van_p5,  color="orange",  linestyle=":",  linewidth=1.5, label=T["hist_l5"].format(v=van_p5))
    ax_hist.axvline(van_p95, color="green",   linestyle=":",  linewidth=1.5, label=T["hist_l95"].format(v=van_p95))
    ax_hist.set_title(T["hist_title"], fontsize=12, fontweight="bold", color="#1F4E78")
    ax_hist.set_xlabel(T["hist_xlabel"], fontsize=10, fontweight="bold")
    ax_hist.set_ylabel(T["hist_ylabel"], fontsize=10, fontweight="bold")
    ax_hist.grid(True, linestyle=":", alpha=0.5)
    ax_hist.legend(loc="upper left", fontsize=9)
    st.pyplot(fig_hist)
    plt.close(fig_hist)

# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN III – GRÁFICO DE TORNADO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"<h2 class='section-title'>{T['s3_title']}</h2>", unsafe_allow_html=True)
st.markdown(T["s3_desc"].format(pp=var_pesimista_pct, po=var_optimista_pct, vb=van_base))

var_names = T["var_names"]
variables_tornado = [
    {"nombre": var_names[0], "fp": 1-var_precio_pes/100, "fo": 1+var_precio_opt/100, "pp": var_precio_pes, "po": var_precio_opt},
    {"nombre": var_names[1], "fp": 1-var_cv_pes/100,     "fo": 1+var_cv_opt/100,     "pp": var_cv_pes,     "po": var_cv_opt},
    {"nombre": var_names[2], "fp": 1-var_vol_pes/100,    "fo": 1+var_vol_opt/100,    "pp": var_vol_pes,    "po": var_vol_opt},
    {"nombre": var_names[3], "fp": 1-var_cf_pes/100,     "fo": 1+var_cf_opt/100,     "pp": var_cf_pes,     "po": var_cf_opt},
    {"nombre": var_names[4], "fp": 1-var_pesimista_pct/100, "fo": 1+var_optimista_pct/100, "pp": var_pesimista_pct, "po": var_optimista_pct},
    {"nombre": var_names[5], "fp": 1-var_pesimista_pct/100, "fo": 1+var_optimista_pct/100, "pp": var_pesimista_pct, "po": var_optimista_pct},
    {"nombre": var_names[6], "fp": 1-var_pesimista_pct/100, "fo": 1+var_optimista_pct/100, "pp": var_pesimista_pct, "po": var_optimista_pct},
]

resultados_tornado = []
for var in variables_tornado:
    vp, vo = calcular_van_tornado(
        var["nombre"], var["fp"], var["fo"],
        precio_base, volumen_base, tax_rate, tasa_descuento, n_periodos,
        inversion_inicial, dep_anual, cap_trabajo, salvamento,
        costo_var, costo_fijo, tipo_cambio
    )
    resultados_tornado.append({
        T["col_var"]: var["nombre"],
        T["col_pes"]: vp,
        T["col_opt"]: vo,
        T["col_rng"]: abs(vo - vp),
        T["col_pp"]:  var["pp"],
        T["col_po"]:  var["po"],
    })
resultados_tornado.sort(key=lambda x: x[T["col_rng"]], reverse=True)

# Tabla
df_tornado = pd.DataFrame(resultados_tornado)
df_display = df_tornado.copy()
df_display.index = range(1, len(df_display) + 1)

def color_van_cell(val):
    if isinstance(val, (int, float)):
        return "background-color: #E2EFDA" if val >= 0 else "background-color: #FCE4D6"
    return ""

styler = df_display.style.format({
    T["col_pes"]: "${:,.2f}",
    T["col_opt"]: "${:,.2f}",
    T["col_rng"]: "${:,.2f}",
    T["col_pp"]:  "{:.0f}%",
    T["col_po"]:  "{:.0f}%",
}).background_gradient(subset=[T["col_rng"]], cmap="Blues")
try:
    styler = styler.map(color_van_cell, subset=[T["col_pes"], T["col_opt"]])
except AttributeError:
    styler = styler.applymap(color_van_cell, subset=[T["col_pes"], T["col_opt"]])

st.dataframe(styler, use_container_width=True)

# ── Gráfico Tornado ──────────────────────────────────────────────────────────
vars_plot    = [r[T["col_var"]] for r in reversed(resultados_tornado)]
van_pes_plot = [r[T["col_pes"]] for r in reversed(resultados_tornado)]
van_opt_plot = [r[T["col_opt"]] for r in reversed(resultados_tornado)]

n_vars = len(vars_plot)
y_pos  = np.arange(n_vars)

COLOR_PES  = "#C00000"
COLOR_OPT  = "#1F4E78"
COLOR_BASE = "#FFD966"

# Calcular rango total para ajustar márgenes de etiquetas
all_vals = van_pes_plot + van_opt_plot + [van_base]
x_min_data = min(all_vals)
x_max_data = max(all_vals)
x_span = x_max_data - x_min_data if x_max_data != x_min_data else 1.0

fig_tornado, ax_tornado = plt.subplots(figsize=(13, max(5, n_vars * 1.1)))

for i, (pes, opt, _) in enumerate(zip(van_pes_plot, van_opt_plot, vars_plot)):
    width = abs(opt - pes) if abs(opt - pes) > 0 else x_span * 0.01
    if pes < van_base:
        ax_tornado.barh(i, van_base - pes, left=pes, height=0.5,
                        color=COLOR_PES, alpha=0.85, zorder=3)
    if opt > van_base:
        ax_tornado.barh(i, opt - van_base, left=van_base, height=0.5,
                        color=COLOR_OPT, alpha=0.85, zorder=3)
    # Etiquetas con offset fijo basado en el span total (evita overlap)
    offset = x_span * 0.015
    ax_tornado.text(pes - offset, i, f"${pes:,.0f}",
                    va="center", ha="right", fontsize=7.5,
                    color=COLOR_PES, fontweight="bold")
    ax_tornado.text(opt + offset, i, f"${opt:,.0f}",
                    va="center", ha="left", fontsize=7.5,
                    color=COLOR_OPT, fontweight="bold")

ax_tornado.axvline(van_base, color=COLOR_BASE, linewidth=2.5, linestyle="--",
                   zorder=4, label=T["leg_base"].format(v=van_base))
ax_tornado.axvline(0, color="gray", linewidth=1.0, linestyle=":", zorder=2,
                   label=T["van_zero"])

# Ampliar límites del eje X para que las etiquetas no queden cortadas
margin = x_span * 0.18
ax_tornado.set_xlim(x_min_data - margin, x_max_data + margin)

ax_tornado.set_yticks(y_pos)
ax_tornado.set_yticklabels(vars_plot, fontsize=9.5, fontweight="bold")
ax_tornado.set_xlabel(T["tornado_xlabel"], fontsize=11, fontweight="bold")
ax_tornado.set_title(
    T["tornado_title"].format(pp=var_pesimista_pct, po=var_optimista_pct,
                               n=n_periodos, k=tasa_descuento*100),
    fontsize=12, fontweight="bold", color="#1F4E78", pad=18
)
ax_tornado.grid(True, axis="x", linestyle=":", alpha=0.5, zorder=1)

patch_pes = mpatches.Patch(color=COLOR_PES, alpha=0.85, label=T["leg_pes"])
patch_opt = mpatches.Patch(color=COLOR_OPT, alpha=0.85, label=T["leg_opt"])
line_base = plt.Line2D([0], [0], color=COLOR_BASE, linewidth=2.5,
                        linestyle="--", label=T["leg_base"].format(v=van_base))
ax_tornado.legend(handles=[patch_pes, patch_opt, line_base],
                  loc="lower right", fontsize=9, framealpha=0.9)
ax_tornado.spines["top"].set_visible(False)
ax_tornado.spines["right"].set_visible(False)
plt.tight_layout(pad=1.5)
st.pyplot(fig_tornado)
plt.close(fig_tornado)

# Interpretación
st.markdown(T["interp_title"])
var_critica = resultados_tornado[0]
var_menor   = resultados_tornado[-1]
ci1, ci2 = st.columns(2)
with ci1:
    st.info(T["most_critical"].format(
        v=var_critica[T["col_var"]], r=var_critica[T["col_rng"]],
        p=var_critica[T["col_pes"]], o=var_critica[T["col_opt"]]))
with ci2:
    st.success(T["least_critical"].format(
        v=var_menor[T["col_var"]], r=var_menor[T["col_rng"]],
        p=var_menor[T["col_pes"]], o=var_menor[T["col_opt"]]))

jerarquia = " > ".join([r[T["col_var"]] for r in resultados_tornado])
st.markdown(T["hierarchy"].format(h=jerarquia))

# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN IV – DESCARGAS (Excel + CSV)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"### {T['dl_header']}")

dl_col1, dl_col2 = st.columns(2)

# ── Excel ────────────────────────────────────────────────────────────────────
with dl_col1:
    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
        # Hoja 1: Flujo de Caja
        df_flujos.to_excel(writer, sheet_name="Flujo de Caja" if lang_choice == "Español" else "Cash Flow")
        # Hoja 2: Tornado
        df_tornado.to_excel(writer, sheet_name="Tornado", index=False)
        # Hoja 3: Parámetros
        params_label = "Parámetro" if lang_choice == "Español" else "Parameter"
        params_val   = "Valor"     if lang_choice == "Español" else "Value"
        df_params = pd.DataFrame({
            params_label: [
                T["n_periodos"], T["precio_base"], T["costo_var"],
                T["volumen_base"], T["costo_fijo"], T["tax_rate"],
                T["wacc"], T["tipo_cambio"], T["inversion"],
                T["cap_trabajo"], T["salvamento"],
                "VAN Base" if lang_choice == "Español" else "Base NPV",
                "TIR" if lang_choice == "Español" else "IRR",
            ],
            params_val: [
                n_periodos, precio_base, costo_var,
                volumen_base, costo_fijo, f"{tax_rate_pct:.1f}%",
                f"{tasa_desc_pct:.1f}%", tipo_cambio, inversion_inicial,
                f"{cap_trabajo_pct:.1f}%", f"{salvamento_pct:.1f}%",
                f"${van_base:,.2f}", f"{tir_val*100:.2f}%",
            ]
        })
        df_params.to_excel(writer, sheet_name="Parámetros" if lang_choice == "Español" else "Parameters", index=False)
    excel_buf.seek(0)
    st.download_button(
        label=T["dl_excel"],
        data=excel_buf,
        file_name="simulador_van_reporte.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help=T["dl_excel_help"],
        use_container_width=True
    )

# ── CSV ──────────────────────────────────────────────────────────────────────
with dl_col2:
    csv_buf = io.StringIO()
    df_tornado.to_csv(csv_buf, index=False)
    st.download_button(
        label=T["dl_csv"],
        data=csv_buf.getvalue().encode("utf-8"),
        file_name="tornado_sensibilidad.csv",
        mime="text/csv",
        help=T["dl_csv_help"],
        use_container_width=True
    )

# ─────────────────────────────────────────────────────────────────────────────
# PIE DE PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(T["footer"].format(v=resultados_tornado[0][T["col_var"]], n=n_periodos))