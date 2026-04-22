import json
import google.generativeai as genai

def configurar_api(api_key):
    genai.configure(api_key=api_key)

def extraer_calamares_y_preguntas(texto_medico, num_preguntas=5, tema_especifico="todos los temas"):
    """
    Envía el texto bruto a Gemini y retorna un diccionario estructurado.
    """
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )
    
    prompt = f"""
    Eres un asistente médico experto. Analiza el siguiente apunte o caso clínico y extrae la información en un objeto JSON estricto con esta estructura exacta:
    {{
        "tema_general": "Identifica el tema, patología o diagnóstico principal del documento en máximo 5 palabras",
        "calamares": {{
            "Diagnostico": "Resumen de sospecha o diagnóstico definitivo",
            "Tratamiento": "Manejo médico, quirúrgico o de primera línea",
            "Etiologia": "Causas o factores de riesgo",
            "Clinica": "Signos y síntomas principales",
            "Pruebas": "Estudios de imagen, laboratorio o gold standard"
        }},
        "flashcards": [
            {{
                "pregunta": "Pregunta de banqueo directa basada en un dato clave",
                "respuesta": "Respuesta corta y precisa"
            }}
        ]
    }}

    Instrucciones críticas:
    1. Extrae exactamente {num_preguntas} flashcards.
    2. Enfoca las preguntas de las flashcards principalmente en: {tema_especifico}.
    3. Si una categoría de los 'calamares' no se menciona en el texto, déjala como "No especificado".

    Texto médico:
    {texto_medico}
    """
    
    respuesta = model.generate_content(prompt)
    return json.loads(respuesta.text)
