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
    Eres un asistente médico experto. Analiza el texto y tablas.
    Genera un JSON con esta estructura de valores de texto simple:
    {{
        "tema_general": "...",
        "calamares": {{
            "Etiologia": "Texto con viñetas y mnemotecnia al final",
            "Clinica": "Texto con viñetas y mnemotecnia al final",
            "Diagnostico": "Texto con viñetas y mnemotecnia al final",
            "Pruebas": "Texto con viñetas y mnemotecnia al final",
            "Tratamiento": "Texto con viñetas y mnemotecnia al final"
        }},
        "flashcards": [ {{"pregunta": "...", "respuesta": "..."}} ]
    }}

    REGLAS CRÍTICAS DE FORMATO:
    1. No devuelvas diccionarios dentro de 'calamares', solo cadenas de texto (strings).
    2. Usa guiones (-) para cada punto.
    3. Usa saltos de línea reales (\\n) entre cada punto.
    4. Al final de cada sección, añade: \\n\\n💡 **Mnemotecnia:** [Texto de la mnemotecnia].
    5. No te saltes ningún dato de las tablas. Genera {num_preguntas} flashcards.

    Texto: {texto_medico}
    """
    
    contenido = [prompt]
    if imagenes:
        contenido.extend(imagenes)
        
    configuracion_seguridad = {
        category: HarmBlockThreshold.BLOCK_NONE 
        for category in [HarmCategory.HARM_CATEGORY_HATE_SPEECH, HarmCategory.HARM_CATEGORY_HARASSMENT, 
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT]
    }
        
    respuesta = model.generate_content(contenido, safety_settings=configuracion_seguridad)
    return json.loads(respuesta.text)
