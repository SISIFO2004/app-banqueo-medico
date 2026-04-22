import streamlit as st
import PyPDF2
from pptx import Presentation
from PIL import Image
import io
from procesador import configurar_api, extraer_calamares_y_preguntas

st.set_page_config(page_title="Banqueo Médico", layout="wide")

if "data_procesada" not in st.session_state:
    st.session_state.data_procesada = None

st.title("🦑 Sistema de Banqueo y Calamares Mentales")

# --- CONTROLES ---
st.markdown("### ⚙️ Configuración del Banqueo")
col_ctrl1, col_ctrl2 = st.columns(2)
with col_ctrl1:
    num_preguntas = st.slider("Número de Flashcards a generar", min_value=1, max_value=20, value=5)
with col_ctrl2:
    tema_sugerido = st.text_input("Tema sugerido (Opcional)", placeholder="Ej: Tratamiento. Si está vacío, serán todos.")

tema_final = tema_sugerido if tema_sugerido.strip() != "" else "todos los temas"
st.markdown("---")

# --- CARGA DE DOCUMENTOS (Ahora soporta PPTX) ---
archivo_subido = st.file_uploader("Sube tu apunte (PDF o PPTX)", type=["pdf", "pptx"])

texto_extraido = ""
imagenes_extraidas = []

if archivo_subido is not None:
    nombre_archivo = archivo_subido.name.lower()
    
    # Si es PDF, solo sacamos texto (por ahora)
    if nombre_archivo.endswith(".pdf"):
        lector = PyPDF2.PdfReader(archivo_subido)
        for pagina in lector.pages:
            texto_extraido += pagina.extract_text() + "\n"
            
    # Si es PPTX, sacamos texto e IMÁGENES
    elif nombre_archivo.endswith(".pptx"):
        prs = Presentation(archivo_subido)
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    texto_extraido += shape.text + "\n"
                # Extraer imágenes de la diapositiva
                if hasattr(shape, "image"):
                    image_bytes = shape.image.blob
                    imagen = Image.open(io.BytesIO(image_bytes))
                    imagenes_extraidas.append(imagen)
                    
        # Mostrar preview de lo que la app acaba de "ver"
        if imagenes_extraidas:
            with st.expander(f"🖼️ Se detectaron {len(imagenes_extraidas)} imágenes/tablas en las diapositivas"):
                # Mostramos miniaturas para que sepas qué está analizando
                st.image(imagenes_extraidas, width=150)

# --- PROCESAMIENTO ---
if st.button("Procesar Apunte", type="primary"):
    if not texto_extraido and not imagenes_extraidas:
        st.error("Por favor, sube un documento válido con texto o imágenes.")
    else:
        with st.spinner(f"Analizando texto e imágenes para crear {num_preguntas} flashcards..."):
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
                configurar_api(api_key)
                # Pasamos el texto y las imágenes a la IA
                st.session_state.data_procesada = extraer_calamares_y_preguntas(
                    texto_extraido, imagenes_extraidas, num_preguntas, tema_final
                )
            except KeyError:
                st.error("Falta configurar la API Key en los secretos de Streamlit.")
            except Exception as e:
                st.error(f"Error en el procesamiento: {e}")

# --- VISUALIZACIÓN ---
if st.session_state.data_procesada:
    data = st.session_state.data_procesada
    
    tema_detectado = data.get("tema_general", "No identificado")
    st.success(f"📌 **Tema central detectado:** {tema_detectado}")
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
