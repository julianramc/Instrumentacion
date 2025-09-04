import streamlit as st
import random
import pandas as pd
import math

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Asistente de Instrumentación v5.0",
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
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .st-expander header { 
        background: linear-gradient(90deg, #3498DB, #2C3E50);
        color: white; 
        border-radius: 15px;
        font-weight: bold;
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
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #e2f3ff;
        border: 1px solid #b8daff;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- BASES DE DATOS AMPLIADAS ---

FIRST_LETTER = {
    'A': 'Análisis', 'B': 'Llama (Burner)', 'C': 'Conductividad', 'D': 'Densidad', 'E': 'Tensión (Voltaje)',
    'F': 'Caudal (Flow)', 'G': 'Calibre/Dimensión', 'H': 'Manual (Hand)', 'I': 'Corriente', 'J': 'Potencia', 
    'K': 'Tiempo', 'L': 'Nivel (Level)', 'M': 'Humedad', 'N': 'Definido por usuario', 'O': 'Definido por usuario',
    'P': 'Presión', 'Q': 'Cantidad', 'R': 'Radiactividad', 'S': 'Velocidad', 'T': 'Temperatura',
    'U': 'Multivariable', 'V': 'Vibración', 'W': 'Peso o Fuerza', 'X': 'Sin clasificar', 'Y': 'Evento', 'Z': 'Posición'
}

SUCCESSOR_LETTERS = {
    'A': 'Alarma', 'B': 'Definido por usuario', 'C': 'Controlador', 'D': 'Diferencial', 'E': 'Elemento Primario', 
    'F': 'Fracción/Ratio', 'G': 'Visor/Mirilla', 'H': 'Alto', 'I': 'Indicador', 'J': 'Exploración/Barrido',
    'K': 'Estación de Control', 'L': 'Luz o Bajo', 'M': 'Medio/Intermedio', 'N': 'Definido por usuario',
    'O': 'Orificio/Restricción', 'P': 'Punto de Prueba', 'Q': 'Integrador/Totalizador', 'R': 'Registrador', 
    'S': 'Interruptor (Switch)', 'T': 'Transmisor', 'U': 'Multifunción', 'V': 'Válvula/Actuador', 
    'W': 'Pozo/Vaina', 'X': 'Sin clasificar', 'Y': 'Relé/Convertidor', 'Z': 'Elemento Final de Control'
}

PID_SYMBOLS = {
    "Instrumentos y Ubicación": {
        "Instrumento en Campo": "https://i.imgur.com/Cbn55Od.png",
        "Panel de Control Principal": "https://i.imgur.com/Bf1gB8w.png",
        "Panel Local": "https://i.imgur.com/zO4yB7c.png",
        "Función en DCS/Computadora": "https://i.imgur.com/vHq7FfS.png",
        "Lógica en PLC": "https://i.imgur.com/dJ8o8tX.png",
        "Instrumento Auxiliar": "https://i.imgur.com/K9mN2pQ.png",
    },
    "Válvulas de Proceso y Control": {
        "Válvula de Globo": "https://i.imgur.com/v3d9E4S.png", 
        "Válvula de Bola": "https://i.imgur.com/K1L5J2s.png",
        "Válvula de Compuerta": "https://i.imgur.com/T0b4u0a.png", 
        "Válvula de Mariposa": "https://i.imgur.com/uJ8wQ9l.png",
        "Válvula de Diafragma": "https://i.imgur.com/1vO1e8j.png", 
        "Válvula de Aguja": "https://i.imgur.com/3q8Yf4M.png",
        "Válvula de Retención (Check)": "https://i.imgur.com/d1Q6n7M.png", 
        "Válvula de 3 Vías": "https://i.imgur.com/5Jb6R6o.png",
        "Válvula de Seguridad": "https://i.imgur.com/X7Y9Z1a.png",
        "Válvula Reductora de Presión": "https://i.imgur.com/P8Q2R3b.png",
    },
    "Actuadores de Válvula": {
        "Actuador de Diafragma": "https://i.imgur.com/nJhA0yH.png", 
        "Actuador de Pistón": "https://i.imgur.com/P0b6A5t.png",
        "Actuador Eléctrico (Motor)": "https://i.imgur.com/9q4J5YF.png", 
        "Actuador Manual (Volante)": "https://i.imgur.com/R8i7Q6C.png",
        "Falla Cierra (FC)": "https://i.imgur.com/NfT2Y6f.png", 
        "Falla Abre (FO)": "https://i.imgur.com/B9I6k4p.png",
        "Posicionador": "https://i.imgur.com/M4N5O6p.png",
    },
    "Líneas de Señal e Impulso": {
        "Conexión a Proceso": "https://i.imgur.com/x0Q3K8C.png", 
        "Señal Neumática": "https://i.imgur.com/s6n9p0E.png",
        "Señal Eléctrica": "https://i.imgur.com/r7wY6G7.png", 
        "Tubo Capilar": "https://i.imgur.com/G5n0f6F.png",
        "Enlace de Software": "https://i.imgur.com/w8m4t1J.png", 
        "Señal Hidráulica": "https://i.imgur.com/5D4f2gD.png",
        "Fibra Óptica": "https://i.imgur.com/F7G8H9i.png",
        "Señal Inalámbrica": "https://i.imgur.com/W1X2Y3z.png",
    },
    "Sensores y Elementos Primarios": {
        "Termopar": "https://i.imgur.com/T1C2P3l.png",
        "RTD": "https://i.imgur.com/R4T5D6m.png",
        "Placa Orificio": "https://i.imgur.com/O7R8I9f.png",
        "Tubo Venturi": "https://i.imgur.com/V2N3T4u.png",
        "Rotámetro": "https://i.imgur.com/R5O6T7a.png",
        "Manómetro": "https://i.imgur.com/M8A9N0o.png",
    }
}

INSTRUMENT_SELECTION_DB = {
    "Temperatura": {
        "Uso General (Bajo Costo)": {
            "instrumento": "Termopar (Tipo J, K)",
            "descripcion": "**Aplicaciones:** Hornos, motores, gases de escape, monitoreo general. **Rango:** -200°C a +1200°C. **Exactitud:** ±1-3°C. **Ventajas:** Muy económico, robusto, rango extremadamente amplio, respuesta rápida. **Desventajas:** Menor exactitud, deriva con el tiempo, requiere compensación de junta fría.",
            "imagen": "https://i.imgur.com/sC5nL5A.png",
            "costo": "Bajo ($20-100)",
            "exactitud": "±1-3°C"
        },
        "Alta Precisión": {
            "instrumento": "RTD (Pt100/Pt1000)",
            "descripcion": "**Aplicaciones:** Control de procesos críticos, farmacéutico, alimentario, transferencia de custodia. **Rango:** -200°C a +850°C. **Exactitud:** ±0.1-0.5°C. **Ventajas:** Alta exactitud, excelente estabilidad, linealidad superior. **Desventajas:** Más costoso, rango limitado, requiere excitación, más frágil.",
            "imagen": "https://i.imgur.com/Gj8aA3n.png",
            "costo": "Alto ($100-500)",
            "exactitud": "±0.1-0.5°C"
        },
        "Sin Contacto": {
            "instrumento": "Pirómetro Infrarrojo",
            "descripcion": "**Aplicaciones:** Objetos en movimiento, alta temperatura, materiales peligrosos. **Rango:** -50°C a +3000°C. **Exactitud:** ±1-2% de lectura. **Ventajas:** Sin contacto, respuesta instantánea, no afecta el proceso. **Desventajas:** Afectado por emisividad, vapor, polvo.",
            "imagen": "https://i.imgur.com/P9I8R7o.png",
            "costo": "Medio ($200-1000)",
            "exactitud": "±1-2% lectura"
        }
    },
    "Presión": {
        "Uso General (Bajo Costo)": {
            "instrumento": "Transmisor Piezorresistivo",
            "descripcion": "**Aplicaciones:** Líneas de aire, agua, aceite, servicios generales. **Rango:** 0-1000 bar. **Exactitud:** ±0.25-1% span. **Ventajas:** Económico, compacto, robusto. **Desventajas:** Sensible a temperatura, menor exactitud que capacitivos.",
            "imagen": "https://i.imgur.com/vHqgPj7.png",
            "costo": "Bajo ($100-300)",
            "exactitud": "±0.25-1% span"
        },
        "Alta Precisión": {
            "instrumento": "Transmisor Capacitivo",
            "descripcion": "**Aplicaciones:** Presión diferencial, caudal, nivel, control crítico, vacío. **Rango:** 0.1 Pa a 70 MPa. **Exactitud:** ±0.04-0.1% span. **Ventajas:** Alta exactitud, excelente estabilidad, amplio rango. **Desventajas:** Más costoso, complejo.",
            "imagen": "https://i.imgur.com/R3aB52N.png",
            "costo": "Alto ($500-2000)",
            "exactitud": "±0.04-0.1% span"
        },
        "Alta Temperatura": {
            "instrumento": "Transmisor con Sello Remoto",
            "descripcion": "**Aplicaciones:** Procesos a alta temperatura, fluidos corrosivos, cristalizantes. **Rango:** Según sensor base. **Exactitud:** ±0.1-0.5% span. **Ventajas:** Protege el sensor, permite medición remota. **Desventajas:** Mayor costo, posible deriva térmica.",
            "imagen": "https://i.imgur.com/S4E5L6r.png",
            "costo": "Alto ($800-3000)",
            "exactitud": "±0.1-0.5% span"
        }
    },
    "Nivel": {
        "Uso General (Bajo Costo)": {
            "instrumento": "Sensor Ultrasónico",
            "descripcion": "**Aplicaciones:** Tanques abiertos, agua, líquidos limpios, sumideros. **Rango:** 0.3-15 m. **Exactitud:** ±0.25% span. **Ventajas:** Sin contacto, fácil instalación, económico. **Desventajas:** Afectado por espuma, vapor, turbulencia.",
            "imagen": "https://i.imgur.com/yL7R8F2.png",
            "costo": "Bajo ($200-600)",
            "exactitud": "±0.25% span"
        },
        "Alta Precisión": {
            "instrumento": "Radar de Onda Guiada (GWR)",
            "descripcion": "**Aplicaciones:** Inventarios, condiciones variables, interfaces líquido-líquido. **Rango:** 0.2-35 m. **Exactitud:** ±1-3 mm. **Ventajas:** Muy alta precisión, inmune a condiciones del proceso. **Desventajas:** Contacto con producto, más costoso.",
            "imagen": "https://i.imgur.com/T0TqW4h.png",
            "costo": "Alto ($1500-5000)",
            "exactitud": "±1-3 mm"
        },
        "Continuo Sin Contacto": {
            "instrumento": "Radar Sin Contacto (FMCW)",
            "descripcion": "**Aplicaciones:** Tanques presurizados, líquidos agresivos, alta temperatura. **Rango:** 0.5-100 m. **Exactitud:** ±2-5 mm. **Ventajas:** Sin contacto, inmune a condiciones del proceso. **Desventajas:** Costo elevado, requiere calibración.",
            "imagen": "https://i.imgur.com/R6A7D8r.png",
            "costo": "Muy Alto ($2000-8000)",
            "exactitud": "±2-5 mm"
        }
    },
    "Caudal": {
        "Uso General (Bajo Costo)": {
            "instrumento": "Placa Orificio + ΔP",
            "descripcion": "**Aplicaciones:** Líquidos y gases limpios, tuberías grandes. **Rango:** Variable según diseño. **Exactitud:** ±1-4% lectura. **Ventajas:** Muy económico, probado, sin partes móviles. **Desventajas:** Alta pérdida de presión, sensible a perfil de velocidad.",
            "imagen": "https://i.imgur.com/O7R8I9f.png",
            "costo": "Muy Bajo ($100-500)",
            "exactitud": "±1-4% lectura"
        },
        "Alta Precisión": {
            "instrumento": "Medidor Electromagnético",
            "descripcion": "**Aplicaciones:** Líquidos conductivos, agua, químicos. **Rango:** 0.1-15 m/s. **Exactitud:** ±0.2-0.5% lectura. **Ventajas:** Sin obstrucción, bidireccional, alta exactitud. **Desventajas:** Solo líquidos conductivos, costo elevado.",
            "imagen": "https://i.imgur.com/E9M8A7g.png",
            "costo": "Alto ($1000-5000)",
            "exactitud": "±0.2-0.5% lectura"
        },
        "Gases y Vapores": {
            "instrumento": "Medidor de Vórtex",
            "descripcion": "**Aplicaciones:** Vapor, gases, líquidos de baja viscosidad. **Rango:** Re > 10,000. **Exactitud:** ±0.75-1% lectura. **Ventajas:** Sin partes móviles, amplio rango, multifase. **Desventajas:** Sensible a vibración, requiere flujo turbulento.",
            "imagen": "https://i.imgur.com/V3O7R8t.png",
            "costo": "Medio ($800-3000)",
            "exactitud": "±0.75-1% lectura"
        }
    }
}

def generate_scaling_quiz():
    """Generate a random scaling exercise with improved variety and error handling."""
    try:
        pv_types = [
            {'name': 'Presión', 'units': 'bar'}, 
            {'name': 'Temperatura', 'units': '°C'}, 
            {'name': 'Nivel', 'units': '%'},
            {'name': 'Caudal', 'units': 'L/min'},
            {'name': 'pH', 'units': 'pH'},
            {'name': 'Conductividad', 'units': 'µS/cm'}
        ]
        
        signal_types = [
            {'name': 'Corriente', 'units': 'mA', 'lrv': 4, 'urv': 20}, 
            {'name': 'Voltaje', 'units': 'V', 'lrv': 1, 'urv': 5},
            {'name': 'Voltaje', 'units': 'V', 'lrv': 0, 'urv': 10}
        ]
        
        pv = random.choice(pv_types)
        signal = random.choice(signal_types)
        
        # Generate more realistic ranges based on variable type
        if pv['name'] == 'Temperatura':
            lrv_pv, urv_pv = random.randint(-50, 50), random.randint(100, 800)
        elif pv['name'] == 'Presión':
            lrv_pv, urv_pv = random.randint(0, 5), random.randint(10, 100)
        elif pv['name'] == 'pH':
            lrv_pv, urv_pv = 0, 14
        else:
            lrv_pv, urv_pv = round(random.uniform(0, 50)), round(random.uniform(100, 500))
        
        # Decide if direct (PV -> OUT) or inverse (OUT -> PV)
        if random.choice([True, False]):
            # Direct conversion
            input_val = round(random.uniform(lrv_pv, urv_pv), 1)
            correct_out = (((input_val - lrv_pv) / (urv_pv - lrv_pv)) * (signal['urv'] - signal['lrv'])) + signal['lrv']
            question = f"Un transmisor de **{pv['name']}** con rango **{lrv_pv} a {urv_pv} {pv['units']}** y salida **{signal['lrv']}-{signal['urv']} {signal['units']}**, ¿qué salida corresponde a una lectura de **{input_val} {pv['units']}**?"
            correct_answer = f"{correct_out:.2f} {signal['units']}"
        else:
            # Inverse conversion
            input_val = round(random.uniform(signal['lrv'], signal['urv']), 2)
            correct_out = (((input_val - signal['lrv']) / (signal['urv'] - signal['lrv'])) * (urv_pv - lrv_pv)) + lrv_pv
            question = f"Un transmisor de **{pv['name']}** con rango **{lrv_pv} a {urv_pv} {pv['units']}** y salida **{signal['lrv']}-{signal['urv']} {signal['units']}**, ¿qué valor de proceso corresponde a una salida de **{input_val} {signal['units']}**?"
            correct_answer = f"{correct_out:.1f} {pv['units']}"
        
        # Generate distractors
        options = {correct_answer}
        base_value = float(correct_answer.split(' ')[0])
        unit = correct_answer.split(' ')[1]
        
        while len(options) < 4:
            distractor = base_value * random.uniform(0.6, 1.4)
            if abs(distractor - base_value) > 0.1:  # Ensure distractors are different enough
                options.add(f"{distractor:.2f} {unit}")
        
        return question, list(options), correct_answer
        
    except Exception as e:
        st.error(f"Error generando ejercicio: {e}")
        return "Error en la generación", ["Error"], "Error"

def generate_error_quiz():
    """Generate error calculation quiz with enhanced variety."""
    try:
        lrv = round(random.uniform(0, 50), 1)
        urv = round(random.uniform(100, 500), 1)
        valor_medido = round(random.uniform(lrv + (urv - lrv) * 0.2, urv - (urv - lrv) * 0.2), 2)
        
        accuracy_options = [
            {'val': 0.04, 'type': 'A'}, {'val': 0.1, 'type': 'A'}, {'val': 0.25, 'type': 'A'},
            {'val': 0.5, 'type': 'B'}, {'val': 1.0, 'type': 'B'},
            {'val': 0.1, 'type': 'C'}, {'val': 0.5, 'type': 'C'},
            {'val': 0.5, 'type': 'D'}, {'val': 1.0, 'type': 'D'}
        ]
        
        accuracy = random.choice(accuracy_options)
        accuracy_val, type_code = accuracy['val'], accuracy['type']
        
        accuracy_types = {
            'A': f"{accuracy_val}% del URV ({urv})",
            'B': f"{accuracy_val}% del span",
            'C': f"{accuracy_val}% del valor medido",
            'D': f"{accuracy_val} unidades"
        }
        
        span = urv - lrv
        
        if type_code == 'A':
            error = (accuracy_val / 100) * urv
        elif type_code == 'B':
            error = (accuracy_val / 100) * span
        elif type_code == 'C':
            error = (accuracy_val / 100) * valor_medido
        else:
            error = accuracy_val
        
        correct_answer = f"± {error:.3f}"
        question = f"Un instrumento con rango **{lrv} a {urv}** mide **{valor_medido}**. Si su exactitud es **{accuracy_types[type_code]}**, ¿cuál es el error máximo?"
        
        # Generate better distractors
        options = {correct_answer}
        while len(options) < 4:
            distractor_error = error * random.uniform(0.3, 3.0)
            if abs(distractor_error - error) > 0.001:
                options.add(f"± {distractor_error:.3f}")
        
        return question, list(options), correct_answer
        
    except Exception as e:
        st.error(f"Error generando ejercicio de error: {e}")
        return "Error en la generación", ["Error"], "Error"

def generate_tag_quiz():
    """Generate ISA-5.1 tag identification quiz."""
    try:
        # Generate random tag
        first_letter = random.choice(list(FIRST_LETTER.keys()))
        second_letter = random.choice(list(SUCCESSOR_LETTERS.keys()))
        loop_number = random.randint(100, 999)
        tag = f"{first_letter}{second_letter}-{loop_number}"
        
        # Create question
        question = f"¿Qué significa el tag **{tag}** según ISA-5.1?"
        
        # Correct answer
        correct_answer = f"{FIRST_LETTER[first_letter]} - {SUCCESSOR_LETTERS[second_letter]}"
        
        # Generate distractors
        options = {correct_answer}
        while len(options) < 4:
            wrong_first = random.choice(list(FIRST_LETTER.values()))
            wrong_second = random.choice(list(SUCCESSOR_LETTERS.values()))
            if f"{wrong_first} - {wrong_second}" != correct_answer:
                options.add(f"{wrong_first} - {wrong_second}")
        
        return question, list(options), correct_answer
        
    except Exception as e:
        st.error(f"Error generando ejercicio de tags: {e}")
        return "Error en la generación", ["Error"], "Error"

def convert_pressure(value, from_unit, to_unit):
    """Convert pressure between different units."""
    # Conversion factors to Pascal
    to_pascal = {
        'Pa': 1, 'kPa': 1000, 'MPa': 1000000, 'bar': 100000, 'mbar': 100,
        'psi': 6894.76, 'mmHg': 133.322, 'inHg': 3386.39, 'atm': 101325
    }
    
    try:
        pascal_value = value * to_pascal[from_unit]
        result = pascal_value / to_pascal[to_unit]
        return round(result, 4)
    except KeyError:
        return None

def convert_temperature(value, from_unit, to_unit):
    """Convert temperature between different units."""
    try:
        # Convert to Celsius first
        if from_unit == 'F':
            celsius = (value - 32) * 5/9
        elif from_unit == 'K':
            celsius = value - 273.15
        elif from_unit == 'R':
            celsius = (value - 491.67) * 5/9
        else:  # Celsius
            celsius = value
        
        # Convert from Celsius to target
        if to_unit == 'F':
            return round(celsius * 9/5 + 32, 2)
        elif to_unit == 'K':
            return round(celsius + 273.15, 2)
        elif to_unit == 'R':
            return round(celsius * 9/5 + 491.67, 2)
        else:  # Celsius
            return round(celsius, 2)
    except:
        return None

# --- INTERFAZ DE USUARIO MEJORADA ---

st.title("🛠️ Asistente de Instrumentación Industrial v5.0")
st.markdown("*Herramienta completa para cálculos, selección y práctica en instrumentación*")

with st.sidebar:
    st.header("⭐ Tips del Ingeniero")
    
    # Session state for tip rotation
    if 'tip_index' not in st.session_state:
        st.session_state.tip_index = 0
    
    tips = [
        "La exactitud no es lo mismo que la repetibilidad. Un instrumento puede ser muy repetible pero poco exacto.",
        "El 'Campo de Medida' (25-75% del rango) es donde un transmisor ofrece su mejor rendimiento.",
        "Un lazo de control se compone de: medición (sensor), controlador (PLC/DCS) y elemento final (válvula).",
        "La calibración en 5 puntos (0%, 25%, 50%, 75%, 100%) verifica la linealidad del instrumento.",
        "La histéresis es la diferencia entre lecturas ascendentes y descendentes en el mismo punto.",
        "Los transmisores inteligentes pueden compensar automáticamente efectos de temperatura y presión estática.",
        "La rangeabilidad (turndown) indica cuánto se puede reducir el rango sin perder exactitud.",
        "Los sellos remotos introducen errores adicionales por efectos de temperatura en el fluido de llenado.",
        "La presión diferencial para caudal varía con el cuadrado del flujo (ΔP ∝ Q²).",
        "Los RTD tienen coeficiente de temperatura positivo, los termistores pueden ser positivo o negativo."
    ]
    
    current_tip = tips[st.session_state.tip_index % len(tips)]
    st.info(f"💡 {current_tip}")
    
    if st.button("💡 Siguiente Tip"):
        st.session_state.tip_index += 1
        st.rerun()
    
    st.divider()
    
    st.header("📋 Referencia Rápida")
    with st.expander("Rangos Típicos"):
        st.markdown("""
        **Temperatura:**
        - Termopar K: -200 a 1200°C
        - RTD Pt100: -200 a 850°C
        - Termistor: -50 a 150°C
        
        **Presión:**
        - Piezorresistivo: 0-1000 bar
        - Capacitivo: 0.1 Pa - 70 MPa
        
        **Señales Estándar:**
        - 4-20 mA (analógica)
        - 1-5 V (analógica)
        - HART (digital + analógica)
        """)

tab1, tab2, tab3, tab4 = st.tabs(["**📐 Herramientas de Cálculo**", "**🤔 Guía de Ingeniería**", "**🧠 Centro de Práctica**", "**🔧 Conversores de Unidades**"])

with tab1:
    st.header("Cálculos Fundamentales de Instrumentación")
    
    with st.expander("**📈 Calculadora de Escalamiento y Análisis de Rango**", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Variable de Proceso (PV)")
            pv_units = st.text_input("Unidades", "kPa", key="pv_units")
            lrv_pv = st.number_input("LRV", value=100.0, format="%.2f", key="lrv_pv")
            urv_pv = st.number_input("URV", value=500.0, format="%.2f", key="urv_pv")
            
        with col2:
            st.subheader("Señal de Salida (OUT)")
            out_units = st.text_input("Unidades", "mA", key="out_units")
            lrv_out = st.number_input("LRV", value=4.0, format="%.2f", key="lrv_out")
            urv_out = st.number_input("URV", value=20.0, format="%.2f", key="urv_out")
        
        st.divider()
        
        # Live calculation section
        if urv_pv > lrv_pv and urv_out > lrv_out:
            col_calc1, col_calc2 = st.columns(2)
            
            with col_calc1:
                st.subheader("🔄 Conversión PV → Salida")
                pv_input = st.number_input("Valor de PV:", value=(lrv_pv + urv_pv)/2, format="%.2f")
                if lrv_pv <= pv_input <= urv_pv:
                    output_calc = (((pv_input - lrv_pv) / (urv_pv - lrv_pv)) * (urv_out - lrv_out)) + lrv_out
                    st.success(f"**Salida:** {output_calc:.3f} {out_units}")
                else:
                    st.warning("Valor fuera del rango del instrumento")
            
            with col_calc2:
                st.subheader("🔄 Conversión Salida → PV")
                out_input = st.number_input("Valor de Salida:", value=(lrv_out + urv_out)/2, format="%.3f")
                if lrv_out <= out_input <= urv_out:
                    pv_calc = (((out_input - lrv_out) / (urv_out - lrv_out)) * (urv_pv - lrv_pv)) + lrv_pv
                    st.success(f"**PV:** {pv_calc:.2f} {pv_units}")
                else:
                    st.warning("Valor fuera del rango de salida")
        
        st.divider()
        st.subheader("📊 Análisis del Rango del Instrumento")
        
        if urv_pv > lrv_pv:
            span = urv_pv - lrv_pv
            ci_inf_medida = lrv_pv + (0.25 * span)
            ci_sup_medida = urv_pv - (0.25 * span)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Campo de Indicación (CI)", f"{lrv_pv} a {urv_pv} {pv_units}")
            c2.metric("Span", f"{span:.2f} {pv_units}")
            c3.metric("Campo de Medida (25-75%)", f"{ci_inf_medida:.2f} a {ci_sup_medida:.2f} {pv_units}")
            
            # Additional analysis
            st.markdown("**Análisis Adicional:**")
            col_a1, col_a2, col_a3 = st.columns(3)
            col_a1.metric("Punto Medio", f"{(lrv_pv + urv_pv)/2:.2f} {pv_units}")
            col_a2.metric("Resolución (0.1%)", f"{span * 0.001:.4f} {pv_units}")
            col_a3.metric("Supresión de Cero", f"{lrv_pv:.2f} {pv_units}" if lrv_pv > 0 else "No")

    with st.expander("**🎯 Calculadora de Error y Exactitud Avanzada**"):
        ec1, ec2 = st.columns(2)
        
        with ec1:
            st.subheader("Parámetros del Instrumento")
            e_lrv = st.number_input("LRV del instrumento", 0.0, format="%.2f", key="e_lrv")
            e_urv = st.number_input("URV del instrumento", 1000.0, format="%.2f", key="e_urv")
            e_val = st.number_input("Valor medido", 500.0, format="%.2f", key="e_val")
            
        with ec2:
            st.subheader("Especificación de Exactitud")
            accuracy_type = st.selectbox("Tipo de exactitud:", [
                "A: % del URV", 
                "B: % del span", 
                "C: % del valor medido", 
                "D: En unidades absolutas",
                "E: % de la escala completa",
                "F: Combinada (% lectura + % span)"
            ])
            accuracy_val = st.number_input("Valor de exactitud:", 0.5, format="%.4f", key="e_acc")
            
            if "F:" in accuracy_type:
                accuracy_val2 = st.number_input("Segundo valor (% span):", 0.1, format="%.4f", key="e_acc2")
        
        if st.button("🧮 Calcular Error Completo"):
            if e_urv > e_lrv:
                e_span = e_urv - e_lrv
                
                if "A:" in accuracy_type:
                    error = (accuracy_val / 100) * e_urv
                    error_type = "% del URV"
                elif "B:" in accuracy_type:
                    error = (accuracy_val / 100) * e_span
                    error_type = "% del span"
                elif "C:" in accuracy_type:
                    error = (accuracy_val / 100) * e_val
                    error_type = "% del valor medido"
                elif "D:" in accuracy_type:
                    error = accuracy_val
                    error_type = "unidades absolutas"
                elif "E:" in accuracy_type:
                    error = (accuracy_val / 100) * (e_urv - 0)  # Assuming zero-based scale
                    error_type = "% de escala completa"
                elif "F:" in accuracy_type:
                    error1 = (accuracy_val / 100) * e_val
                    error2 = (accuracy_val2 / 100) * e_span
                    error = math.sqrt(error1**2 + error2**2)  # RSS combination
                    error_type = "combinada (RSS)"
                
                # Results display
                st.markdown("### 📊 Resultados del Análisis de Error")
                
                col_r1, col_r2, col_r3 = st.columns(3)
                col_r1.metric("Error Absoluto", f"± {error:.4f}", delta=f"{error_type}")
                col_r2.metric("Error Relativo", f"± {(error/e_val)*100:.3f}%", delta="del valor medido")
                col_r3.metric("Error vs Span", f"± {(error/e_span)*100:.3f}%", delta="del span")
                
                st.markdown(f"**Rango del Valor Real:** {e_val - error:.4f} a {e_val + error:.4f}")
                
                # Uncertainty budget
                st.markdown("### 📋 Presupuesto de Incertidumbre")
                uncertainty_data = {
                    'Fuente': ['Exactitud del instrumento', 'Resolución (estimada)', 'Deriva térmica (estimada)', 'Incertidumbre combinada'],
                    'Valor (±)': [f"{error:.4f}", f"{e_span*0.0005:.4f}", f"{error*0.1:.4f}", f"{math.sqrt(error**2 + (e_span*0.0005)**2 + (error*0.1)**2):.4f}"],
                    'Tipo': ['B', 'B', 'B', 'Combinada']
                }
                st.dataframe(pd.DataFrame(uncertainty_data), use_container_width=True)

with tab4:
    st.header("🔧 Conversores de Unidades")
    
    conv_col1, conv_col2 = st.columns(2)
    
    with conv_col1:
        st.subheader("🌡️ Conversor de Temperatura")
        temp_value = st.number_input("Valor:", value=25.0, key="temp_val")
        temp_from = st.selectbox("De:", ['C', 'F', 'K', 'R'], key="temp_from")
        temp_to = st.selectbox("A:", ['C', 'F', 'K', 'R'], key="temp_to")
        
        if st.button("Convertir Temperatura"):
            result = convert_temperature(temp_value, temp_from, temp_to)
            if result is not None:
                st.success(f"**{temp_value}°{temp_from} = {result}°{temp_to}**")
            else:
                st.error("Error en la conversión")
    
    with conv_col2:
        st.subheader("📊 Conversor de Presión")
        press_value = st.number_input("Valor:", value=1.0, key="press_val")
        press_from = st.selectbox("De:", ['Pa', 'kPa', 'MPa', 'bar', 'mbar', 'psi', 'mmHg', 'inHg', 'atm'], key="press_from")
        press_to = st.selectbox("A:", ['Pa', 'kPa', 'MPa', 'bar', 'mbar', 'psi', 'mmHg', 'inHg', 'atm'], key="press_to")
        
        if st.button("Convertir Presión"):
            result = convert_pressure(press_value, press_from, press_to)
            if result is not None:
                st.success(f"**{press_value} {press_from} = {result} {press_to}**")
            else:
                st.error("Error en la conversión")


with tab2:
    st.header("Guías de Referencia Rápida")
    
    with st.expander("**🤔 Asistente para Selección de Instrumentos**", expanded=True):
        sc1, sc2 = st.columns(2)
        variable = sc1.selectbox("Variable a medir:", list(INSTRUMENT_SELECTION_DB.keys()))
        precision = sc2.selectbox("Nivel de precisión requerido:", list(INSTRUMENT_SELECTION_DB[variable].keys()))
        
        recomendacion = INSTRUMENT_SELECTION_DB[variable][precision]
        
        st.divider()
        st.subheader(f"🎯 Recomendación: {recomendacion['instrumento']}")
        
        ic1, ic2 = st.columns([1, 2])
        ic1.image(recomendacion['imagen'], use_column_width=True)
        
        with ic2:
            st.markdown(recomendacion['descripcion'])
            
            # Additional details
            if 'costo' in recomendacion:
                cost_col, acc_col = st.columns(2)
                cost_col.metric("💰 Costo Típico", recomendacion['costo'])
                acc_col.metric("🎯 Exactitud", recomendacion['exactitud'])
        
        # Comparison table for the variable
        if st.checkbox("📊 Mostrar Comparación Completa"):
            comparison_data = []
            for prec_level, details in INSTRUMENT_SELECTION_DB[variable].items():
                comparison_data.append({
                    'Tipo': details['instrumento'],
                    'Aplicación': prec_level,
                    'Costo': details.get('costo', 'N/A'),
                    'Exactitud': details.get('exactitud', 'N/A')
                })
            
            st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)

    # Enhanced P&ID symbols with search functionality
    with st.expander("**📚 Biblioteca de Símbolos P&ID Ampliada**"):
        # Search functionality
        search_term = st.text_input("🔍 Buscar símbolo:", placeholder="Ej: válvula, transmisor, etc.")
        
        for category, symbols in PID_SYMBOLS.items():
            # Filter symbols based on search
            if search_term:
                filtered_symbols = {name: url for name, url in symbols.items() 
                                  if search_term.lower() in name.lower() or search_term.lower() in category.lower()}
            else:
                filtered_symbols = symbols
            
            if filtered_symbols:  # Only show category if it has matching symbols
                st.subheader(category)
                cols = st.columns(4)
                for i, (name, url) in enumerate(filtered_symbols.items()):
                    with cols[i % 4]:
                        st.image(url, caption=name, use_column_width=True)
                st.markdown("---")

with tab3:
    st.header("🧠 Centro de Práctica y Exámenes")
    st.info("Pon a prueba tus conocimientos con ejercicios generados aleatoriamente. ¡Nunca verás dos veces el mismo problema!")
    
    quiz_type = st.selectbox("Elige qué tema quieres practicar:", [
        "Ejercicios de Escalamiento (Directo e Inverso)", 
        "Ejercicios de Cálculo de Error", 
        "Identificación de Tags (ISA-5.1)"
    ])
    
    # Initialize session state for statistics
    if 'quiz_stats' not in st.session_state:
        st.session_state.quiz_stats = {'correct': 0, 'total': 0}
    
    # Display statistics
    if st.session_state.quiz_stats['total'] > 0:
        accuracy = (st.session_state.quiz_stats['correct'] / st.session_state.quiz_stats['total']) * 100
        st.metric("📈 Tu Rendimiento", f"{accuracy:.1f}%", 
                 delta=f"{st.session_state.quiz_stats['correct']}/{st.session_state.quiz_stats['total']} correctas")
    
    st.divider()

    if "Ejercicios de Escalamiento" in quiz_type:
        st.subheader("📐 Problema de Escalamiento")
        
        if 'scaling_question' not in st.session_state:
            st.session_state.scaling_question = generate_scaling_quiz()
        
        question, options, correct_answer = st.session_state.scaling_question
        random.shuffle(options)
        
        user_answer = st.radio(f"**Problema:** {question}", options, key=f"scale_{correct_answer}")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("✅ Verificar Respuesta", key="verify_scale"):
                st.session_state.quiz_stats['total'] += 1
                if user_answer == correct_answer:
                    st.session_state.quiz_stats['correct'] += 1
                    st.markdown('<div class="success-box">🎉 ¡Cálculo perfecto! Excelente dominio del escalamiento.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-box">❌ Incorrecto. La respuesta correcta es: **{correct_answer}**</div>', unsafe_allow_html=True)
                    
                    # Show calculation steps
                    st.markdown("**💡 Pasos de la solución:**")
                    st.code("""
Fórmula de escalamiento:
OUT = ((PV - LRV_PV) / (URV_PV - LRV_PV)) × (URV_OUT - LRV_OUT) + LRV_OUT

Para conversión inversa:
PV = ((OUT - LRV_OUT) / (URV_OUT - LRV_OUT)) × (URV_PV - LRV_PV) + LRV_PV
                    """)
        
        with col_btn2:
            if st.button("➡️ Siguiente Ejercicio", key="next_scale"):
                st.session_state.scaling_question = generate_scaling_quiz()
                st.rerun()

    elif "Ejercicios de Cálculo de Error" in quiz_type:
        st.subheader("🎯 Problema de Exactitud y Error")
        
        if 'error_question' not in st.session_state:
            st.session_state.error_question = generate_error_quiz()
        
        question, options, correct_answer = st.session_state.error_question
        random.shuffle(options)
        
        user_answer = st.radio(f"**Problema:** {question}", options, key=f"error_{correct_answer}")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("✅ Verificar Respuesta", key="verify_error"):
                st.session_state.quiz_stats['total'] += 1
                if user_answer == correct_answer:
                    st.session_state.quiz_stats['correct'] += 1
                    st.markdown('<div class="success-box">🎉 ¡Correcto! Has calculado bien la incertidumbre.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-box">❌ Incorrecto. La respuesta correcta es: **{correct_answer}**</div>', unsafe_allow_html=True)
        
        with col_btn2:
            if st.button("➡️ Siguiente Ejercicio", key="next_error"):
                st.session_state.error_question = generate_error_quiz()
                st.rerun()

    elif "Identificación de Tags" in quiz_type:
        st.subheader("🏷️ Problema de Identificación ISA-5.1")
        
        if 'tag_question' not in st.session_state:
            st.session_state.tag_question = generate_tag_quiz()
        
        question, options, correct_answer = st.session_state.tag_question
        random.shuffle(options)
        
        user_answer = st.radio(f"**Problema:** {question}", options, key=f"tag_{correct_answer}")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("✅ Verificar Respuesta", key="verify_tag"):
                st.session_state.quiz_stats['total'] += 1
                if user_answer == correct_answer:
                    st.session_state.quiz_stats['correct'] += 1
                    st.markdown('<div class="success-box">🎉 ¡Excelente! Dominas la nomenclatura ISA-5.1.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-box">❌ Incorrecto. La respuesta correcta es: **{correct_answer}**</div>', unsafe_allow_html=True)
        
        with col_btn2:
            if st.button("➡️ Siguiente Ejercicio", key="next_tag"):
                st.session_state.tag_question = generate_tag_quiz()
                st.rerun()

st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <h4>🛠️ Asistente de Instrumentación Industrial v5.0</h4>
    <p>Desarrollado para ingenieros de instrumentación y control | Basado en estándares ISA</p>
    <p><em>Mejoras v5.0: Conversores de unidades, análisis de incertidumbre avanzado, estadísticas de práctica, búsqueda de símbolos</em></p>
</div>
""", unsafe_allow_html=True)
