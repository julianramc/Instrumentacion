# app_instrumentacion.py
import streamlit as st
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Asistente de Instrumentación Industrial",
    page_icon="⚙️",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- BASE DE DATOS Y LÓGICA (DICCIONARIOS ISA-5.1) ---

# Mapeo de la primera letra (Variable de Proceso)
FIRST_LETTER = {
    'A': 'Análisis', 'B': 'Llama (Burner)', 'C': 'Conductividad', 'D': 'Densidad o Peso Específico',
    'E': 'Tensión (Voltaje)', 'F': 'Caudal (Flow)', 'H': 'Manual (Hand)', 'I': 'Corriente Eléctrica',
    'J': 'Potencia', 'K': 'Tiempo', 'L': 'Nivel (Level)', 'M': 'Humedad (Moisture)',
    'P': 'Presión', 'Q': 'Cantidad', 'R': 'Radiactividad', 'S': 'Velocidad o Frecuencia',
    'T': 'Temperatura', 'V': 'Vibración', 'W': 'Peso o Fuerza', 'Y': 'Evento o Estado', 'Z': 'Posición'
}

# Mapeo de letras sucesivas (Función del Instrumento)
SUCCESSOR_LETTERS = {
    'A': 'Alarma', 'C': 'Controlador', 'E': 'Elemento Primario (Sensor)', 'H': 'Alto (High)',
    'I': 'Indicador', 'L': 'Luz Piloto o Bajo (Low)', 'R': 'Registrador (Recorder)',
    'S': 'Interruptor (Switch)', 'T': 'Transmisor', 'V': 'Válvula, Damper o Actuador',
    'Y': 'Relé o Convertidor', 'Z': 'Elemento Final de Control (No clasificado)'
}

# Símbolos gráficos para algunos instrumentos comunes
INSTRUMENT_IMAGES = {
    "PT": "https://i.imgur.com/8f7pYJv.png",
    "TT": "https://i.imgur.com/1B9Z1hZ.png",
    "LT": "https://i.imgur.com/v8gqNfQ.png",
    "FT": "https://i.imgur.com/E0b9m0O.png",
    "PIC": "https://i.imgur.com/3jL2r8E.png",
    "TIC": "https://i.imgur.com/TfS036p.png",
    "LIC": "https://i.imgur.com/s6n5F7T.png",
    "FIC": "https://i.imgur.com/2sO9qP3.png",
    "LSH": "https://i.imgur.com/uStyP5a.png",
    "PSV": "https://i.imgur.com/nJhA0yH.png",
    "GENERIC": "https://i.imgur.com/Cbn55Od.png" # Círculo genérico
}

def get_instrument_description(tag):
    """Interpreta un tag de instrumento según la norma ISA-5.1."""
    if not tag or not tag.isalpha():
        return "El tag debe contener solo letras."
    
    tag = tag.upper()
    first = tag[0]
    successors = tag[1:]
    
    if first not in FIRST_LETTER:
        return f"La primera letra '{first}' no corresponde a una variable de proceso válida."
    
    desc = f"**Variable Principal:** {FIRST_LETTER[first]}\n"
    
    functions = []
    for letter in successors:
        if letter in SUCCESSOR_LETTERS:
            functions.append(SUCCESSOR_LETTERS[letter])
        else:
            functions.append(f"Función Desconocida ('{letter}')")
    
    desc += f"**Funciones:** {', '.join(functions)}"
    
    # Combinación común para el nombre
    full_name = ""
    if 'T' in successors and 'I' in successors and 'C' in successors:
        full_name = f"Controlador Indicador y Transmisor de {FIRST_LETTER[first]}"
    elif 'I' in successors and 'C' in successors:
        full_name = f"Controlador con Indicador de {FIRST_LETTER[first]}"
    elif 'T' in successors:
        full_name = f"Transmisor de {FIRST_LETTER[first]}"
    elif 'I' in successors:
        full_name = f"Indicador de {FIRST_LETTER[first]}"
    elif 'C' in successors:
        full_name = f"Controlador de {FIRST_LETTER[first]}"
    elif 'S' in successors:
        full_name = f"Interruptor (Switch) de {FIRST_LETTER[first]}"
        if 'H' in successors:
            full_name += " por Alto Nivel"
        if 'L' in successors:
            full_name += " por Bajo Nivel"
            
    if full_name:
        return f"**Nombre Común:** {full_name}\n\n**Desglose:**\n- **{first}:** {FIRST_LETTER[first]}\n- **{'/'.join(successors)}:** {', '.join(functions)}"
    
    return desc

def generate_isa_quiz():
    """Genera una pregunta de examen para identificación de instrumentos."""
    # Elige una variable y una función al azar
    correct_var_code = random.choice(list(FIRST_LETTER.keys()))
    correct_func_code = random.choice(['T', 'I', 'C', 'S'])
    
    correct_tag = correct_var_code + correct_func_code
    correct_desc = f"{SUCCESSOR_LETTERS[correct_func_code]} de {FIRST_LETTER[correct_var_code]}"
    
    options = {correct_tag}
    while len(options) < 4:
        # Generar opciones incorrectas
        wrong_var = random.choice(list(FIRST_LETTER.keys()))
        wrong_func = random.choice(list(SUCCESSOR_LETTERS.keys()))
        wrong_tag = wrong_var + wrong_func
        if wrong_tag != correct_tag:
            options.add(wrong_tag)
            
    return correct_desc, list(options), correct_tag

