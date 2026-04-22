import json
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

def configurar_api(api_key):
    genai.configure(api_key=api_key)

def extraer_calamares_y_preguntas(texto_medico, imagenes=None, num_preguntas=30, tema_especifico="todos los temas"):
    """
    Envía texto e imágenes a Gemini para análisis multimodal y retorna un JSON estructurado,
    con los filtros de seguridad ajustados para permitir contenido médico.
    """
    if imagenes is None:
        imagenes = []
        
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )
    
    prompt = f"""
    Eres un asistente médico experto. Analiza el texto médico y las imágenes/tablas adjuntas. Extrae la información en un objeto JSON estricto con esta estructura exacta:
    {{
        "tema_general": "Identifica el tema, patología o diagnóstico principal en máximo 5 palabras",
        "calamares": {{
            "Diagnostico": "Resumen de sospecha o diagnóstico. Usa viñetas y negritas.",
            "Tratamiento": "Manejo médico/quirúrgico. Usa viñetas y negritas para separar fármacos y dosis.",
            "Etiologia": "Causas o factores de riesgo. Usa viñetas.",
            "Clinica": "Signos y síntomas principales. Usa viñetas.",
            "Pruebas": "Estudios de imagen o laboratorio. Usa viñetas.",
            "Mnemotecnias": "Crea 1 o 2 mnemotecnias originales, en español y muy fáciles de recordar para los datos más difíciles de este tema (ej. criterios, fármacos o clínica)."
        }},
        "flashcards": [
            {{
                "pregunta": "Pregunta de banqueo directa basada en un dato clave del texto o de las imágenes",
                "respuesta": "Respuesta corta y precisa"
            }}
        ]
    }}

    Instrucciones críticas y absolutas:
    1. FORMATO ORDENADO: El contenido de los 'calamares' DEBE estar obligatoriamente en formato de lista con guiones (-). Prohibido usar bloques de texto sólidos. Resalta con **negritas** las palabras clave.
    2. ATENCIÓN A LAS TABLAS: No te saltes ningún dato crucial que aparezca en las imágenes, clasificaciones o tablas adjuntas. Intégralos en los calamares y en las flashcards.
    3. Extrae exactamente {num_preguntas} flashcards.
    4. Enfoca las preguntas principalmente en: {tema_especifico}.
    5. Si una categoría no se menciona, déjala como "No especificado".

    Texto médico:
    {texto_medico}
    """
    
    contenido = [prompt]
    if imagenes:
        contenido.extend(imagenes)
        
    configuracion_seguridad = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
        
    respuesta = model.generate_content(
        contenido,
        safety_settings=configuracion_seguridad
    )
    
    return json.loads(respuesta.text)
