import streamlit as st
import random
import pandas as pd
import math
import re

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Asistente de Instrumentación v6.0 JR",
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
</style>
""", unsafe_allow_html=True)

# --- BASES DE DATOS (DICCIONARIOS ISA-5.1) ---

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

# --- FUNCIONES PARA EL CENTRO DE PRÁCTICA (CON CORRECCIONES) ---

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


# --- INTERFAZ DE USUARIO (UI) ---

st.title("🛠️ Asistente de Instrumentación Industrial v6.0")
st.markdown("*Herramienta avanzada para cálculos, interpretación de normas y práctica profesional*")

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
    ]
    if 'tip_index' not in st.session_state:
        st.session_state.tip_index = 0
    st.info(f"💡 {tips[st.session_state.tip_index]}")
    if st.button("Siguiente Tip 💡"):
        st.session_state.tip_index = (st.session_state.tip_index + 1) % len(tips)
        st.rerun()

    st.divider()
    st.header("📋 Referencia Rápida ISA-5.1")
    st.selectbox("Primera Letra (Variable)", options=list(FIRST_LETTER.items()), format_func=lambda x: f"{x[0]} - {x[1]}")
    st.selectbox("Letras Sucesivas (Función)", options=list(SUCCESSOR_LETTERS.items()), format_func=lambda x: f"{x[0]} - {x[1]}")


tab1, tab2, tab3, tab4 = st.tabs(["**📐 Herramientas de Cálculo**", "**📖 Interpretador ISA-5.1**", "**🧠 Centro de Práctica**", "**🔧 Conversores de Unidades**"])

with tab1:
    st.header("Cálculos Fundamentales de Instrumentación")
    
    with st.expander("**📈 Calculadora de Escalamiento y Tabla de Calibración**", expanded=True):
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
        
        st.divider()
        if urv_pv > lrv_pv and urv_out > lrv_out:
            span_pv = urv_pv - lrv_pv
            span_out = urv_out - lrv_out
            
            # Tabla de calibración/verificación
            st.subheader("📊 Tabla de Puntos de Verificación")
            percentages = [0, 25, 50, 75, 100]
            table_data = {
                "Porcentaje (%)": percentages,
                f"Variable de Proceso ({pv_units})": [lrv_pv + (p/100) * span_pv for p in percentages],
                f"Señal de Salida ({out_units})": [lrv_out + (p/100) * span_out for p in percentages]
            }
            df = pd.DataFrame(table_data)
            st.dataframe(df.style.format({df.columns[1]: "{:.2f}", df.columns[2]: "{:.2f}"}), use_container_width=True)
            
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
        # Regex para parsear el tag de forma flexible
        match = re.match(r'^([A-Z]+)(\d+)([A-Z]*)$', tag_input.replace('-', ''))
        
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
                
            # Letras Sucesivas
            for i, letter in enumerate(letters[1:]):
                if letter in SUCCESSOR_LETTERS:
                    descriptions.append(f"**{letter}** (Letra Sucesiva {i+1}): **{SUCCESSOR_LETTERS[letter]}**. Describe la función del instrumento en el lazo.")
                else:
                    descriptions.append(f"**{letter}**: Letra desconocida.")
            
            for desc in descriptions:
                st.markdown(f"<li>{desc}</li>", unsafe_allow_html=True)

            st.markdown("---")
            st.success(f"**Resumen:** El tag **{tag_input}** representa un instrumento en el lazo de control **{loop_num}** que se encarga de las funciones de **{' y '.join([SUCCESSOR_LETTERS.get(l, 'Función Desconocida') for l in letters[1:]])}** para la variable de **{FIRST_LETTER.get(first_letter, 'Variable Desconocida')}**.")

        else:
            st.warning("Formato de tag no reconocido. Por favor, use un formato como 'TIC101' o 'FT-205B'.")

with tab3:
    st.header("🧠 Centro de Práctica y Autoevaluación")
    st.info("Pon a prueba tus conocimientos con ejercicios generados aleatoriamente. ¡Nunca verás dos veces el mismo problema!")
    
    quiz_type = st.radio("Elige qué tema quieres practicar:", [
        "Ejercicios de Escalamiento", 
        "Identificación de Tags (ISA-5.1)"
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

    # Generar nueva pregunta si no existe
    question_state_key = f"{quiz_key_prefix}_question"
    if question_state_key not in st.session_state:
        st.session_state[question_state_key] = generator_func()
    
    question, options, correct_answer = st.session_state[question_state_key]
    random.shuffle(options)
    
    # Widget de respuesta con llave única
    user_answer = st.radio(f"**Problema:** {question}", options, key=f"{quiz_key_prefix}_{st.session_state.quiz_id}")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1,1,2])
    
    if col_btn1.button("✅ Verificar Respuesta", key=f"verify_{quiz_key_prefix}"):
        st.session_state.quiz_stats['total'] += 1
        if user_answer == correct_answer:
            st.session_state.quiz_stats['correct'] += 1
            st.markdown('<div class="success-box">🎉 ¡Correcto! Excelente trabajo.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-box">❌ Incorrecto. La respuesta correcta es: **{correct_answer}**</div>', unsafe_allow_html=True)
            
    if col_btn2.button("➡️ Siguiente Ejercicio", key=f"next_{quiz_key_prefix}"):
        st.session_state[question_state_key] = generator_func()
        st.session_state.quiz_id += 1 # Clave para la corrección del bug
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

st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <h4>🛠️ Asistente de Instrumentación Industrial v6.0</h4>
    <p>Desarrollado para ingenieros y técnicos de instrumentación y control | Basado en estándares ISA</p>
    <p><em>Mejoras v6.0: Calculadoras de Cv y Placa de Orificio, Interpretador de Tags ISA-5.1, Corrección de bugs y Tabla de Calibración.</em></p>
</div>
""", unsafe_allow_html=True)