def generate_scaling_quiz():
    """Genera un ejercicio de examen para cálculos de escalamiento."""
    # Seleccionar tipo de señal
    signal_type = random.choice([
        {'name': 'Corriente', 'units': 'mA', 'lrv': 4, 'urv': 20},
        {'name': 'Voltaje', 'units': 'V', 'lrv': 1, 'urv': 5},
        {'name': 'Neumática', 'units': 'psi', 'lrv': 3, 'urv': 15}
    ])
    
    # Seleccionar variable de proceso
    pv_type = random.choice([
        {'name': 'Presión', 'units': 'kPa', 'min': 0, 'max': 500},
        {'name': 'Temperatura', 'units': '°C', 'min': -20, 'max': 200},
        {'name': 'Nivel', 'units': '%', 'min': 0, 'max': 100},
        {'name': 'Caudal', 'units': 'L/min', 'min': 10, 'max': 1000}
    ])
    
    lrv_pv = round(random.uniform(pv_type['min'], pv_type['max'] / 2), 2)
    urv_pv = round(random.uniform(lrv_pv + 10, pv_type['max']), 2)
    
    # Elegir un punto a calcular
    percentage = random.choice([25, 50, 75])
    pv_in = lrv_pv + (urv_pv - lrv_pv) * (percentage / 100)

    # Calcular la respuesta correcta
    span_pv = urv_pv - lrv_pv
    span_out = signal_type['urv'] - signal_type['lrv']
    output = (((pv_in - lrv_pv) / span_pv) * span_out) + signal_type['lrv']
    
    # Generar opciones
    correct_answer = f"{output:.2f} {signal_type['units']}"
    options = {correct_answer}
    while len(options) < 4:
        # Errores comunes: no sumar el LRV_OUT, invertir el cálculo, etc.
        error_factor = random.uniform(0.5, 1.5)
        wrong_answer = f"{output * error_factor:.2f} {signal_type['units']}"
        if wrong_answer != correct_answer:
            options.add(wrong_answer)
            
    question_text = (
        f"Un **{pv_type['name']}** está configurado con un rango de **{lrv_pv} a {urv_pv} {pv_type['units']}**. "
        f"El transmisor tiene una señal de salida de **{signal_type['lrv']}-{signal_type['urv']} {signal_type['units']}**. "
        f"¿Qué valor de salida corresponde a un {percentage}% del rango de medida ({pv_in:.2f} {pv_type['units']})?"
    )
    
    return question_text, list(options), correct_answer


# --- INTERFAZ DE USUARIO (STREAMLIT) ---

st.title("👨‍💻 Asistente de Instrumentación Industrial")
st.markdown("Herramienta interactiva para estudiar y resolver problemas de instrumentación y control. Creada por tu mentor, el Ingeniero de Instrumentación y Control.")

# --- TABS PRINCIPALES ---
tab1, tab2 = st.tabs(["**🆔 Identificación de Instrumentos (ISA-5.1)**", "**📈 Cálculos de Escalamiento**"])


# --- PESTAÑA 1: IDENTIFICACIÓN DE INSTRUMENTOS ---
with tab1:
    st.header("Identificación de Instrumentos según ISA-5.1")
    
    mode_isa = st.radio("Selecciona el modo de operación:", ["**Modo Búsqueda**", "**Modo Examen 🧠**"], horizontal=True)

    if mode_isa == "**Modo Búsqueda**":
        st.info("Ingresa un 'tag' de instrumento (ej. TT, PIC, LSH) para ver su descripción.")
        tag_input = st.text_input("Ingresa el Tag del Instrumento:", "PT").upper()
        
        if tag_input:
            col1, col2 = st.columns([1,1])
            with col1:
                st.markdown("#### Descripción del Instrumento:")
                description = get_instrument_description(tag_input)
                st.markdown(description)
            with col2:
                st.markdown("#### Símbolo Típico en P&ID:")
                # Intenta encontrar una imagen específica, si no, usa la genérica
                image_key = "".join(filter(str.isalpha, tag_input))
                if image_key not in INSTRUMENT_IMAGES:
                    image_key = "GENERIC"
                st.image(INSTRUMENT_IMAGES.get(image_key, INSTRUMENT_IMAGES["GENERIC"]), caption=f"Símbolo para {tag_input}", use_column_width=True)

    else: # Modo Examen
        st.subheader("📝 Examen: ¿Qué significa este tag?")
        st.warning("Pon a prueba tu conocimiento de la norma ISA-5.1.")

        if 'isa_question' not in st.session_state:
            st.session_state.isa_question = generate_isa_quiz()
            st.session_state.isa_score = 0
            st.session_state.isa_attempts = 0

        desc, options, correct_tag = st.session_state.isa_question
        random.shuffle(options)
        
        st.markdown(f"**Pregunta:** ¿Cuál es el tag para un **'{desc}'**?")
        user_answer = st.radio("Selecciona la respuesta correcta:", options, key=f"isa_q_{st.session_state.isa_attempts}")

        if st.button("Verificar Respuesta", key="verify_isa"):
            st.session_state.isa_attempts += 1
            if user_answer == correct_tag:
                st.success(f"¡Correcto! ✅ '{correct_tag}' es la respuesta.")
                st.session_state.isa_score += 1
            else:
                st.error(f"Incorrecto. ❌ La respuesta correcta es '{correct_tag}'.")

            st.info(f"Puntaje: **{st.session_state.isa_score} / {st.session_state.isa_attempts}**")
            
            # Genera la siguiente pregunta
            st.session_state.isa_question = generate_isa_quiz()
            st.button("Siguiente Pregunta ➡️")


