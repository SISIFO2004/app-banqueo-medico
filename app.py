import streamlit as st
import PyPDF2
from procesador import configurar_api, extraer_calamares_y_preguntas

st.set_page_config(page_title="Banqueo Médico", layout="wide")

# Inicializar sesión
if "data_procesada" not in st.session_state:
    st.session_state.data_procesada = None

st.title("🦑 Sistema de Banqueo y Calamares Mentales")

# 1. Carga de documento
archivo_subido = st.file_uploader("Sube tu apunte o caso clínico (PDF)", type=["pdf"])

texto_extraido = ""
if archivo_subido is not None:
    lector = PyPDF2.PdfReader(archivo_subido)
    for pagina in lector.pages:
        texto_extraido += pagina.extract_text() + "\n"

# 2. Procesamiento
if st.button("Procesar Apunte", type="primary"):
    if not texto_extraido:
        st.error("Sube un documento válido con texto.")
    else:
        with st.spinner("Desmembrando la información..."):
            # Llama a la API Key oculta en los secretos de Streamlit
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
                configurar_api(api_key)
                st.session_state.data_procesada = extraer_calamares_y_preguntas(texto_extraido)
            except KeyError:
                st.error("Falta configurar la API Key en los secretos de Streamlit.")
            except Exception as e:
                st.error(f"Error en el procesamiento: {e}")

# 3. Visualización
if st.session_state.data_procesada:
    data = st.session_state.data_procesada
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("🦑 Calamares")
        for categoria, contenido in data.get("calamares", {}).items():
            st.subheader(categoria)
            st.info(contenido)
                
    with col2:
        st.header("🗂️ Flashcards")
        for idx, card in enumerate(data.get("flashcards", [])):
            with st.expander(f"Pregunta {idx + 1}: {card['pregunta']}"):
                st.success(card['respuesta'])
