import streamlit as st
import random
import pandas as pd
import math
import re

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Asistente de Instrumentación v7.0 JR - Expandido",
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
    'TI': {'variable': 'Temperatura', 'funcion': 'Indicador', 'rango_tipico': '0-500°C', 'exactitud_tipica': '±1°C'},
    'TIT': {'variable': 'Temperatura', 'funcion': 'Indicador-Transmisor', 'rango_tipico': '-50-800°C', 'exactitud_tipica': '±0.5°C'},
    'TIC': {'variable': 'Temperatura', 'funcion': 'Indicador-Controlador', 'rango_tipico': '0-1200°C', 'exactitud_tipica': '±2°C'},
    'TIR': {'variable': 'Temperatura', 'funcion': 'Indicador-Registrador', 'rango_tipico': '0-600°C', 'exactitud_tipica': '±1°C'},
    'TSH': {'variable': 'Temperatura', 'funcion': 'Switch Alto', 'rango_tipico': '0-300°C', 'exactitud_tipica': '±3°C'},
    'TSL': {'variable': 'Temperatura', 'funcion': 'Switch Bajo', 'rango_tipico': '0-200°C', 'exactitud_tipica': '±3°C'},
    'TE': {'variable': 'Temperatura', 'funcion': 'Elemento Sensor', 'rango_tipico': '-200-1600°C', 'exactitud_tipica': '±0.1°C'},
    'TT': {'variable': 'Temperatura', 'funcion': 'Transmisor', 'rango_tipico': '-40-850°C', 'exactitud_tipica': '±0.3°C'},
    
    # Instrumentos de Nivel
    'LI': {'variable': 'Nivel', 'funcion': 'Indicador', 'rango_tipico': '0-100%', 'exactitud_tipica': '±1%'},
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
    
    # Instrumentos de Análisis
    'AI': {'variable': 'Análisis', 'funcion': 'Indicador', 'rango_tipico': '0-14 pH', 'exactitud_tipica': '±0.1 pH'},
    'AIT': {'variable': 'Análisis', 'funcion': 'Indicador-Transmisor', 'rango_tipico': '0-20 ppm', 'exactitud_tipica': '±2%'},
    'AIC': {'variable': 'Análisis', 'funcion': 'Indicador-Controlador', 'rango_tipico': '0-100%', 'exactitud_tipica': '±1%'},
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
    
    # Instrumentos Multivariable
    'UIT': {'variable': 'Multivariable', 'funcion': 'Indicador-Transmisor', 'rango_tipico': 'Variable', 'exactitud_tipica': '±0.1%'},
    'UT': {'variable': 'Multivariable', 'funcion': 'Transmisor', 'rango_tipico': 'Variable', 'exactitud_tipica': '±0.15%'},
    
    # Instrumentos de Vibración
    'VI': {'variable': 'Vibración', 'funcion': 'Indicador', 'rango_tipico': '0-50 mm/s', 'exactitud_tipica': '±5%'},
    'VIT': {'variable': 'Vibración', 'funcion': 'Indicador-Transmisor', 'rango_tipico': '0-100 mm/s', 'exactitud_tipica': '±3%'},
    'VT': {'variable': 'Vibración', 'funcion': 'Transmisor', 'rango_tipico': '0-200 mm/s', 'exactitud_tipica': '±2%'},
    
    # Instrumentos de Peso
    'WI': {'variable': 'Peso', 'funcion': 'Indicador', 'rango_tipico': '0-10000 kg', 'exactitud_tipica': '±0.1%'},
    'WIT': {'variable': 'Peso', 'funcion': 'Indicador-Transmisor', 'rango_tipico': '0-50000 kg', 'exactitud_tipica': '±0.05%'},
    'WT': {'variable': 'Peso', 'funcion': 'Transmisor', 'rango_tipico': '0-100000 kg', 'exactitud_tipica': '±0.03%'},
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