# --- PESTAÑA 2: CÁLCULOS DE ESCALAMIENTO ---
with tab2:
    st.header("Cálculos de Escalamiento de Señales")
    
    mode_calc = st.radio("Selecciona el modo de operación:", ["**Calculadora Interactiva**", "**Modo Examen 🧠**"], horizontal=True, key="calc_mode")

    if mode_calc == "**Calculadora Interactiva**":
        st.info("Ingresa los rangos de tu proceso y de la señal para realizar el cálculo.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Variable de Proceso (PV)")
            pv_units = st.text_input("Unidades (ej. kPa, °C, %)", "kPa")
            lrv_pv = st.number_input(f"Valor Mínimo (LRV) en {pv_units}", value=100.0, format="%.2f")
            urv_pv = st.number_input(f"Valor Máximo (URV) en {pv_units}", value=500.0, format="%.2f")
            
        with col2:
            st.subheader("Señal de Salida (OUT)")
            out_units = st.text_input("Unidades (ej. mA, V, psi)", "mA")
            lrv_out = st.number_input(f"Valor Mínimo (LRV) en {out_units}", value=4.0, format="%.2f")
            urv_out = st.number_input(f"Valor Máximo (URV) en {out_units}", value=20.0, format="%.2f")
        
        st.divider()

        st.subheader("Realizar Conversión")
        input_pv = st.number_input(f"Ingresa el valor actual del proceso en {pv_units}", value=(lrv_pv + urv_pv) / 2, format="%.2f")

        if st.button("Calcular Salida"):
            if urv_pv == lrv_pv:
                st.error("El rango de la variable de proceso no puede ser cero.")
            else:
                # Cálculo
                span_pv = urv_pv - lrv_pv
                span_out = urv_out - lrv_out
                output = (((input_pv - lrv_pv) / span_pv) * span_out) + lrv_out
                
                st.success(f"**Resultado:** Para una entrada de **{input_pv:.2f} {pv_units}**, la salida es **{output:.3f} {out_units}**")

                with st.expander("Ver el desglose del cálculo (¡La fórmula general!)"):
                    st.latex(r"Salida = \left( \frac{Valor_{PV} - LRV_{PV}}{URV_{PV} - LRV_{PV}} \right) \times (Span_{OUT}) + LRV_{OUT}")
                    st.markdown(f"- **Span del Proceso (Span_PV):** {urv_pv} - {lrv_pv} = {span_pv} {pv_units}")
                    st.markdown(f"- **Span de la Salida (Span_OUT):** {urv_out} - {lrv_out} = {span_out} {out_units}")
                    st.markdown(f"- **Cálculo:** `(({input_pv} - {lrv_pv}) / {span_pv}) * {span_out} + {lrv_out} = {output:.3f}`")

    else: # Modo Examen
        st.subheader("📝 Examen: Resuelve el problema de escalamiento")
        st.warning("Aplica la fórmula general para encontrar la respuesta correcta.")

        if 'scale_question' not in st.session_state:
            st.session_state.scale_question = generate_scaling_quiz()
            st.session_state.scale_score = 0
            st.session_state.scale_attempts = 0

        question, options, correct_answer = st.session_state.scale_question
        random.shuffle(options)
        
        st.markdown(f"**Problema:** {question}")
        user_answer = st.radio("Selecciona la salida calculada:", options, key=f"scale_q_{st.session_state.scale_attempts}")

        if st.button("Verificar Respuesta", key="verify_scale"):
            st.session_state.scale_attempts += 1
            if user_answer == correct_answer:
                st.success(f"¡Excelente cálculo! ✅ La respuesta es {correct_answer}.")
                st.session_state.scale_score += 1
            else:
                st.error(f"Cálculo incorrecto. ❌ La respuesta correcta era {correct_answer}.")

            st.info(f"Puntaje: **{st.session_state.scale_score} / {st.session_state.scale_attempts}**")

            # Genera la siguiente pregunta
            st.session_state.scale_question = generate_scaling_quiz()
            st.button("Siguiente Problema ➡️")