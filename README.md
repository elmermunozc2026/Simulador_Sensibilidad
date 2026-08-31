# Simulador Interactivo de Sensibilidad e Incertidumbre (VAN)
### Módulo 6 – Evaluación Financiera de Inversiones y Proyectos

---

## 📋 Descripción

Simulador financiero interactivo desarrollado en **Streamlit** que permite analizar de forma dinámica el **Valor Actual Neto (VAN)** y la **Tasa Interna de Retorno (TIR)** de un proyecto de inversión, con tres módulos integrados:

| Sección | Descripción |
|---------|-------------|
| **I. Flujo de Caja Base** | Proyección detallada para N períodos definidos por el usuario |
| **II. Sensibilidad / Monte Carlo** | Análisis cruzado Precio×Volumen o Simulación estocástica |
| **III. Gráfico de Tornado** | Análisis OAT de sensibilidad con visualización interactiva |

---

## 🚀 Instalación y Ejecución

### Requisitos previos
- Python 3.9 o superior
- pip

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/simulador-van.git
cd simulador-van

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`

---

## 🎛️ Parámetros del Simulador

### Sección 1 – Parámetros Base del Proyecto
Todos los parámetros cuentan con **doble control sincronizado** (casilla numérica + slider):

| Parámetro | Rango | Valor por defecto |
|-----------|-------|-------------------|
| Número de Períodos (años) | 1 – 20 | 5 |
| Precio de Venta Base ($/unidad) | 50 – 500 | 200 |
| Costo Variable Unitario ($/unidad) | 10 – 400 | 80 |
| Volumen de Ventas Base (unidades/año) | 100 – 5,000 | 1,000 |
| Costo Fijo Anual ($) | 0 – 500,000 | 50,000 |
| Tasa Impositiva Corporativa (%) | 0 – 60 | 35 |
| Tasa de Descuento / WACC (%) | 1 – 40 | 12 |
| Tipo de Cambio (moneda local/USD) | 0.5 – 20 | 1.0 |
| Inversión Inicial ($) | 10,000 – 5,000,000 | 300,000 |
| Capital de Trabajo (% de Inversión) | 0 – 50 | 18 |
| Valor de Salvamento (% de Inversión) | 0 – 100 | 40 |

> **Nota:** La depreciación lineal se calcula automáticamente: `Inversión / N períodos`

### Sección 2 – Simulación de Incertidumbre
- **Modo Determinístico:** Tabla de sensibilidad cruzada Precio × Volumen (heatmap)
- **Modo Monte Carlo:** Distribución de probabilidades del VAN con estadísticas clave

### Sección 3 – Análisis de Tornado
- Variación pesimista y optimista configurables globalmente (sidebar)
- Ajuste fino por variable individual (expander en la sección)
- Tabla de resultados ordenada por rango de impacto
- Gráfico de tornado con interpretación automática

---

## 📐 Modelo Financiero

### Fórmula del Flujo de Caja Neto (FCN)

```
Año 0:
  FCN₀ = −(Inversión Inicial + Capital de Trabajo)

Años 1 a N−1:
  Ventas     = Precio × Volumen × Tipo de Cambio
  EBIT       = Ventas − Costos Variables − Costos Fijos − Depreciación
  Impuesto   = max(0, EBIT × Tasa Impositiva)
  NOPAT      = EBIT − Impuesto
  OCF        = NOPAT + Depreciación

Año N (último período):
  FCNₙ = OCF + Salvamento × (1 − Tasa Impositiva) + Capital de Trabajo
```

### VAN y TIR

```
VAN = FCN₀ + Σ [FCNₜ / (1 + k)ᵗ]   para t = 1 … N

TIR: tasa r tal que VAN(r) = 0  [solver de bisección]
```

### Gráfico de Tornado (OAT)

Para cada variable sensible, se calcula:
- **VAN Pesimista:** variable reducida en X% (las demás en valor base)
- **VAN Optimista:** variable incrementada en Y% (las demás en valor base)
- **Rango:** |VAN Optimista − VAN Pesimista|
- Las variables se ordenan de **mayor a menor rango**

---

## 🗂️ Estructura del Proyecto

```
simulador-van/
├── app.py                  # Script principal de Streamlit
├── requirements.txt        # Dependencias Python
├── README.md               # Este archivo
└── .streamlit/
    └── config.toml         # Configuración de tema y servidor
```

---

## 🔧 Personalización

### Agregar nuevas variables al Tornado
En `app.py`, localizar la lista `variables_tornado` y agregar un nuevo diccionario:
```python
{
    "nombre": "Nueva Variable",
    "factor_pes": 1 - var_pesimista_pct / 100,
    "factor_opt": 1 + var_optimista_pct / 100,
    "var_pes_pct": var_pesimista_pct,
    "var_opt_pct": var_optimista_pct,
},
```
Luego, agregar el caso correspondiente en la función `calcular_van_tornado()`.

### Cambiar el tema visual
Editar `.streamlit/config.toml` con los colores corporativos deseados.

---

## 📚 Conceptos Clave

| Concepto | Descripción |
|----------|-------------|
| **VAN > 0** | El proyecto crea valor; se recomienda aceptar |
| **TIR > WACC** | La rentabilidad supera el costo de capital |
| **Análisis OAT** | One-At-a-Time: varía una variable, mantiene el resto constante |
| **Tornado** | Ordena variables por impacto; la barra más larga = variable más crítica |
| **Monte Carlo** | Modela incertidumbre simultánea con distribuciones de probabilidad |
| **CV (Coef. Variación)** | σ / |μ|: mide riesgo relativo del VAN esperado |

---

## ⚠️ Limitaciones del Modelo

1. **OAT no captura correlaciones:** El Tornado varía una variable a la vez; para análisis más robusto, usar Monte Carlo.
2. **Distribución normal en Monte Carlo:** Se asume normalidad para precio y volumen; en la práctica pueden seguir otras distribuciones.
3. **Depreciación lineal:** El modelo usa depreciación en línea recta; otros métodos (acelerada, MACRS) pueden aplicar según jurisdicción.
4. **Tasa de descuento constante:** Se asume WACC fijo durante todo el horizonte.

---

## 👨‍🏫 Uso Pedagógico

Este simulador está diseñado para el **Módulo 6: Evaluación Financiera de Inversiones y Proyectos** de programas de postgrado en Finanzas y FP&A.

**Preguntas sugeridas para el aula:**
- ¿Por qué la variable más crítica del Tornado tiene ese comportamiento?
- ¿Cómo cambia el VAN al extender el horizonte de evaluación?
- ¿Qué estrategias de cobertura (hedging) mitigarían el riesgo de la variable más sensible?
- ¿Cuándo conviene usar Monte Carlo en lugar del análisis OAT?

---

*Desarrollado para uso académico – FP&A Postgrado*