def select_instrument_for_measurement(variable_type, measurement_value, accuracy_required=True):
    """Selecciona el instrumento adecuado basado en la variable y exactitud requerida."""
    suitable_instruments = []
    
    for tag, specs in INSTRUMENT_DATABASE.items():
        if variable_type.lower() in specs['variable'].lower():
            # Para medición con exactitud, el valor debe estar en el 50% del campo de indicación
            if accuracy_required:
                # Extraer rango numérico del rango típico
                range_match = re.search(r'(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)', specs['rango_tipico'])
                if range_match:
                    min_range, max_range = float(range_match.group(1)), float(range_match.group(2))
                    optimal_range = (max_range - min_range) * 0.5 + min_range
                    
                    # Verificar si el valor a medir está cerca del 50% del rango
                    if abs(measurement_value - optimal_range) / optimal_range <= 0.3:  # ±30% del punto óptimo
                        suitable_instruments.append((tag, specs))
            else:
                suitable_instruments.append((tag, specs))
    
    return suitable_instruments

def calculate_measurement_errors(instrument_tag, measurement_value, error_percentages):
    """Calcula los diferentes tipos de error para un instrumento dado."""
    if instrument_tag not in INSTRUMENT_DATABASE:
        return None
    
    specs = INSTRUMENT_DATABASE[instrument_tag]
    
    # Extraer rango del instrumento
    range_match = re.search(r'(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)', specs['rango_tipico'])
    if not range_match:
        return None
    
    min_range, max_range = float(range_match.group(1)), float(range_match.group(2))
    span = max_range - min_range
    
    errors = {}
    
    # Error Tipo A: % del máximo valor del campo de indicación
    errors['A'] = (error_percentages['A'] / 100) * max_range
    
    # Error Tipo B: % del span
    errors['B'] = (error_percentages['B'] / 100) * span
    
    # Error Tipo C: % del valor a medir
    errors['C'] = (error_percentages['C'] / 100) * measurement_value
    
    # Error Tipo D: Valor fijo (depende de la variable)
    if 'temperatura' in specs['variable'].lower():
        errors['D'] = error_percentages['D']  # En °C
    elif 'presión' in specs['variable'].lower():
        errors['D'] = error_percentages['D']  # En unidades de presión
    else:
        errors['D'] = error_percentages['D']  # Valor genérico
    
    return errors, specs

# --- FUNCIONES PARA EL CENTRO DE PRÁCTICA (EXPANDIDAS) ---

def generate_scaling_quiz():
    """Genera un ejercicio de escalamiento aleatorio."""
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
    """Genera un ejercicio de identificación de tags ISA-5.1."""
    first = random.choice(list(FIRST_LETTER.keys()))
    successors = random.sample(list(SUCCESSOR_LETTERS.keys()), random.randint(1, 2))
    tag = f"{first}{''.join(successors)}-{random.randint(100,999)}"
    
    question = f"¿Qué significa el tag **{tag}** según ISA-5.1?"
    
    # Respuesta Correcta
    desc = [FIRST_LETTER[first]]
    for letter in successors:
        desc.append(SUCCESSOR_LETTERS[letter])
    correct_answer = " - ".join(desc)
    
    # Distractores
    options = {correct_answer}
    while len(options) < 4:
        w_first = random.choice(list(FIRST_LETTER.values()))
        w_succ = random.sample(list(SUCCESSOR_LETTERS.values()), len(successors))
        distractor = f"{w_first} - {' - '.join(w_succ)}"
        if distractor != correct_answer:
            options.add(distractor)
            
    return question, list(options), correct_answer

