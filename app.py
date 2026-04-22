import streamlit as st
import PyPDF2
from procesador import configurar_api, extraer_calamares_y_preguntas

st.set_page_config(page_title="Banqueo Médico", layout="wide")

# Inicializar sesión
if "data_procesada" not in st.session_state:
    st.session_state.data_procesada = None

st.title("🦑 Sistema de Banqueo y Calamares Mentales")

# --- CONTROLES ANTES DE CARGAR EL APUNTE ---
st.markdown("### ⚙️ Configuración del Banqueo")
col_ctrl1, col_ctrl2 = st.columns(2)

with col_ctrl1:
    num_preguntas = st.slider("Número de Flashcards a generar", min_value=1, max_value=20, value=5)
    
with col_ctrl2:
    tema_sugerido = st.text_input("Tema sugerido para las flashcards (Opcional)", placeholder="Ej: Tratamiento, Anatomía. Si está vacío, serán todos los temas.")

# Lógica del tema por defecto
tema_final = tema_sugerido if tema_sugerido.strip() != "" else "todos los temas"

st.markdown("---")
# ------------------------------------------

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
        st.error("Por favor, sube un documento PDF válido primero.")
    else:
        with st.spinner(f"Desmembrando la información y creando {num_preguntas} flashcards sobre '{tema_final}'..."):
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
                configurar_api(api_key)
                # Pasamos las variables al procesador
                st.session_state.data_procesada = extraer_calamares_y_preguntas(texto_extraido, num_preguntas, tema_final)
            except KeyError:
                st.error("Falta configurar la API Key en los secretos de Streamlit.")
            except Exception as e:
                st.error(f"Error en el procesamiento: {e}")

# 3. Visualización
if st.session_state.data_procesada:
    data = st.session_state.data_procesada
    
    # Mostrar el tema que detectó la IA
    tema_detectado = data.get("tema_general", "No identificado")
    st.success(f"📌 **Tema central detectado en el documento:** {tema_detectado}")
    st.write("") 
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("🦑 Calamares")
        for categoria, contenido in data.get("calamares", {}).items():
            if contenido and contenido != "No especificado":
                st.subheader(categoria)
                st.info(contenido)
                
    with col2:
        st.header("🗂️ Flashcards")
        for idx, card in enumerate(data.get("flashcards", [])):
            with st.expander(f"Pregunta {idx + 1}: {card.get('pregunta', '')}"):
                st.success(card.get('respuesta', ''))
