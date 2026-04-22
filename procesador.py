import json
import google.generativeai as genai

def configurar_api(api_key):
    genai.configure(api_key=api_key)

def extraer_calamares_y_preguntas(texto_medico):
    """
    Envía el texto bruto a Gemini y retorna un diccionario estructurado.
    """
    # Modelo actualizado a la versión más reciente soportada por la API
    model = genai.GenerativeModel(
        'gemini-1.5-flash-latest',
        generation_config={"response_mime_type": "application/json"}
    )
    
    prompt = f"""
    Eres un asistente médico experto. Analiza el siguiente apunte o caso clínico y extrae la información en un objeto JSON estricto con esta estructura exacta:
    {{
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

    Extrae entre 3 y 5 flashcards de alto rendimiento. Si una categoría de los 'calamares' no se menciona en el texto, déjala como "No especificado".

    Texto médico:
    {texto_medico}
    """
    
    respuesta = model.generate_content(prompt)
    return json.loads(respuesta.text)
