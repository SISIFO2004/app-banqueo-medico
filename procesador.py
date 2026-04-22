import json
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

def configurar_api(api_key):
    genai.configure(api_key=api_key)

def extraer_calamares_y_preguntas(texto_medico, imagenes=None, num_preguntas=30, tema_especifico="todos los temas"):
    if imagenes is None:
        imagenes = []
        
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )
    
    prompt = f"""
    Eres un asistente médico experto. Analiza el texto médico y las imágenes/tablas adjuntas. Extrae la información en un objeto JSON estricto con esta estructura exacta:
    {{
        "tema_general": "Identifica el tema principal en máximo 5 palabras",
        "calamares": {{
            "Diagnostico": {{ "contenido": "...", "mnemotecnia": "..." }},
            "Tratamiento": {{ "contenido": "...", "mnemotecnia": "..." }},
            "Etiologia": {{ "contenido": "...", "mnemotecnia": "..." }},
            "Clinica": {{ "contenido": "...", "mnemotecnia": "..." }},
            "Pruebas": {{ "contenido": "...", "mnemotecnia": "..." }}
        }},
        "flashcards": [
            {{ "pregunta": "...", "respuesta": "..." }}
        ]
    }}

    Instrucciones críticas:
    1. CONTENIDO: Usa obligatoriamente guiones (-) y negritas para resaltar datos clave. Prohibido bloques de texto.
    2. MNEMOTECNIAS: Crea una mnemotecnia específica para cada sección que ayude a recordar los puntos clave de ese apartado.
    3. TABLAS: Extrae e integra cada dato de las tablas/imágenes en la sección correspondiente. No omitas nada rentable para el examen.
    4. FLASHCARDS: Genera exactamente {num_preguntas} enfocadas en {tema_especifico}.

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
        
    respuesta = model.generate_content(contenido, safety_settings=configuracion_seguridad)
    return json.loads(respuesta.text)
