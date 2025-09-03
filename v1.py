# app_instrumentacion_v2.py
import streamlit as st
import random
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Asistente de Instrumentación v2.0",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS PERSONALIZADOS (Opcional, para pulir la apariencia) ---
st.markdown("""
<style>
    /* Mejora la apariencia de los contenedores de métricas */
    [data-testid="stMetricValue"] {
        font-size: 24px;
    }
    /* Estilo para los expanders */
    .st-expander {
        border: 1px solid #2C3E50;
        border-radius: 10px;
    }
    .st-expander header {
        background-color: #F0F2F6;
        color: #2C3E50;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# --- BASE DE DATOS Y LÓGICA ---

# --- DICCIONARIOS ISA-5.1 ---
FIRST_LETTER = {
    'A': 'Análisis', 'B': 'Llama (Burner)', 'C': 'Conductividad', 'D': 'Densidad o Peso Específico',
    'E': 'Tensión (Voltaje)', 'F': 'Caudal (Flow)', 'H': 'Manual (Hand)', 'I': 'Corriente Eléctrica',
    'J': 'Potencia', 'K': 'Tiempo', 'L': 'Nivel (Level)', 'M': 'Humedad (Moisture)',
    'P': 'Presión', 'Q': 'Cantidad', 'R': 'Radiactividad', 'S': 'Velocidad o Frecuencia',
    'T': 'Temperatura', 'V': 'Vibración', 'W': 'Peso o Fuerza', 'Y': 'Evento o Estado', 'Z': 'Posición'
}
SUCCESSOR_LETTERS = {
    'A': 'Alarma', 'C': 'Controlador', 'E': 'Elemento Primario (Sensor)', 'H': 'Alto (High)',
    'I': 'Indicador', 'L': 'Luz Piloto o Bajo (Low)', 'R': 'Registrador (Recorder)',
    'S': 'Interruptor (Switch)', 'T': 'Transmisor', 'V': 'Válvula, Damper o Actuador',
    'Y': 'Relé o Convertidor', 'Z': 'Elemento Final de Control (No clasificado)'
}

# --- BIBLIOTECA DE SÍMBOLOS P&ID ---
PID_SYMBOLS = {
    "Instrumentos": {
        "Instrumento Discreto / Aislado": "https://i.imgur.com/Cbn55Od.png",
        "Instrumento en Panel de Control Principal": "https://i.imgur.com/Bf1gB8w.png",
        "Instrumento en Panel Local": "https://i.imgur.com/zO4yB7c.png",
        "Función de Computadora / PLC": "https://i.imgur.com/vHq7FfS.png",
        "Lógica en PLC": "https://i.imgur.com/dJ8o8tX.png",
    },
    "Válvulas": {
        "Válvula de Globo Genérica": "https://i.imgur.com/v3d9E4S.png",
        "Válvula de Bola": "https://i.imgur.com/K1L5J2s.png",
        "Válvula de Compuerta": "https://i.imgur.com/T0b4u0a.png",
        "Válvula de Mariposa": "https://i.imgur.com/uJ8wQ9l.png",
        "Válvula de Control Neumática (Falla Cierra)": "https://i.imgur.com/NfT2Y6f.png",
        "Válvula de Control Neumática (Falla Abre)": "https://i.imgur.com/B9I6k4p.png",
    },
    "Líneas de Señal": {
        "Conexión a Proceso": "https://i.imgur.com/x0Q3K8C.png",
        "Señal Neumática": "https://i.imgur.com/s6n9p0E.png",
        "Señal Eléctrica": "https://i.imgur.com/r7wY6G7.png",
        "Tubo Capilar": "https://i.imgur.com/G5n0f6F.png",
        "Enlace de Software o Datos": "https://i.imgur.com/w8m4t1J.png",
    }
}


# --- FUNCIONES DE LÓGICA ---

def get_instrument_description(tag):
    # ... (código sin cambios)
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
    full_name = ""
    if 'T' in successors:
        full_name = f"Transmisor de {FIRST_LETTER[first]}"
    elif 'I' in successors and 'C' in successors:
        full_name = f"Controlador Indicador de {FIRST_LETTER[first]}"
    elif 'S' in successors:
        full_name = f"Interruptor de {FIRST_LETTER[first]}"
    if full_name:
        return f"**Nombre Común:** {full_name}\n\n**Desglose:**\n- **{first}:** {FIRST_LETTER[first]}\n- **{'/'.join(successors)}:** {', '.join(functions)}"
    return desc

def generate_isa_quiz():
    # ... (código sin cambios)
    correct_var_code = random.choice(list(FIRST_LETTER.keys()))
    correct_func_code = random.choice(['T', 'I', 'C', 'S'])
    correct_tag = correct_var_code + correct_func_code
    correct_desc = f"{SUCCESSOR_LETTERS[correct_func_code]} de {FIRST_LETTER[correct_var_code]}"
    options = {correct_tag}
    while len(options) < 4:
        wrong_var = random.choice(list(FIRST_LETTER.keys()))
        wrong_func = random.choice(list(SUCCESSOR_LETTERS.keys()))
        wrong_tag = wrong_var + wrong_func
        if wrong_tag != correct_tag:
            options.add(wrong_tag)
    return correct_desc, list(options), correct_tag

# Funciones de conversión de unidades
def convert_pressure(value, from_unit, to_unit):
    # Tabla de conversión a kPa
    to_kpa = {
        'kPa': 1,
        'bar': 100,
        'psi': 6.89476,
        'inH₂O': 0.249089
    }
    # Convertir de la unidad de entrada a kPa
    value_kpa = value * to_kpa[from_unit]
    # Convertir de kPa a la unidad de salida
    from_kpa = {unit: 1/factor for unit, factor in to_kpa.items()}
    return value_kpa * from_kpa[to_unit]

def convert_temp(value, from_unit, to_unit):
    if from_unit == to_unit:
        return value
    if from_unit == '°C':
        if to_unit == '°F': return (value * 9/5) + 32
        if to_unit == 'K': return value + 273.15
    if from_unit == '°F':
        if to_unit == '°C': return (value - 32) * 5/9
        if to_unit == 'K': return ((value - 32) * 5/9) + 273.15
    if from_unit == 'K':
        if to_unit == '°C': return value - 273.15
        if to_unit == '°F': return ((value - 273.15) * 9/5) + 32
    return value


# --- INTERFAZ DE USUARIO (STREAMLIT) ---

st.title("🔧 Asistente de Instrumentación Industrial v2.0")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⭐ Tips del Ingeniero")
    tips = [
        "La señal 4-20 mA se usa porque un valor de 0 mA indica un fallo (cable roto), a esto se le llama 'cero vivo'.",
        "Un P&ID es el 'mapa' de la planta. Aprender a leerlo es una habilidad fundamental.",
        "La característica de una válvula (lineal, isoporcentual) se elige según el comportamiento del proceso que controla.",
        "Calibrar un instrumento significa verificar y ajustar su precisión contra un estándar conocido (patrón).",
        "El 'Span' de un instrumento es la diferencia algebraica entre el valor superior e inferior del rango.",
        "Un PLC (Controlador Lógico Programable) es el cerebro de la mayoría de los procesos automatizados modernos."
    ]
    st.info(f"_{random.choice(tips)}_")
    st.markdown("---")
    st.write("Creado como herramienta de apoyo por tu mentor en Instrumentación y Control.")


# --- TABS PRINCIPALES ---
tab1, tab2, tab3, tab4 = st.tabs([
    "**🆔 Identificación (ISA-5.1)**", 
    "**📈 Cálculos de Escalamiento**",
    "**🔄 Conversor de Unidades**",
    "**📚 Biblioteca de Símbolos P&ID**"
])


# --- PESTAÑA 1: IDENTIFICACIÓN DE INSTRUMENTOS ---
with tab1:
    st.header("Identificación de Instrumentos")
    mode_isa = st.radio("Selecciona el modo:", ["**Modo Búsqueda**", "**Modo Examen 🧠**"], horizontal=True, key="isa_mode")

    if mode_isa == "**Modo Búsqueda**":
        # ... (código sin cambios)
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
                image_key = "".join(filter(str.isalpha, tag_input))
                image_url = PID_SYMBOLS["Instrumentos"].get("Instrumento Discreto / Aislado") # Genérico
                st.image(image_url, caption=f"Símbolo para {tag_input}", use_column_width=True)

    else: # Modo Examen
        st.subheader("📝 Examen: ¿Qué significa este tag?")
        # CORRECCIÓN DEL BUG: Se usan claves únicas para el radio y se maneja el estado
        if 'current_isa_question' not in st.session_state:
            st.session_state.current_isa_question = generate_isa_quiz()
            st.session_state.isa_answer_submitted = False
        
        desc, options, correct_tag = st.session_state.current_isa_question
        
        st.markdown(f"**Pregunta:** ¿Cuál es el tag para un **'{desc}'**?")
        
        # Mezclar opciones solo una vez por pregunta
        if 'shuffled_options' not in st.session_state or st.session_state.get('last_tag') != correct_tag:
            st.session_state.shuffled_options = random.sample(options, len(options))
            st.session_state.last_tag = correct_tag

        user_answer = st.radio("Selecciona la respuesta correcta:", st.session_state.shuffled_options, key=f"isa_quiz_{correct_tag}")
        
        if st.button("Verificar Respuesta", key="verify_isa"):
            if user_answer == correct_tag:
                st.success(f"¡Correcto! ✅ '{correct_tag}' es la respuesta.")
                st.toast("¡Excelente trabajo!")
            else:
                st.error(f"Incorrecto. ❌ La respuesta correcta es '{correct_tag}'.")
            st.session_state.isa_answer_submitted = True

        if st.session_state.get('isa_answer_submitted'):
            if st.button("Siguiente Pregunta ➡️"):
                st.session_state.current_isa_question = generate_isa_quiz()
                st.session_state.isa_answer_submitted = False
                st.experimental_rerun()


# --- PESTAÑA 2: CÁLCULOS DE ESCALAMIENTO ---
with tab2:
    st.header("Cálculos de Escalamiento de Señales")
    st.info("Define los rangos del instrumento y calcula la relación entre la variable de proceso y la señal de salida.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Variable de Proceso (PV)")
        pv_units = st.text_input("Unidades (ej. kPa, °C, %)", "kPa")
        lrv_pv = st.number_input(f"Valor Mínimo (LRV)", value=97.8, format="%.2f")
        urv_pv = st.number_input(f"Valor Máximo (URV)", value=427.0, format="%.2f")
    with col2:
        st.subheader("Señal de Salida (OUT)")
        out_units = st.text_input("Unidades (ej. mA, V, psi)", "V")
        lrv_out = st.number_input(f"Valor Mínimo (LRV)", value=1.0, format="%.2f")
        urv_out = st.number_input(f"Valor Máximo (URV)", value=5.0, format="%.2f")

    st.divider()

    calc_type = st.radio(
        "¿Qué deseas calcular?",
        ["Un solo punto", "Generar Tabla de Calibración"],
        horizontal=True,
        key="calc_type"
    )

    if calc_type == "Un solo punto":
        input_pv = st.number_input(f"Ingresa el valor del proceso en {pv_units}", value=(lrv_pv + urv_pv) / 2, format="%.2f")
        if st.button("Calcular Salida"):
            if urv_pv <= lrv_pv:
                st.error("El valor URV debe ser mayor que el LRV.")
            else:
                span_pv = urv_pv - lrv_pv
                span_out = urv_out - lrv_out
                output = (((input_pv - lrv_pv) / span_pv) * span_out) + lrv_out
                st.metric(label=f"Salida Correspondiente en {out_units}", value=f"{output:.3f}")
    
    else: # Generar Tabla de Calibración
        st.subheader("Generador de Tabla de Calibración")
        increment = st.number_input("Introduce el incremento de porcentaje (%) para la tabla:", min_value=1, max_value=50, value=10, step=1)
        
        if st.button(f"Generar Tabla cada {increment}%"):
            if urv_pv <= lrv_pv:
                st.error("El valor URV debe ser mayor que el LRV.")
            else:
                span_pv = urv_pv - lrv_pv
                span_out = urv_out - lrv_out
                
                table_data = []
                for percent in range(0, 101, increment):
                    pv_value = lrv_pv + (span_pv * percent / 100)
                    out_value = lrv_out + (span_out * percent / 100)
                    table_data.append({
                        "Porcentaje (%)": f"{percent}%",
                        f"Proceso ({pv_units})": f"{pv_value:.2f}",
                        f"Salida ({out_units})": f"{out_value:.3f}"
                    })
                # Asegurar que el 100% esté si el incremento no es exacto
                if (100 % increment) != 0:
                     table_data.append({
                        "Porcentaje (%)": "100%",
                        f"Proceso ({pv_units})": f"{urv_pv:.2f}",
                        f"Salida ({out_units})": f"{urv_out:.3f}"
                    })

                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True)

# --- PESTAÑA 3: CONVERSOR DE UNIDADES ---
with tab3:
    st.header("Conversor de Unidades")
    magnitude = st.selectbox("Selecciona la magnitud a convertir:", ["Presión", "Temperatura"])

    if magnitude == "Presión":
        units = ['kPa', 'bar', 'psi', 'inH₂O']
        col1, col2, col3 = st.columns(3)
        from_unit = col1.selectbox("Desde:", units, key="p_from")
        to_unit = col2.selectbox("Hasta:", units, key="p_to", index=1)
        value = col3.number_input(f"Valor en {from_unit}", value=1.0, format="%.4f")
        result = convert_pressure(value, from_unit, to_unit)
        st.metric(label=f"Resultado en {to_unit}", value=f"{result:.4f}")
    
    if magnitude == "Temperatura":
        units = ['°C', '°F', 'K']
        col1, col2, col3 = st.columns(3)
        from_unit = col1.selectbox("Desde:", units, key="t_from")
        to_unit = col2.selectbox("Hasta:", units, key="t_to", index=1)
        value = col3.number_input(f"Valor en {from_unit}", value=25.0, format="%.2f")
        result = convert_temp(value, from_unit, to_unit)
        st.metric(label=f"Resultado en {to_unit}", value=f"{result:.2f}")

# --- PESTAÑA 4: BIBLIOTECA DE SÍMBOLOS P&ID ---
with tab4:
    st.header("Biblioteca de Símbolos Comunes en P&ID")
    st.info("Una referencia rápida para los símbolos estándar (ISA-5.1) que encontrarás en los diagramas de procesos.")

    for category, symbols in PID_SYMBOLS.items():
        with st.expander(f"**{category}**", expanded=(category=="Instrumentos")):
            for name, url in symbols.items():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(url, width=100)
                with col2:
                    st.markdown(f"**{name}**")
                    # Podríamos añadir más descripción aquí si quisiéramos