def generate_error_quiz():
    """Genera un ejercicio de selección de instrumentos y cálculo de errores."""
    variables = ['Presión', 'Temperatura', 'Nivel', 'Caudal']
    variable = random.choice(variables)
    
    # Generar valor a medir
    if variable == 'Presión':
        measurement_value = round(random.uniform(5, 15), 1)
        unit = 'bar'
    elif variable == 'Temperatura':
        measurement_value = round(random.uniform(100, 400), 0)
        unit = '°C'
    elif variable == 'Nivel':
        measurement_value = round(random.uniform(2, 8), 1)
        unit = 'm'
    else:  # Caudal
        measurement_value = round(random.uniform(50, 500), 0)
        unit = 'm³/h'
    
    # Seleccionar instrumento adecuado
    suitable_instruments = select_instrument_for_measurement(variable, measurement_value, accuracy_required=True)
    
    if not suitable_instruments:
        # Fallback a cualquier instrumento de la variable
        suitable_instruments = select_instrument_for_measurement(variable, measurement_value, accuracy_required=False)
    
    if suitable_instruments:
        selected_instrument = random.choice(suitable_instruments)
        instrument_tag = selected_instrument[0]
        
        question = f"Para medir **{measurement_value} {unit}** de {variable.lower()} con exactitud (valor al 50% del campo de indicación), ¿qué instrumento sería el más adecuado?"
        
        # Generar opciones
        correct_answer = f"{instrument_tag} - {selected_instrument[1]['variable']} {selected_instrument[1]['funcion']}"
        
        options = {correct_answer}
        # Agregar distractores de otros instrumentos
        all_instruments = list(INSTRUMENT_DATABASE.keys())
        while len(options) < 4:
            distractor_tag = random.choice(all_instruments)
            distractor_specs = INSTRUMENT_DATABASE[distractor_tag]
            distractor = f"{distractor_tag} - {distractor_specs['variable']} {distractor_specs['funcion']}"
            if distractor != correct_answer:
                options.add(distractor)
        
        return question, list(options), correct_answer, instrument_tag, measurement_value
    
    return None, None, None, None, None

# --- INTERFAZ DE USUARIO (UI) ---

st.title("🛠️ Asistente de Instrumentación Industrial v7.0 - Expandido")
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
    
    # Mostrar algunos instrumentos comunes
    st.subheader("🔧 Instrumentos Comunes")
    common_instruments = ['PIT', 'TIT', 'FIT', 'LIT', 'PDT', 'TT', 'FT', 'LT']
    selected_inst = st.selectbox("Ver especificaciones:", common_instruments)
    if selected_inst in INSTRUMENT_DATABASE:
        specs = INSTRUMENT_DATABASE[selected_inst]
        st.write(f"**{specs['variable']}** - {specs['funcion']}")
        st.write(f"Rango típico: {specs['rango_tipico']}")
        st.write(f"Exactitud típica: {specs['exactitud_tipica']}")


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
            
            # Tabla de calibración/verificación personalizable
            st.subheader("📊 Tabla de Puntos de Verificación Personalizada")
            table_data = {
                "Porcentaje (%)": custom_percentages,
                f"Variable de Proceso ({pv_units})": [lrv_pv + (p/100) * span_pv for p in custom_percentages],
                f"Señal de Salida ({out_units})": [lrv_out + (p/100) * span_out for p in custom_percentages]
            }
            df = pd.DataFrame(table_data)
            st.dataframe(df.style.format({df.columns[1]: "{:.2f}", df.columns[2]: "{:.2f}"}), use_container_width=True)
            
            # Información adicional sobre el campo de medida
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
            if error_msg:
                st.error(error_msg)
            else:
                st.metric("Coeficiente de Válvula Requerido (Cv)", f"{cv}")
                st.info(f"Seleccione una válvula con un Cv nominal mayor a **{cv}**. Se recomienda que este valor esté entre el 20% y 80% del rango de operación de la válvula seleccionada.")

    with st.expander("**🎛️ Calculadora de Caudal por Placa de Orificio**"):
        st.latex(r"Q = K \sqrt{\Delta P}")
        k_factor = st.number_input("Factor K del Medidor", value=50.0, format="%.3f", help="Este factor depende de la geometría de la tubería, la placa y las propiedades del fluido.")
        delta_p = st.number_input("Presión Diferencial (ΔP) [inH2O]", value=100.0, format="%.2f")
        
        if st.button("Calcular Caudal"):
            flow, error_msg = calculate_orifice_flow(delta_p, k_factor)
            if error_msg:
                st.error(error_msg)
            else:
                st.metric("Caudal Calculado (Q)", f"{flow} unidades de caudal")

