import streamlit as st
import random
import pandas as pd
import math
import re

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Asistente de Instrumentación v8.0 JR - Mejorado",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS MEJORADOS ---
st.markdown("""
<style>
    .st-expander {
        border: 2px solid #2C3E50;
        border-radius: 15px;
        margin-bottom: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .st-expander header {
        background: linear-gradient(90deg, #3498DB, #2C3E50);
        color: white;
        border-radius: 12px 12px 0 0;
        font-weight: bold;
        padding: 10px;
    }
    [data-testid="stMetricValue"] {
        font-size: 28px;
        color: #0066CC;
        font-weight: bold;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        color: #155724;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        color: #721c24;
    }
    .info-box {
        background-color: #e2f3ff;
        border: 1px solid #b8daff;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        color: #004085;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

# --- BASES DE DATOS EXPANDIDAS (DICCIONARIOS ISA-5.1) ---

FIRST_LETTER = {
    'A': 'Análisis', 'B': 'Llama (Burner)', 'C': 'Conductividad', 'D': 'Densidad o Peso Específico', 'E': 'Tensión (Voltaje)',
    'F': 'Caudal (Flow)', 'G': 'Calibre/Dimensión (Gauge)', 'H': 'Manual (Hand)', 'I': 'Corriente', 'J': 'Potencia',
    'K': 'Tiempo o Programa', 'L': 'Nivel (Level)', 'M': 'Humedad (Moisture)', 'N': 'Definido por Usuario', 'O': 'Definido por Usuario',
    'P': 'Presión o Vacío', 'Q': 'Cantidad', 'R': 'Radiactividad', 'S': 'Velocidad o Frecuencia', 'T': 'Temperatura',
    'U': 'Multivariable', 'V': 'Vibración o Análisis Mecánico', 'W': 'Peso o Fuerza', 'X': 'Sin clasificar', 'Y': 'Evento, Estado o Presencia', 'Z': 'Posición o Dimensión'
}

SUCCESSOR_LETTERS = {
    'A': 'Alarma', 'B': 'Definido por Usuario', 'C': 'Control', 'D': 'Diferencial', 'E': 'Elemento Primario (Sensor)',
    'F': 'Relación (Ratio)', 'G': 'Visor o Vidrio (Glass)', 'H': 'Alto', 'I': 'Indicación', 'J': 'Exploración (Scan)',
    'K': 'Estación de Control', 'L': 'Luz Piloto o Bajo', 'M': 'Medio o Intermedio', 'N': 'Definido por Usuario',
    'O': 'Orificio de Restricción', 'P': 'Punto de Prueba', 'Q': 'Integrador o Totalizador', 'R': 'Registro (Recorder)',
    'S': 'Interruptor (Switch) o Seguridad', 'T': 'Transmisión', 'U': 'Multifunción', 'V': 'Válvula, Damper o Actuador',
    'W': 'Pozo (Well)', 'X': 'Accesorio o Sin clasificar', 'Y': 'Relé, Convertidor o Computador', 'Z': 'Elemento Final de Control (no clasificado)'
}

INSTRUMENT_DATABASE = {
    # Instrumentos de Presión
    'PI': {'variable': 'Presión', 'funcion': 'Indicador', 'rango_tipico': '0-10 bar', 'exactitud_tipica': '±0.5%'},
    'PIT': {'variable': 'Presión', 'funcion': 'Indicador-Transmisor', 'rango_tipico': '0-25 bar', 'exactitud_tipica': '±0.25%'},
    'PIC': {'variable': 'Presión', 'funcion': 'Indicador-Controlador', 'rango_tipico': '0-16 bar', 'exactitud_tipica': '±0.5%'},
    'PIR': {'variable': 'Presión', 'funcion': 'Indicador-Registrador', 'rango_tipico': '0-40 bar', 'exactitud_tipica': '±0.3%'},
    'PSH': {'variable': 'Presión', 'funcion': 'Switch Alto', 'rango_tipico': '0-100 bar', 'exactitud_tipica': '±1%'},
    'PSL': {'variable': 'Presión', 'funcion': 'Switch Bajo', 'rango_tipico': '0-50 bar', 'exactitud_tipica': '±1%'},
    'PDI': {'variable': 'Presión Diferencial', 'funcion': 'Indicador', 'rango_tipico': '0-2500 mmH2O', 'exactitud_tipica': '±0.5%'},
    'PDT': {'variable': 'Presión Diferencial', 'funcion': 'Transmisor', 'rango_tipico': '0-6000 mmH2O', 'exactitud_tipica': '±0.25%'},
    
    # Instrumentos de Temperatura
    'TI': {'variable': 'Temperatura', 'funcion': 'Indicador', 'rango_tipico': '0-500 °C', 'exactitud_tipica': '±1°C'},
    'TIT': {'variable': 'Temperatura', 'funcion': 'Indicador-Transmisor', 'rango_tipico': '-50-800 °C', 'exactitud_tipica': '±0.5°C'},
    'TIC': {'variable': 'Temperatura', 'funcion': 'Indicador-Controlador', 'rango_tipico': '0-1200 °C', 'exactitud_tipica': '±2°C'},
    'TIR': {'variable': 'Temperatura', 'funcion': 'Indicador-Registrador', 'rango_tipico': '0-600 °C', 'exactitud_tipica': '±1°C'},
    'TSH': {'variable': 'Temperatura', 'funcion': 'Switch Alto', 'rango_tipico': '0-300 °C', 'exactitud_tipica': '±3°C'},
    'TSL': {'variable': 'Temperatura', 'funcion': 'Switch Bajo', 'rango_tipico': '0-200 °C', 'exactitud_tipica': '±3°C'},
    'TE': {'variable': 'Temperatura', 'funcion': 'Elemento Sensor', 'rango_tipico': '-200-1600 °C', 'exactitud_tipica': '±0.1°C'},
    'TT': {'variable': 'Temperatura', 'funcion': 'Transmisor', 'rango_tipico': '-40-850 °C', 'exactitud_tipica': '±0.3°C'},
    
    # Instrumentos de Nivel
    'LI': {'variable': 'Nivel', 'funcion': 'Indicador', 'rango_tipico': '0-100 %', 'exactitud_tipica': '±1%'},
    'LIT': {'variable': 'Nivel', 'funcion': 'Indicador-Transmisor', 'rango_tipico': '0-10 m', 'exactitud_tipica': '±0.5%'},
    'LIC': {'variable': 'Nivel', 'funcion': 'Indicador-Controlador', 'rango_tipico': '0-5 m', 'exactitud_tipica': '±1%'},
    'LSH': {'variable': 'Nivel', 'funcion': 'Switch Alto', 'rango_tipico': '0-20 m', 'exactitud_tipica': '±2%'},
    'LSL': {'variable': 'Nivel', 'funcion': 'Switch Bajo', 'rango_tipico': '0-15 m', 'exactitud_tipica': '±2%'},
    'LT': {'variable': 'Nivel', 'funcion': 'Transmisor', 'rango_tipico': '0-30 m', 'exactitud_tipica': '±0.25%'},
    'LG': {'variable': 'Nivel', 'funcion': 'Visor/Indicador Visual', 'rango_tipico': '0-3 m', 'exactitud_tipica': '±5%'},
    
    # Instrumentos de Caudal
    'FI': {'variable': 'Caudal', 'funcion': 'Indicador', 'rango_tipico': '0-1000 m³/h', 'exactitud_tipica': '±1%'},
    'FIT': {'variable': 'Caudal', 'funcion': 'Indicador-Transmisor', 'rango_tipico': '0-500 m³/h', 'exactitud_tipica': '±0.5%'},
    'FIC': {'variable': 'Caudal', 'funcion': 'Indicador-Controlador', 'rango_tipico': '0-2000 m³/h', 'exactitud_tipica': '±1%'},
    'FT': {'variable': 'Caudal', 'funcion': 'Transmisor', 'rango_tipico': '0-10000 m³/h', 'exactitud_tipica': '±0.25%'},
    'FE': {'variable': 'Caudal', 'funcion': 'Elemento Primario', 'rango_tipico': '0-5000 m³/h', 'exactitud_tipica': '±2%'},
    'FQ': {'variable': 'Caudal', 'funcion': 'Totalizador', 'rango_tipico': '0-999999 m³', 'exactitud_tipica': '±0.1%'},

    # Instrumentos Eléctricos (NUEVOS)
    'EI': {'variable': 'Tensión', 'funcion': 'Indicador', 'rango_tipico': '0-150 V', 'exactitud_tipica': '±1.5%'},
    'ET': {'variable': 'Tensión', 'funcion': 'Transmisor', 'rango_tipico': '0-600 V', 'exactitud_tipica': '±0.2%'},
    'EIC': {'variable': 'Tensión', 'funcion': 'Indicador-Controlador', 'rango_tipico': '0-100 V', 'exactitud_tipica': '±0.5%'},
    'II': {'variable': 'Corriente', 'funcion': 'Indicador', 'rango_tipico': '0-50 A', 'exactitud_tipica': '±1.5%'},
    'IT': {'variable': 'Corriente', 'funcion': 'Transmisor', 'rango_tipico': '0-100 A', 'exactitud_tipica': '±0.5%'},
    'IIT': {'variable': 'Corriente', 'funcion': 'Indicador-Transmisor', 'rango_tipico': '0-60 A', 'exactitud_tipica': '±0.75%'},
    
    # Instrumentos de Análisis
    'AI': {'variable': 'Análisis', 'funcion': 'Indicador', 'rango_tipico': '0-14 pH', 'exactitud_tipica': '±0.1 pH'},
    'AIT': {'variable': 'Análisis', 'funcion': 'Indicador-Transmisor', 'rango_tipico': '0-20 ppm', 'exactitud_tipica': '±2%'},
    'AIC': {'variable': 'Análisis', 'funcion': 'Indicador-Controlador', 'rango_tipico': '0-100 %', 'exactitud_tipica': '±1%'},
    'AT': {'variable': 'Análisis', 'funcion': 'Transmisor', 'rango_tipico': '0-1000 ppm', 'exactitud_tipica': '±3%'},
    
    # Instrumentos de Conductividad
    'CI': {'variable': 'Conductividad', 'funcion': 'Indicador', 'rango_tipico': '0-2000 µS/cm', 'exactitud_tipica': '±2%'},
    'CIT': {'variable': 'Conductividad', 'funcion': 'Indicador-Transmisor', 'rango_tipico': '0-20000 µS/cm', 'exactitud_tipica': '±1%'},
    'CT': {'variable': 'Conductividad', 'funcion': 'Transmisor', 'rango_tipico': '0-200000 µS/cm', 'exactitud_tipica': '±1.5%'},
    
    # Válvulas de Control
    'PCV': {'variable': 'Presión', 'funcion': 'Válvula de Control', 'rango_tipico': 'Cv 0.1-1000', 'exactitud_tipica': '±5%'},
    'TCV': {'variable': 'Temperatura', 'funcion': 'Válvula de Control', 'rango_tipico': 'Cv 0.5-500', 'exactitud_tipica': '±5%'},
    'FCV': {'variable': 'Caudal', 'funcion': 'Válvula de Control', 'rango_tipico': 'Cv 1-2000', 'exactitud_tipica': '±3%'},
    'LCV': {'variable': 'Nivel', 'funcion': 'Válvula de Control', 'rango_tipico': 'Cv 0.2-800', 'exactitud_tipica': '±5%'},
}

ERROR_TYPES = {
    'A': 'Porcentaje del máximo valor del campo de indicación',
    'B': 'Porcentaje del span (rango)',
    'C': 'Porcentaje del valor a medir',
    'D': 'Valor fijo según la variable'
}

# --- FUNCIONES DE CÁLCULO Y LÓGICA ---

def convert_pressure(value, from_unit, to_unit):
    to_pascal = {
        'Pa': 1, 'kPa': 1000, 'MPa': 1e6, 'bar': 1e5, 'mbar': 100,
        'psi': 6894.76, 'kg/cm²': 98066.5, 'atm': 101325,
        'mmH2O': 9.80665, 'inH2O': 249.089
    }
    if from_unit not in to_pascal or to_unit not in to_pascal: return None
    return (value * to_pascal[from_unit]) / to_pascal[to_unit]

def convert_temperature(value, from_unit, to_unit):
    try:
        if from_unit == '°C': celsius = value
        elif from_unit == '°F': celsius = (value - 32) * 5/9
        elif from_unit == 'K': celsius = value - 273.15
        else: return None

        if to_unit == '°C': return round(celsius, 2)
        elif to_unit == '°F': return round(celsius * 9/5 + 32, 2)
        elif to_unit == 'K': return round(celsius + 273.15, 2)
        else: return None
    except:
        return None

def calculate_cv_liquid(flow_rate, sg, p1, p2):
    if p1 <= p2:
        return None, "La presión de entrada debe ser mayor que la de salida."
    delta_p = p1 - p2
    cv = flow_rate * math.sqrt(sg / delta_p)
    return round(cv, 2), None

def calculate_orifice_flow(dp, k):
    if dp < 0 or k <=0:
        return None, "La presión diferencial y el factor K deben ser positivos."
    flow = k * math.sqrt(dp)
    return round(flow, 2), None


def find_suitable_instruments(measurement_value, variable_type, accuracy_required):
    """Devuelve instrumentos cuyo rango incluye el valor a medir. Marca si están en campo óptimo."""
    suitable_instruments = {}
    for tag, specs in INSTRUMENT_DATABASE.items():
        if variable_type.lower() in specs['variable'].lower():
            range_match = re.search(r'(-?\d+(?:\.\d+)?)\s*-\s*(-?\d+(?:\.\d+)?)', specs['rango_tipico'])
            if range_match:
                try:
                    min_range = float(range_match.group(1))
                    max_range = float(range_match.group(2))
                    if max_range <= min_range:
                        continue
                    span = max_range - min_range
                    in_range = min_range <= measurement_value <= max_range
                    in_optimal = (min_range + 0.25 * span) <= measurement_value <= (min_range + 0.75 * span)
                    if in_range:
                        specs['campo_optimo'] = in_optimal
                        suitable_instruments[tag] = specs
                except (ValueError, IndexError):
                    continue
    return suitable_instruments


def calculate_measurement_errors(instrument_specs, measurement_value, error_percentages):
    """Calcula los diferentes tipos de error para un instrumento dado."""
    # Regex mejorado para capturar números negativos y decimales.
    range_match = re.search(r'(-?\d+(?:\.\d+)?)\s*-\s*(-?\d+(?:\.\d+)?)', instrument_specs['rango_tipico'])
    if not range_match:
        return None, None
    
    try:
        min_range = float(range_match.group(1))
        max_range = float(range_match.group(2))
    except (ValueError, IndexError):
        return None, None

    span = max_range - min_range
    if span <= 0: return None, None
    
    errors = {}
    
    # Error Tipo A: Porcentaje del MÁXIMO valor del campo de indicación.
    errors['A'] = (error_percentages['A'] / 100) * max_range
    
    # Error Tipo B: Porcentaje del SPAN.
    errors['B'] = (error_percentages['B'] / 100) * span
    
    # Error Tipo C: Porcentaje del VALOR MEDIDO.
    errors['C'] = (error_percentages['C'] / 100) * measurement_value
    
    # Error Tipo D: Valor FIJO.
    errors['D'] = error_percentages['D']
    
    return errors, instrument_specs


# --- FUNCIONES PARA EL CENTRO DE PRÁCTICA (SIN CAMBIOS) ---
def generate_scaling_quiz():
    pv_types = [{'name': 'Presión', 'units': 'bar'}, {'name': 'Temperatura', 'units': '°C'}, {'name': 'Nivel', 'units': '%'}, {'name': 'Caudal', 'units': 'm³/h'}]
    signal_types = [{'name': 'Corriente', 'units': 'mA', 'lrv': 4, 'urv': 20}, {'name': 'Voltaje', 'units': 'V', 'lrv': 1, 'urv': 5}]
    pv, signal = random.choice(pv_types), random.choice(signal_types)
    lrv_pv, urv_pv = round(random.uniform(0, 50)), round(random.uniform(100, 500))
    if random.choice([True, False]): # PV -> OUT
        input_val = round(random.uniform(lrv_pv, urv_pv), 1)
        correct_out = (((input_val - lrv_pv) / (urv_pv - lrv_pv)) * (signal['urv'] - signal['lrv'])) + signal['lrv']
        question = f"Un transmisor de **{pv['name']}** con rango **{lrv_pv} a {urv_pv} {pv['units']}** y salida **{signal['lrv']}-{signal['urv']} {signal['units']}**, ¿qué salida corresponde a **{input_val} {pv['units']}**?"
        correct_answer = f"{correct_out:.2f} {signal['units']}"
        unit = signal['units']
        base_value = correct_out
    else: # OUT -> PV
        input_val = round(random.uniform(signal['lrv'], signal['urv']), 2)
        correct_out = (((input_val - signal['lrv']) / (signal['urv'] - signal['lrv'])) * (urv_pv - lrv_pv)) + lrv_pv
        question = f"Un transmisor de **{pv['name']}** con rango **{lrv_pv} a {urv_pv} {pv['units']}** y salida **{signal['lrv']}-{signal['urv']} {signal['units']}**, ¿qué PV corresponde a **{input_val} {signal['units']}**?"
        correct_answer = f"{correct_out:.1f} {pv['units']}"
        unit = pv['units']
        base_value = correct_out
    options = {correct_answer}
    while len(options) < 4:
        distractor = base_value * random.uniform(0.5, 1.5)
        if abs(distractor - base_value) > 0.1 * base_value:
            options.add(f"{distractor:.2f} {unit}" if isinstance(base_value, float) and base_value != int(base_value) else f"{distractor:.1f} {unit}")
    return question, list(options), correct_answer

def generate_tag_quiz():
    first = random.choice(list(FIRST_LETTER.keys()))
    successors = random.sample(list(SUCCESSOR_LETTERS.keys()), random.randint(1, 2))
    tag = f"{first}{''.join(successors)}-{random.randint(100,999)}"
    question = f"¿Qué significa el tag **{tag}** según ISA-5.1?"
    desc = [FIRST_LETTER[first]]
    for letter in successors:
        desc.append(SUCCESSOR_LETTERS[letter])
    correct_answer = " - ".join(desc)
    options = {correct_answer}
    while len(options) < 4:
        w_first = random.choice(list(FIRST_LETTER.values()))
        w_succ = random.sample(list(SUCCESSOR_LETTERS.values()), len(successors))
        distractor = f"{w_first} - {' - '.join(w_succ)}"
        if distractor != correct_answer:
            options.add(distractor)
    return question, list(options), correct_answer

# --- INTERFAZ DE USUARIO (UI) ---

st.title("🛠️ Asistente de Instrumentación Industrial v8.0 - Mejorado")
st.markdown("*Herramienta avanzada para cálculos, interpretación de normas, análisis de errores y práctica profesional*")

with st.sidebar:
    st.header("⭐ Tips del Ingeniero")
    tips = [
        "La exactitud no es lo mismo que la repetibilidad. Un instrumento puede ser muy repetible pero poco exacto.",
        "El 'Campo de Medida' (25-75% del rango) es donde un transmisor ofrece su mejor rendimiento.",
        "Un lazo de control se compone de: medición (sensor), controlador (PLC/DCS) y elemento final (válvula).",
        "La calibración en 5 puntos (0%, 25%, 50%, 75%, 100%) es esencial para verificar la linealidad del instrumento.",
        "La histéresis es la diferencia entre lecturas ascendentes y descendentes en el mismo punto de medida.",
        "La 'rangeabilidad' (turndown) indica cuánto se puede reducir el rango de un transmisor sin perder la exactitud especificada.",
        "En la selección de válvulas de control, un Cv calculado debe quedar idealmente entre el 20% y 80% del recorrido de la válvula.",
        "La presión diferencial para medir caudal con placa de orificio varía con el cuadrado del flujo ($ΔP ∝ Q^2$).",
        "Para medición con exactitud, el valor a medir debe estar cerca del 50% del campo de indicación del instrumento.",
        "Los errores tipo A se expresan como % del máximo del rango, tipo B como % del span, tipo C como % del valor medido.",
    ]
    if 'tip_index' not in st.session_state:
        st.session_state.tip_index = 0
    st.info(f"💡 {tips[st.session_state.tip_index]}")
    if st.button("Siguiente Tip 💡"):
        st.session_state.tip_index = (st.session_state.tip_index + 1) % len(tips)
        st.rerun()
    st.divider()
    st.header("📋 Referencia Rápida ISA-5.1 (Expandida)")
    st.selectbox("Primera Letra (Variable)", options=list(FIRST_LETTER.items()), format_func=lambda x: f"{x[0]} - {x[1]}")
    st.selectbox("Letras Sucesivas (Función)", options=list(SUCCESSOR_LETTERS.items()), format_func=lambda x: f"{x[0]} - {x[1]}")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["**📐 Herramientas de Cálculo**", "**📖 Interpretador ISA-5.1**", "**🧠 Centro de Práctica**", "**🔧 Conversores de Unidades**", "**⚠️ Análisis de Errores**"])

with tab1:
    st.header("Cálculos Fundamentales de Instrumentación")
    with st.expander("**📈 Calculadora de Escalamiento y Tabla de Calibración Personalizable**", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Variable de Proceso (PV)")
            pv_units = st.text_input("Unidades PV", "kPa")
            lrv_pv = st.number_input("LRV (Límite Inferior del Rango)", value=0.0, format="%.2f")
            urv_pv = st.number_input("URV (Límite Superior del Rango)", value=1000.0, format="%.2f")
        with col2:
            st.subheader("Señal de Salida (OUT)")
            out_units = st.text_input("Unidades Salida", "mA")
            lrv_out = st.number_input("LRV Salida", value=4.0, format="%.2f")
            urv_out = st.number_input("URV Salida", value=20.0, format="%.2f")
        st.subheader("🎯 Puntos de Verificación Personalizables")
        col1, col2, col3, col4, col5 = st.columns(5)
        p1 = col1.number_input("Punto 1 (%)", value=0, min_value=0, max_value=100)
        p2 = col2.number_input("Punto 2 (%)", value=25, min_value=0, max_value=100)
        p3 = col3.number_input("Punto 3 (%)", value=50, min_value=0, max_value=100)
        p4 = col4.number_input("Punto 4 (%)", value=75, min_value=0, max_value=100)
        p5 = col5.number_input("Punto 5 (%)", value=100, min_value=0, max_value=100)
        custom_percentages = [p1, p2, p3, p4, p5]
        st.divider()
        if urv_pv > lrv_pv and urv_out > lrv_out:
            span_pv = urv_pv - lrv_pv
            span_out = urv_out - lrv_out
            st.subheader("📊 Tabla de Puntos de Verificación Personalizada")
            table_data = { "Porcentaje (%)": custom_percentages, f"Variable de Proceso ({pv_units})": [lrv_pv + (p/100) * span_pv for p in custom_percentages], f"Señal de Salida ({out_units})": [lrv_out + (p/100) * span_out for p in custom_percentages] }
            df = pd.DataFrame(table_data)
            st.dataframe(df.style.format({df.columns[1]: "{:.2f}", df.columns[2]: "{:.2f}"}), use_container_width=True)
            optimal_value = lrv_pv + 0.5 * span_pv
            st.info(f"🎯 **Campo de Medida Óptimo (50%):** {optimal_value:.2f} {pv_units} - Para máxima exactitud, mida cerca de este valor.")
        else:
            st.error("El valor URV debe ser mayor que el LRV para ambos rangos.")
    with st.expander("**밸 Calculadora de Coeficiente de Válvula (Cv) para Líquidos**"):
        st.latex(r"C_v = Q \sqrt{\frac{SG}{\Delta P}}")
        c1, c2, c3 = st.columns(3)
        flow_rate_q = c1.number_input("Caudal (Q) [GPM]", value=100.0, format="%.2f")
        sg = c2.number_input("Gravedad Específica (SG)", value=1.0, format="%.2f", help="Para agua, SG=1")
        c1, c2 = st.columns(2)
        p1 = c1.number_input("Presión de Entrada (P1) [psi]", value=50.0, format="%.2f")
        p2 = c2.number_input("Presión de Salida (P2) [psi]", value=30.0, format="%.2f")
        if st.button("Calcular Cv"):
            cv, error_msg = calculate_cv_liquid(flow_rate_q, sg, p1, p2)
            if error_msg: st.error(error_msg)
            else:
                st.metric("Coeficiente de Válvula Requerido (Cv)", f"{cv}")
                st.info(f"Seleccione una válvula con un Cv nominal mayor a **{cv}**. Se recomienda que este valor esté entre el 20% y 80% del rango de operación de la válvula seleccionada.")
    with st.expander("**🎛️ Calculadora de Caudal por Placa de Orificio**"):
        st.latex(r"Q = K \sqrt{\Delta P}")
        k_factor = st.number_input("Factor K del Medidor", value=50.0, format="%.3f", help="Este factor depende de la geometría de la tubería, la placa y las propiedades del fluido.")
        delta_p = st.number_input("Presión Diferencial (ΔP) [inH2O]", value=100.0, format="%.2f")
        if st.button("Calcular Caudal"):
            flow, error_msg = calculate_orifice_flow(delta_p, k_factor)
            if error_msg: st.error(error_msg)
            else: st.metric("Caudal Calculado (Q)", f"{flow} unidades de caudal")

with tab2:
    st.header("📖 Interpretador de Tags de Instrumentación (ISA-5.1)")
    st.info("Introduce un tag de instrumento (ej: `TIC-101`, `PDT-50A`, `LSHH-203`) para ver su significado desglosado según la norma ISA-5.1.")
    tag_input = st.text_input("**Introduce el Tag del Instrumento:**", "TIC-101A").upper()
    if tag_input:
        match = re.match(r'^([A-Z]{1,4})(\d+)([A-Z]*)$', tag_input.replace('-', ''))
        if match:
            letters, loop_num, suffix = match.groups()
            st.subheader(f"Análisis del Tag: **{tag_input}**")
            c1, c2, c3 = st.columns(3)
            c1.metric("Identificación de Letras", letters)
            c2.metric("Número de Lazo", loop_num)
            c3.metric("Sufijo (si aplica)", suffix if suffix else "N/A")
            st.markdown("---")
            descriptions = []
            first_letter = letters[0]
            if first_letter in FIRST_LETTER: descriptions.append(f"**{first_letter}** (Primera Letra): **{FIRST_LETTER[first_letter]}**. Esta es la variable medida o iniciadora del lazo de control.")
            else: descriptions.append(f"**{first_letter}**: Letra desconocida.")
            for i, letter in enumerate(letters[1:]):
                if letter in SUCCESSOR_LETTERS: descriptions.append(f"**{letter}** (Letra Sucesiva {i+1}): **{SUCCESSOR_LETTERS[letter]}**. Describe la función del instrumento en el lazo.")
                else: descriptions.append(f"**{letter}**: Letra desconocida.")
            for desc in descriptions: st.markdown(f"<li>{desc}</li>", unsafe_allow_html=True)
            st.markdown("---")
            if letters in INSTRUMENT_DATABASE:
                specs = INSTRUMENT_DATABASE[letters]
                st.success(f"**Instrumento Encontrado en Base de Datos:**")
                col1, col2 = st.columns(2)
                col1.write(f"**Rango Típico:** {specs['rango_tipico']}")
                col2.write(f"**Exactitud Típica:** {specs['exactitud_tipica']}")
            st.success(f"**Resumen:** El tag **{tag_input}** representa un instrumento en el lazo de control **{loop_num}** que se encarga de las funciones de **{' y '.join([SUCCESSOR_LETTERS.get(l, 'Función Desconocida') for l in letters[1:]])}** para la variable de **{FIRST_LETTER.get(first_letter, 'Variable Desconocida')}**.")
        else:
            st.warning("Formato de tag no reconocido. Por favor, use un formato como 'TIC101' o 'FT-205B'.")

with tab3:
    st.header("🧠 Centro de Práctica y Autoevaluación")
    st.info("Pon a prueba tus conocimientos con ejercicios generados aleatoriamente. ¡Nunca verás dos veces el mismo problema!")
    quiz_type = st.radio("Elige qué tema quieres practicar:", ["Ejercicios de Escalamiento", "Identificación de Tags (ISA-5.1)"], horizontal=True)
    if 'quiz_id' not in st.session_state: st.session_state.quiz_id = 0
    if 'quiz_stats' not in st.session_state: st.session_state.quiz_stats = {'correct': 0, 'total': 0}
    if st.session_state.quiz_stats['total'] > 0:
        accuracy = (st.session_state.quiz_stats['correct'] / st.session_state.quiz_stats['total']) * 100
        st.metric("📈 Tu Rendimiento General", f"{accuracy:.1f}%", delta=f"{st.session_state.quiz_stats['correct']} de {st.session_state.quiz_stats['total']} correctas")
    st.divider()
    quiz_key_prefix, generator_func = ("scaling", generate_scaling_quiz) if "Escalamiento" in quiz_type else ("tag", generate_tag_quiz)
    question_state_key = f"{quiz_key_prefix}_question"
    if question_state_key not in st.session_state: st.session_state[question_state_key] = generator_func()
    question, options, correct_answer = st.session_state[question_state_key]
    random.shuffle(options)
    user_answer = st.radio(f"**Problema:** {question}", options, key=f"{quiz_key_prefix}_question_{st.session_state.quiz_id}")
    col_btn1, col_btn2, _ = st.columns([1,1,2])
    if col_btn1.button("✅ Verificar Respuesta", key=f"verify_{quiz_key_prefix}"):
        st.session_state.quiz_stats['total'] += 1
        if user_answer == correct_answer:
            st.session_state.quiz_stats['correct'] += 1
            st.markdown('<div class="success-box">🎉 ¡Correcto! Excelente trabajo.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-box">❌ Incorrecto. La respuesta correcta es: **{correct_answer}**</div>', unsafe_allow_html=True)
    if col_btn2.button("➡️ Siguiente Ejercicio", key=f"next_{quiz_key_prefix}"):
        st.session_state[question_state_key] = generator_func()
        st.session_state.quiz_id += 1
        st.rerun()

with tab4:
    st.header("🔧 Conversores de Unidades")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🌡️ Conversor de Temperatura")
        temp_val = st.number_input("Valor Temp.", value=25.0, format="%.2f")
        temp_from = st.selectbox("De:", ('°C', '°F', 'K'))
        temp_to = st.selectbox("A:", ('°F', '°C', 'K'))
        result = convert_temperature(temp_val, temp_from, temp_to)
        if result is not None: st.metric(f"Resultado en {temp_to}", f"{result}")
    with c2:
        st.subheader("📊 Conversor de Presión")
        press_val = st.number_input("Valor Presión", value=1.0, format="%.3f")
        press_from = st.selectbox("De:", ('bar', 'psi', 'kPa', 'kg/cm²', 'atm', 'mmH2O', 'inH2O'))
        press_to = st.selectbox("A:", ('psi', 'bar', 'kPa', 'kg/cm²', 'atm', 'mmH2O', 'inH2O'))
        result = convert_pressure(press_val, press_from, press_to)
        if result is not None: st.metric(f"Resultado en {press_to}", f"{result:.4f}")

# --- PESTAÑA DE ANÁLISIS DE ERRORES (COMPLETAMENTE REESTRUCTURADA) ---
with tab5:
    st.header("⚠️ Análisis Guiado de Errores de Instrumentación")
    st.markdown("""
    Esta herramienta le guía en la selección de un instrumento adecuado y calcula los errores de medición.
    1.  **Defina la Medición**: Ingrese el valor y la variable que necesita medir.
    2.  **Especifique Exactitud**: Si requiere alta exactitud, el sistema filtrará instrumentos donde su valor de medición se encuentre en el **campo de medida** óptimo (entre 25% y 75% del rango del instrumento).
    3.  **Seleccione y Calcule**: Elija uno de los instrumentos sugeridos y calcule los errores asociados.
    """)

    # --- PASO 1: DEFINIR MEDICIÓN ---
    st.divider()
    st.subheader("Paso 1: Definir la Medición")
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        # Crear una lista única y ordenada de variables desde la base de datos
        variables_list = sorted(list(set(spec['variable'] for spec in INSTRUMENT_DATABASE.values())))
        variable = st.selectbox("Seleccione la Variable", options=variables_list, help="La variable física que desea medir.")
    
    with col2:
        valor_a_medir = st.number_input("Valor a Medir", value=50.0, format="%.2f", help="El valor numérico que espera medir.")
        
    with col3:
        st.write("Criterio de Selección:")
        exactitud_requerida = st.checkbox("Requiere Alta Exactitud", value=True, help="Filtra instrumentos para que el valor a medir esté en su rango óptimo (25%-75%).")

    # --- PASO 2: SELECCIONAR INSTRUMENTO COMPATIBLE ---
    st.divider()
    st.subheader("Paso 2: Seleccionar un Instrumento Compatible")

    # Buscar instrumentos que cumplan con los criterios del Paso 1
    instrumentos_compatibles = find_suitable_instruments(valor_a_medir, variable, exactitud_requerida)

    if not instrumentos_compatibles:
        st.warning("No se encontraron instrumentos en la base de datos que cumplan con los criterios especificados. Pruebe ajustar el 'Valor a Medir' o desactive la opción de 'Alta Exactitud'.")
    else:
        # Formatear las opciones para que el usuario vea el rango y seleccione fácilmente
        opciones_formateadas = [f"{tag}  |  Rango: {specs['rango_tipico']}  |  {"✅ Óptimo" if specs.get("campo_optimo") else "⚠️ No Óptimo"}" for tag, specs in instrumentos_compatibles.items()]
        seleccion_formateada = st.selectbox("Instrumentos Sugeridos:", opciones_formateadas)
        
        # Extraer el TAG del instrumento de la opción seleccionada
        tag_seleccionado = seleccion_formateada.split("  |  ")[0]
        
        # --- PASO 3: CONFIGURAR Y CALCULAR ERRORES ---
        st.divider()
        st.subheader(f"Paso 3: Calcular Errores para el Instrumento {tag_seleccionado}")
        
        col1_err, col2_err = st.columns(2)
        with col1_err:
            specs_seleccionado = instrumentos_compatibles[tag_seleccionado]
            st.info(f"**Instrumento Seleccionado: {tag_seleccionado}**")
            st.write(f"**Función:** {specs_seleccionado['funcion']}")
            st.write(f"**Rango:** {specs_seleccionado['rango_tipico']}")
            st.write(f"**Exactitud Típica:** {specs_seleccionado['exactitud_tipica']}")

        with col2_err:
            st.write("*Configure los errores según la hoja de datos del fabricante:*")
            error_a = st.number_input("Error Tipo A (% del máximo):", value=0.5, format="%.2f", help=ERROR_TYPES['A'])
            error_b = st.number_input("Error Tipo B (% del span):", value=0.25, format="%.2f", help=ERROR_TYPES['B'])
            error_c = st.number_input("Error Tipo C (% del valor medido):", value=1.0, format="%.2f", help=ERROR_TYPES['C'])
            error_d = st.number_input("Error Tipo D (valor fijo):", value=0.1, format="%.3f", help=ERROR_TYPES['D'])
        
        if st.button("🧮 Calcular Errores"):
            error_percentages = {'A': error_a, 'B': error_b, 'C': error_c, 'D': error_d}
            errors, _ = calculate_measurement_errors(specs_seleccionado, valor_a_medir, error_percentages)
            
            if errors:
                st.subheader("📊 Resultados del Análisis de Errores")
                error_data = {
                    'Tipo de Error': ['A', 'B', 'C', 'D'],
                    'Descripción': [ERROR_TYPES['A'], ERROR_TYPES['B'], ERROR_TYPES['C'], ERROR_TYPES['D']],
                    'Error Calculado (±)': [f"{errors['A']:.4f}", f"{errors['B']:.4f}", f"{errors['C']:.4f}", f"{errors['D']:.4f}"]
                }
                df_errors = pd.DataFrame(error_data)
                st.dataframe(df_errors.set_index('Tipo de Error'), use_container_width=True)
                
                # Resaltar el error más significativo
                max_error_val = max(errors.values())
                max_error_type = max(errors, key=errors.get)
                st.warning(f"⚠️ **Error Más Crítico:** El **Tipo {max_error_type}** es el más significativo para esta medición, con un valor de **±{max_error_val:.4f}** unidades.")
            else:
                st.error("No se pudieron calcular los errores. Verifique el formato del rango del instrumento en la base de datos.")

st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <h4>🛠️ Asistente de Instrumentación Industrial v8.0 - Mejorado</h4>
    <p>Desarrollado para ingenieros y técnicos de instrumentación y control | Basado en estándares ISA</p>
</div>
""", unsafe_allow_html=True)
