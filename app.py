import os
import requests
import streamlit as st
from dotenv import load_dotenv
from google import genai
from streamlit_lottie import st_lottie

# Cargar variables desde el archivo .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ No se encontró la GEMINI_API_KEY en el archivo .env")
    st.stop()

# Inicializar cliente de Gemini
client = genai.Client(api_key=api_key)

# Configuración de la página
st.set_page_config(
    page_title="Lumi - Tu compañero de estudio",
    page_icon="⚪",
    layout="centered"
)

# Función para cargar animaciones Lottie desde una URL
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# Cargar animación de robot tierno / compañero de estudio
lottie_lumi = load_lottieurl("https://lottie.host/801a61e7-8b09-408a-b851-f7623a9b1c70/vYnZ3pX9kQ.json")

# Estilos CSS
st.markdown("""
    <style>
    .main {
        background-color: #F7F9FC;
    }
    .stButton>button {
        background-color: #4A90E2;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        width: 100%;
    }
    .lumi-card {
        background-color: #FFFFFF;
        color: #1E293B !important;
        padding: 20px;
        border-radius: 18px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 2px solid #E1E8ED;
        margin-bottom: 15px;
        font-size: 16px;
        line-height: 1.5;
    }
    .lumi-card b {
        color: #0F172A !important;
    }
    </style>
""", unsafe_allow_html=True)

SYSTEM_PROMPT = """
Eres Lumi, un robot asistente de aprendizaje inflable, suave, cálido y highly empático (inspirado en Baymax).
Tu meta es ayudar a estudiantes que se sienten abrumados o perdidos.

Reglas de interacción:
1. Tu tono es calmado, tierno, conciso y estructurado.
2. NUNCA entregues bloques gigantes de texto. Desglosa todo en micro-pasos de máximo 2 oraciones.
3. Valida siempre la emoción del estudiante antes de pasar al contenido académico.
4. Usa analogías simples y preguntas de verificación al final de cada paso.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []
if "streak" not in st.session_state:
    st.session_state.streak = 1

# Mostrar mascota animada arriba
if lottie_lumi:
    st_lottie(lottie_lumi, height=160, key="lumi_anim")

# Encabezado del MVP
st.markdown("<h3 style='text-align: center; color: #1E293B;'>⚪ Lumi</h3>", unsafe_allow_html=True)
st.caption(f"🔥 Racha actual: {st.session_state.streak} día(s) de avance")

st.markdown("""
<div class="lumi-card">
    <b>Lumi:</b> Hola. Soy Lumi, tu compañero de estudio personal. 
    He detectado que aprender puede ser abrumador a veces. Estoy aquí para cuidar de tu proceso.
</div>
""", unsafe_allow_html=True)

# Triaje emocional
st.markdown("**¿Cómo te sientes con respecto a tu estudio hoy?**")
col1, col2, col3 = st.columns(3)

mood = None
with col1:
    if st.button("🤯 Abrumado"):
        mood = "muy abrumado y bloqueado"
with col2:
    if st.button("😕 Confundido"):
        mood = "confundido con un tema específico"
with col3:
    if st.button("😴 Sin ganas"):
        mood = "con baja motivación y cansado"

# Entrada del tema a estudiar
topic = st.text_input("¿Qué tema o tarea necesitas abordar hoy?", placeholder="Ej. Estadísticas, Integrales por partes, Mitosis...")

if st.button("Empezar paso a paso con Lumi") and topic:
    user_prompt = f"Estado emocional del estudiante: {mood if mood else 'Normal'}. Tema a aprender/abordar: {topic}."
    
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    
    with st.spinner("Lumi está preparando una ruta suave para ti..."):
        prompt_completo = f"{SYSTEM_PROMPT}\n\nInstrucción del usuario:\n{user_prompt}"
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_completo
        )
        lumi_reply = response.text
        st.session_state.messages.append({"role": "assistant", "content": lumi_reply})

# Historial de conversación
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.markdown(f"""
        <div class="lumi-card">
            <b>⚪ Lumi:</b><br>{msg['content']}
        </div>
        """, unsafe_allow_html=True)

# Input para interacción continua
if len(st.session_state.messages) > 0:
    user_input = st.chat_input("Responde a Lumi o hazle una pregunta...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        historial_texto = f"{SYSTEM_PROMPT}\n\nHistorial de la conversación:\n"
        for m in st.session_state.messages:
            role_name = "Estudiante" if m["role"] == "user" else "Lumi"
            historial_texto += f"{role_name}: {m['content']}\n"
        
        with st.spinner("Lumi procesando..."):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=historial_texto
            )
            lumi_reply = response.text
            st.session_state.messages.append({"role": "assistant", "content": lumi_reply})
            st.rerun()