with tab2:
    st.header("📖 Interpretador de Tags de Instrumentación (ISA-5.1)")
    st.info("Introduce un tag de instrumento (ej: `TIC-101`, `PDT-50A`, `LSHH-203`) para ver su significado desglosado según la norma ISA-5.1.")
    
    tag_input = st.text_input("**Introduce el Tag del Instrumento:**", "TIC-101A").upper()
    
    if tag_input:
        # Regex para parsear el tag de forma flexible (hasta 3 letras)
        match = re.match(r'^([A-Z]{1,3})(\d+)([A-Z]*)$', tag_input.replace('-', ''))
        
        if match:
            letters, loop_num, suffix = match.groups()
            
            st.subheader(f"Análisis del Tag: **{tag_input}**")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Identificación de Letras", letters)
            c2.metric("Número de Lazo", loop_num)
            c3.metric("Sufijo (si aplica)", suffix if suffix else "N/A")
            
            st.markdown("---")
            
            descriptions = []
            # Primera Letra
            first_letter = letters[0]
            if first_letter in FIRST_LETTER:
                descriptions.append(f"**{first_letter}** (Primera Letra): **{FIRST_LETTER[first_letter]}**. Esta es la variable medida o iniciadora del lazo de control.")
            else:
                descriptions.append(f"**{first_letter}**: Letra desconocida.")
                
            # Letras Sucesivas (hasta 3 letras total)
            for i, letter in enumerate(letters[1:]):
                if letter in SUCCESSOR_LETTERS:
                    descriptions.append(f"**{letter}** (Letra Sucesiva {i+1}): **{SUCCESSOR_LETTERS[letter]}**. Describe la función del instrumento en el lazo.")
                else:
                    descriptions.append(f"**{letter}**: Letra desconocida.")
            
            for desc in descriptions:
                st.markdown(f"<li>{desc}</li>", unsafe_allow_html=True)

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
    
    quiz_type = st.radio("Elige qué tema quieres practicar:", [
        "Ejercicios de Escalamiento", 
        "Identificación de Tags (ISA-5.1)",
        "Selección de Instrumentos y Análisis de Errores"
    ], horizontal=True)

    # --- CORRECCIÓN: Gestión de estado para evitar bugs en los quizzes ---
    if 'quiz_id' not in st.session_state:
        st.session_state.quiz_id = 0
    if 'quiz_stats' not in st.session_state:
        st.session_state.quiz_stats = {'correct': 0, 'total': 0}
    
    # Mostrar estadísticas
    if st.session_state.quiz_stats['total'] > 0:
        accuracy = (st.session_state.quiz_stats['correct'] / st.session_state.quiz_stats['total']) * 100
        st.metric("📈 Tu Rendimiento General", f"{accuracy:.1f}%", 
                 delta=f"{st.session_state.quiz_stats['correct']} de {st.session_state.quiz_stats['total']} correctas")
    st.divider()

    # Generación y lógica del quiz
    quiz_key_prefix = ""
    generator_func = None
    
    if "Escalamiento" in quiz_type:
        st.subheader("📐 Problema de Escalamiento")
        quiz_key_prefix = "scaling"
        generator_func = generate_scaling_quiz
    elif "Tags" in quiz_type:
        st.subheader("🏷️ Problema de Identificación ISA-5.1")
        quiz_key_prefix = "tag"
        generator_func = generate_tag_quiz
    elif "Selección de Instrumentos" in quiz_type:
        st.subheader("⚠️ Problema de Selección de Instrumentos y Errores")
        quiz_key_prefix = "error"
        generator_func = generate_error_quiz

    # Generar nueva pregunta si no existe
    question_state_key = f"{quiz_key_prefix}_question"
    if question_state_key not in st.session_state:
        if quiz_key_prefix == "error":
            result = generator_func()
            if result[0] is not None:  # Si se generó correctamente
                st.session_state[question_state_key] = result
            else:
                st.error("No se pudo generar el ejercicio. Intente de nuevo.")
        else:
            st.session_state[question_state_key] = generator_func()
    
    if question_state_key in st.session_state:
        if quiz_key_prefix == "error":
            question, options, correct_answer, instrument_tag, measurement_value = st.session_state[question_state_key]
        else:
            question, options, correct_answer = st.session_state[question_state_key]
            instrument_tag, measurement_value = None, None
        
        if options:
            random.shuffle(options)
            
            # Widget de respuesta con llave única
            user_answer = st.radio(f"**Problema:** {question}", options, key=f"{quiz_key_prefix}_{st.session_state.quiz_id}")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1,1,2])
            
            if col_btn1.button("✅ Verificar Respuesta", key=f"verify_{quiz_key_prefix}"):
                st.session_state.quiz_stats['total'] += 1
                if user_answer == correct_answer:
                    st.session_state.quiz_stats['correct'] += 1
                    st.markdown('<div class="success-box">🎉 ¡Correcto! Excelente trabajo.</div>', unsafe_allow_html=True)
                    
                    if quiz_key_prefix == "error" and instrument_tag:
                        specs = INSTRUMENT_DATABASE[instrument_tag]
                        st.info(f"**Información del instrumento seleccionado:**\n- Rango: {specs['rango_tipico']}\n- Exactitud: {specs['exactitud_tipica']}")
                else:
                    st.markdown(f'<div class="error-box">❌ Incorrecto. La respuesta correcta es: **{correct_answer}**</div>', unsafe_allow_html=True)
                    
            if col_btn2.button("➡️ Siguiente Ejercicio", key=f"next_{quiz_key_prefix}"):
                if quiz_key_prefix == "error":
                    result = generator_func()
                    if result[0] is not None:
                        st.session_state[question_state_key] = result
                else:
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
        if result is not None:
            st.metric(f"Resultado en {temp_to}", f"{result}")

    with c2:
        st.subheader("📊 Conversor de Presión")
        press_val = st.number_input("Valor Presión", value=1.0, format="%.3f")
        press_from = st.selectbox("De:", ('bar', 'psi', 'kPa', 'kg/cm²', 'atm', 'mmH2O', 'inH2O'))
        press_to = st.selectbox("A:", ('psi', 'bar', 'kPa', 'kg/cm²', 'atm', 'mmH2O', 'inH2O'))
        result = convert_pressure(press_val, press_from, press_to)
        if result is not None:
            st.metric(f"Resultado en {press_to}", f"{result:.4f}")

