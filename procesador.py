import json
import google.generativeai as genai

def configurar_api(api_key):
    genai.configure(api_key=api_key)

def extraer_calamares_y_preguntas(texto_medico, imagenes=None, num_preguntas=5, tema_especifico="todos los temas"):
    """
    Envía texto e imágenes a Gemini para análisis multimodal y retorna un JSON estructurado.
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
            "Diagnostico": "Resumen de sospecha o diagnóstico definitivo",
            "Tratamiento": "Manejo médico, quirúrgico o de primera línea",
            "Etiologia": "Causas o factores de riesgo",
            "Clinica": "Signos y síntomas principales",
            "Pruebas": "Estudios de imagen, laboratorio o gold standard"
        }},
        "flashcards": [
            {{
                "pregunta": "Pregunta de banqueo directa basada en un dato clave del texto o de las imágenes",
                "respuesta": "Respuesta corta y precisa"
            }}
        ]
    }}

    Instrucciones críticas:
    1. Extrae exactamente {num_preguntas} flashcards.
    2. Enfoca las preguntas principalmente en: {tema_especifico}.
    3. Asegúrate de incluir datos extraídos de las tablas o imágenes si son relevantes para el banqueo.
    4. Si una categoría de los 'calamares' no se menciona, déjala como "No especificado".

    Texto médico:
    {texto_medico}
    """
    
    # Empaquetamos todo (texto + imágenes) en una lista para el modelo
    contenido = [prompt]
    if imagenes:
        contenido.extend(imagenes)
        
    respuesta = model.generate_content(contenido)
    return json.loads(respuesta.text)
