import streamlit as st
import PyPDF2
from pptx import Presentation
from PIL import Image
import io
from procesador import configurar_api, extraer_calamares_y_preguntas

st.set_page_config(page_title="Banqueo Médico Multimodal", layout="wide")

if "data_procesada" not in st.session_state:
    st.session_state.data_procesada = None

# --- NUEVA FUNCIÓN AUTOMÁTICA ---
def es_tabla_o_esquema(imagen):
    """
    Analiza la cantidad de colores únicos.
    Tablas = pocos colores. Fotos clínicas = miles de colores.
    """
    try:
        # Hacemos una miniatura rápida para no saturar la memoria
        img_analisis = imagen.copy()
        img_analisis.thumbnail((150, 150))
        # Intentamos obtener hasta 3000 colores únicos
        # Si la imagen tiene más de 3000 colores, getcolors() devuelve None (es una foto real)
        colores = img_analisis.getcolors(3000)
        
        if colores is None:
            return False # Es una foto clínica (compleja)
        return True # Es una tabla, gráfico o texto (plana)
    except Exception:
        return True # Ante la duda, la aprobamos
# --------------------------------

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

# --- CARGA DE DOCUMENTOS ---
archivo_subido = st.file_uploader("Sube tu apunte (PDF o PPTX)", type=["pdf", "pptx"])

texto_extraido = ""
imagenes_brutas = []

if archivo_subido is not None:
    nombre_archivo = archivo_subido.name.lower()
    
    if nombre_archivo.endswith(".pdf"):
        lector = PyPDF2.PdfReader(archivo_subido)
        for pagina in lector.pages:
            if pagina.extract_text():
                texto_extraido += pagina.extract_text() + "\n"
                
    elif nombre_archivo.endswith(".pptx"):
        prs = Presentation(archivo_subido)
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    texto_extraido += shape.text + "\n"
                
                if hasattr(shape, "image"):
                    image_bytes = shape.image.blob
                    imagen = Image.open(io.BytesIO(image_bytes))
                    if imagen.mode != 'RGB':
                        imagen = imagen.convert('RGB')
                    imagenes_brutas.append(imagen)

    # --- FILTRO AUTOMÁTICO DE IMÁGENES ---
    imagenes_a_enviar = []
    if imagenes_brutas:
        st.info("🤖 **IA de Pre-filtrado activa:** La aplicación ha intentado identificar y marcar automáticamente las tablas útiles, desmarcando las fotos clínicas.")
        
        columnas = st.columns(4) 
        for idx, img in enumerate(imagenes_brutas):
            col_idx = idx % 4
            
            # ¡AQUÍ ESTÁ LA MAGIA AUTOMÁTICA!
            parece_util = es_tabla_o_esquema(img)
            
            with columnas[col_idx]:
                st.image(img, use_container_width=True)
                # La casilla toma el valor dictado por nuestra función matemática
                incluir = st.checkbox(f"Incluir", value=parece_util, key=f"img_{idx}")
                
                if incluir:
                    imagenes_a_enviar.append(img)
                if not parece_util:
                    st.caption("🔴 *Detectado como Foto*")

    # --- PROCESAMIENTO ---
    if st.button("Procesar Apunte", type="primary"):
        if not texto_extraido and not imagenes_a_enviar:
            st.error("Sube un documento válido con texto o selecciona al menos una imagen.")
        else:
            with st.spinner(f"Analizando {len(imagenes_a_enviar)} tablas/imágenes y el texto para crear {num_preguntas} flashcards..."):
                try:
                    api_key = st.secrets["GEMINI_API_KEY"]
                    configurar_api(api_key)
                    st.session_state.data_procesada = extraer_calamares_y_preguntas(
                        texto_extraido, imagenes_a_enviar, num_preguntas, tema_final
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