with tab5:
    st.header("⚠️ Análisis Guiado de Errores de Instrumentación")
    st.info("Selecciona o define un instrumento personalizado para calcular los diferentes tipos de error (A, B, C, D) según las especificaciones del fabricante.")
    
    with st.expander("**🎯 Análisis Guiado de Errores**", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Configuración del Instrumento")
            
            instrument_source = st.radio("Fuente del instrumento:", 
                                       ["Base de datos", "Instrumento personalizado"], 
                                       horizontal=True)
            
            if instrument_source == "Base de datos":
                selected_instrument = st.selectbox("Instrumento de la base de datos:", 
                                                 list(INSTRUMENT_DATABASE.keys()))
                if selected_instrument in INSTRUMENT_DATABASE:
                    specs = INSTRUMENT_DATABASE[selected_instrument]
                    st.write(f"**Variable:** {specs['variable']}")
                    st.write(f"**Función:** {specs['funcion']}")
                    
                    range_match = re.search(r'(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)', specs['rango_tipico'])
                    if range_match:
                        default_min, default_max = float(range_match.group(1)), float(range_match.group(2))
                    else:
                        default_min, default_max = 0.0, 100.0
                    
                    st.subheader("Campo de Indicación (Editable)")
                    min_range = st.number_input("Valor mínimo del campo:", value=default_min, format="%.2f")
                    max_range = st.number_input("Valor máximo del campo:", value=default_max, format="%.2f")
                    
                    if max_range > min_range:
                        span = max_range - min_range
                        st.metric("📏 Span del Instrumento", f"{span:.2f}", 
                                help="Span = Valor máximo - Valor mínimo del campo de indicación")
                        optimal_point = min_range + (span * 0.5)
                        st.info(f"🎯 **Punto óptimo para máxima exactitud:** {optimal_point:.2f} (50% del campo)")
                    else:
                        st.error("El valor máximo debe ser mayor que el mínimo")
                        
            else:  # Instrumento personalizado
                st.subheader("Definir Instrumento Personalizado")
                custom_variable = st.text_input("Variable medida:", "Presión")
                custom_function = st.text_input("Función del instrumento:", "Transmisor")
                custom_units = st.text_input("Unidades:", "bar")
                
                st.subheader("Campo de Indicación")
                min_range = st.number_input("Valor mínimo del campo:", value=0.0, format="%.2f")
                max_range = st.number_input("Valor máximo del campo:", value=100.0, format="%.2f")
                
                if max_range > min_range:
                    span = max_range - min_range
                    st.metric("📏 Span del Instrumento", f"{span:.2f} {custom_units}", 
                            help="Span = Valor máximo - Valor mínimo del campo de indicación")
                    optimal_point = min_range + (span * 0.5)
                    st.info(f"🎯 **Punto óptimo para máxima exactitud:** {optimal_point:.2f} {custom_units} (50% del campo)")
                else:
                    st.error("El valor máximo debe ser mayor que el mínimo")
            
            measurement_val = st.number_input("Valor a medir:", value=50.0, format="%.2f")
            
            if max_range > min_range:
                measurement_percentage = ((measurement_val - min_range) / span) * 100
                if 40 <= measurement_percentage <= 60:
                    st.success(f"✅ Medición con exactitud: {measurement_percentage:.1f}% del campo (cerca del 50% óptimo)")
                else:
                    st.warning(f"⚠️ Medición sin exactitud óptima: {measurement_percentage:.1f}% del campo (alejado del 50% óptimo)")
        
        with col2:
            st.subheader("Especificaciones de Error del Fabricante")
            st.write("*Configure los porcentajes según las especificaciones del fabricante:*")
            
            error_a = st.number_input("Error Tipo A (% del máximo del campo):", value=0.5, format="%.3f", 
                                    help="Porcentaje del valor máximo del campo de indicación")
            error_b = st.number_input("Error Tipo B (% del span):", value=0.25, format="%.3f", 
                                    help="Porcentaje del span (rango completo)")
            error_c = st.number_input("Error Tipo C (% del valor medido):", value=1.0, format="%.3f", 
                                    help="Porcentaje del valor que se está midiendo")
            error_d = st.number_input("Error Tipo D (valor fijo):", value=0.1, format="%.3f", 
                                    help="Valor fijo según la variable (°C, bar, etc.)")
        
        if st.button("🧮 Calcular Errores") and max_range > min_range:
            span = max_range - min_range
            
            # Calculate errors
            errors = {}
            errors['A'] = (error_a / 100) * max_range
            errors['B'] = (error_b / 100) * span
            errors['C'] = (error_c / 100) * measurement_val
            errors['D'] = error_d
            
            st.subheader("📊 Resultados del Análisis de Errores")
            
            # Display instrument info
            if instrument_source == "Base de datos":
                st.info(f"**Instrumento:** {selected_instrument} - {specs['variable']} {specs['funcion']}")
            else:
                st.info(f"**Instrumento personalizado:** {custom_variable} {custom_function}")
            
            st.write(f"**Campo de indicación:** {min_range:.2f} a {max_range:.2f}")
            st.write(f"**Span:** {span:.2f}")
            st.write(f"**Valor a medir:** {measurement_val:.2f}")
            
            # Create results table
            error_data = {
                'Tipo de Error': ['A - % del máximo', 'B - % del span', 'C - % del valor medido', 'D - Valor fijo'],
                'Descripción': [
                    ERROR_TYPES['A'],
                    ERROR_TYPES['B'], 
                    ERROR_TYPES['C'],
                    ERROR_TYPES['D']
                ],
                'Configuración': [
                    f"±{error_a}% de {max_range:.2f}",
                    f"±{error_b}% de {span:.2f}",
                    f"±{error_c}% de {measurement_val:.2f}",
                    f"±{error_d:.3f} (fijo)"
                ],
                'Error Calculado': [
                    f"±{errors['A']:.3f}",
                    f"±{errors['B']:.3f}",
                    f"±{errors['C']:.3f}",
                    f"±{errors['D']:.3f}"
                ]
            }
            
            df_errors = pd.DataFrame(error_data)
            st.dataframe(df_errors, use_container_width=True)
            
            # Show most critical error
            max_error = max(errors.values())
            max_error_type = [k for k, v in errors.items() if v == max_error][0]
            
            st.warning(f"⚠️ **Error más crítico:** Tipo {max_error_type} con ±{max_error:.3f} unidades")
            
            # Show measurement assessment
            measurement_percentage = ((measurement_val - min_range) / span) * 100
            if 40 <= measurement_percentage <= 60:
                st.success(f"✅ **Medición óptima:** El valor está en el {measurement_percentage:.1f}% del campo (zona de máxima exactitud)")
            else:
                optimal_value = min_range + (span * 0.5)
                st.warning(f"⚠️ **Recomendación:** Para máxima exactitud, mida cerca de {optimal_value:.2f} (50% del campo)")

    with st.expander("**📚 Guía de Tipos de Error**"):
        st.markdown("""
        ### Tipos de Error en Instrumentación
        
        **Error Tipo A - Porcentaje del máximo valor del campo de indicación:**
        - Se calcula como un porcentaje del valor máximo que puede indicar el instrumento
        - Ejemplo: ±0.5% de 100 bar = ±0.5 bar (constante en todo el rango)
        
        **Error Tipo B - Porcentaje del span (rango):**
        - Se calcula como un porcentaje del span completo del instrumento
        - Ejemplo: ±0.25% de span de 0-100 bar = ±0.25 bar
        
        **Error Tipo C - Porcentaje del valor a medir:**
        - Se calcula como un porcentaje del valor que se está midiendo actualmente
        - Ejemplo: ±1% de 50 bar = ±0.5 bar (varía según el valor medido)
        
        **Error Tipo D - Valor fijo:**
        - Error constante independiente del valor medido
        - Ejemplo: ±0.1°C para temperatura, ±0.01 bar para presión
        
        ### 💡 Recomendaciones:
        - Para máxima exactitud, opere el instrumento cerca del 50% de su rango
        - El error tipo C es más favorable para mediciones de valores altos
        - Los errores tipo A y B son constantes en todo el rango
        """)

with tab3:
    st.header("🧠 Centro de Práctica y Autoevaluación")
    st.info("Pon a prueba tus conocimientos con ejercicios generados aleatoriamente. ¡Nunca verás dos veces el mismo problema!")
    
    quiz_type = st.radio("Elige qué tema quieres practicar:", [
        "Ejercicios de Escalamiento", 
        "Identificación de Tags (ISA-5.1)",
        "Selección de Instrumentos y Análisis de Errores"
    ], horizontal=True)

    if 'current_quiz_type' not in st.session_state:
        st.session_state.current_quiz_type = quiz_type
    if 'quiz_counter' not in st.session_state:
        st.session_state.quiz_counter = 0
    if 'quiz_stats' not in st.session_state:
        st.session_state.quiz_stats = {'correct': 0, 'total': 0}
    if 'current_question_data' not in st.session_state:
        st.session_state.current_question_data = None
    if 'answer_submitted' not in st.session_state:
        st.session_state.answer_submitted = False
    
    # Reset if quiz type changed
    if st.session_state.current_quiz_type != quiz_type:
        st.session_state.current_quiz_type = quiz_type
        st.session_state.current_question_data = None
        st.session_state.answer_submitted = False
        st.session_state.quiz_counter += 1
    
    # Show statistics
    if st.session_state.quiz_stats['total'] > 0:
        accuracy = (st.session_state.quiz_stats['correct'] / st.session_state.quiz_stats['total']) * 100
        st.metric("📈 Tu Rendimiento General", f"{accuracy:.1f}%", 
                 delta=f"{st.session_state.quiz_stats['correct']} de {st.session_state.quiz_stats['total']} correctas")
    st.divider()

    # Generate question if needed
    if st.session_state.current_question_data is None:
        if "Escalamiento" in quiz_type:
            st.session_state.current_question_data = generate_scaling_quiz()
        elif "Tags" in quiz_type:
            st.session_state.current_question_data = generate_tag_quiz()
        elif "Selección de Instrumentos" in quiz_type:
            result = generate_error_quiz()
            if result[0] is not None:
                st.session_state.current_question_data = result
            else:
                st.error("No se pudo generar el ejercicio. Intente de nuevo.")
                st.session_state.current_question_data = None

    # Display question
    if st.session_state.current_question_data:
        if "Escalamiento" in quiz_type:
            st.subheader("📐 Problema de Escalamiento")
            question, options, correct_answer = st.session_state.current_question_data
        elif "Tags" in quiz_type:
            st.subheader("🏷️ Problema de Identificación ISA-5.1")
            question, options, correct_answer = st.session_state.current_question_data
        elif "Selección de Instrumentos" in quiz_type:
            st.subheader("⚠️ Problema de Selección de Instrumentos y Errores")
            question, options, correct_answer, instrument_tag, measurement_value = st.session_state.current_question_data
        
        if options:
            unique_key = f"quiz_answer_{st.session_state.quiz_counter}_{quiz_type.replace(' ', '_')}"
            user_answer = st.radio(f"**Problema:** {question}", options, key=unique_key)
            
            col_btn1, col_btn2, col_btn3 = st.columns([1,1,2])
            
            if col_btn1.button("✅ Verificar Respuesta", key=f"verify_{st.session_state.quiz_counter}"):
                if not st.session_state.answer_submitted:
                    st.session_state.quiz_stats['total'] += 1
                    st.session_state.answer_submitted = True
                    
                    if user_answer == correct_answer:
                        st.session_state.quiz_stats['correct'] += 1
                        st.markdown('<div class="success-box">🎉 ¡Correcto! Excelente trabajo.</div>', unsafe_allow_html=True)
                        
                        # Show additional info for error exercises
                        if "Selección de Instrumentos" in quiz_type and 'instrument_tag' in locals():
                            if instrument_tag and instrument_tag in INSTRUMENT_DATABASE:
                                specs = INSTRUMENT_DATABASE[instrument_tag]
                                st.info(f"**Información del instrumento seleccionado:**\n- Rango: {specs['rango_tipico']}\n- Exactitud: {specs['exactitud_tipica']}")
                    else:
                        st.markdown(f'<div class="error-box">❌ Incorrecto. La respuesta correcta es: **{correct_answer}**</div>', unsafe_allow_html=True)
                else:
                    st.info("Ya has verificado esta respuesta. Genera un nuevo ejercicio.")
                    
            if col_btn2.button("➡️ Siguiente Ejercicio", key=f"next_{st.session_state.quiz_counter}"):
                st.session_state.current_question_data = None
                st.session_state.answer_submitted = False
                st.session_state.quiz_counter += 1
                st.rerun()

st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <h4>🛠️ Asistente de Instrumentación Industrial v7.0 - Expandido</h4>
    <p>Desarrollado para ingenieros y técnicos de instrumentación y control | Basado en estándares ISA</p>
    <p><em>Mejoras v7.0: Base de datos expandida con más instrumentos, tabla de calibración personalizable, ejercicios de selección de instrumentos y análisis completo de errores tipo A, B, C y D.</em></p>
</div>
""", unsafe_allow_html=True)
