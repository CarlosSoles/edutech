import streamlit as st
import json
import base64
import io
import os
from google import genai
from google.genai import types
from PIL import Image
from src.core.prompts import PROMPT_GEMINI_EXTRACTOR

class AgentGemini:
    def __init__(self):
        # Obtenemos la llave de los secrets o de las variables de entorno
        api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró GEMINI_API_KEY")
            
        self.client = genai.Client(api_key=api_key)
        # Usamos flash porque es ultra rápido y barato/gratis para imágenes + texto
        self.model_name = "gemini-2.5-flash"

    def process_cuaderno(self, image: Image.Image) -> dict:
        """
        Envía la imagen del cuaderno de campo y el prompt maestro a Gemini.
        Gemini hace OCR y Parsing simultáneo.
        Retorna el diccionario JSON estructurado.
        """
        # Convertir la imagen a bytes y manejar transparencias
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
            
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        image_bytes = img_byte_arr.getvalue()

        # Enviar petición a Gemini 1.5 Flash
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/jpeg',
                ),
                PROMPT_GEMINI_EXTRACTOR
            ]
        )

        raw_result = response.text
        
        # Limpiar backticks si el modelo decide incluirlos a pesar de las instrucciones
        if raw_result.startswith("```json"):
            raw_result = raw_result.replace("```json", "", 1)
        if raw_result.startswith("```"):
            raw_result = raw_result.replace("```", "", 1)
        if raw_result.endswith("```"):
            raw_result = raw_result[:-3]

        raw_result = raw_result.strip()

        try:
            parsed_data = json.loads(raw_result)
            return parsed_data
        except json.JSONDecodeError as e:
            raise ValueError(f"Error al parsear el JSON de Gemini. Respuesta cruda: {raw_result}") from e

class AgentAdvisor:
    def __init__(self):
        api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("No se encontró GEMINI_API_KEY")
            
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"
        
    def generate_advice(self, context: str) -> str:
        prompt = f"""Escribe una asesoría pedagógica basada EXCLUSIVAMENTE en el siguiente contexto del alumno.
ESTRICTAMENTE PROHIBIDO:
- Usar saludos (ej. "Hola", "Buenos días").
- Usar introducciones o rodeos verbales (ej. "Basado en los datos...", "Aquí tienes la asesoría...").
- Inventar datos que no estén en el contexto.

TU RESPUESTA DEBE TENER EXACTAMENTE ESTA ESTRUCTURA FIJA:

1. Diagnóstico Breve: (tu análisis rápido aquí)
2. Dinámica Sugerida: (tu sugerencia aquí)
3. Qué Observar: (tu criterio de logro aquí)

CONTEXTO DEL ALUMNO Y REGISTROS HISTÓRICOS:
{context}
"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[prompt]
        )
        return response.text.strip()
