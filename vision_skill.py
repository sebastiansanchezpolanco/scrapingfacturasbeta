import os
import time
import json
import ast
import re
from google import genai
from google.genai import types
from typing import Dict, Optional

class VisionSkill:
    """
    Skill to extract invoice data using Google Gemini 2.0 Flash (or latest).
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        if not self.api_key:
            # We will handle the missing key gracefully here to allow the script to load,
            # but extract_data will fail if not set.
            print("WARNING: GOOGLE_API_KEY not set.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.0-flash" 

    def extract_data(self, file_path: str) -> Dict:
        """
        Uploads file to Gemini and requests JSON extraction.
        """
        if not self.api_key:
             print("Error: GOOGLE_API_KEY is missing. Cannot process file.")
             return {}

        try:
            mime_type = self._get_mime_type(file_path)
            
            # Comprehensive prompt for full data extraction
            prompt = """
            Eres un asistente administrativo experto y meticuloso. Analiza este documento (factura/recibo).
            Tu objetivo es extraer la mayor cantidad de información posible.
            
            Extrae los siguientes datos en formato JSON estrictamente válido.
            
            Campos requeridos (usa null si no encuentras el valor):
            - proveedor_nombre (string): Nombre legal del emisor.
            - proveedor_nit (string): NIT, RUT, CUIT o identificación fiscal del emisor. Intenta encontrarlo.
            - proveedor_direccion (string): Dirección física.
            - proveedor_telefono (string): Teléfono de contacto.
            - proveedor_ciudad (string): Ciudad del emisor.
            
            - factura_numero (string): Número consecutivo de la factura.
            - fecha_emision (string): Fecha de la factura (YYYY-MM-DD).
            - fecha_vencimiento (string): Fecha de pago/vencimiento (YYYY-MM-DD).
            
            - descripcion_general (string): Resumen breve de qué se está cobrando (ej. "Servicios de aseo", "Mantenimiento", "Compra papelería").
            
            - moneda (string): COP, USD, EUR, etc.
            - base_imponible (float): Subtotal antes de impuestos.
            - impuestos (float): Valor total de IVA u otros impuestos.
            - total (float): Valor total a pagar.
            - cufe (string): CUFE o CUDE (Código Único de Facturación Electrónica). Cadena larga alfanumérica.

            Devuelve SOLO el objeto JSON, nada de markdown ni explicaciones.
            """

            try:
                print(f"Uploading {os.path.basename(file_path)} to Google GenAI...")
            except UnicodeEncodeError:
                print(f"Uploading {os.path.basename(file_path).encode('utf-8', 'replace').decode('utf-8')} to Google GenAI...")
            
            # Upload file
            myfile = self.client.files.upload(file=file_path)
            
            # Polling to wait for processing (mostly for PDFs)
            while myfile.state.name == "PROCESSING":
                print("Processing file remotely...")
                time.sleep(2)
                myfile = self.client.files.get(name=myfile.name)

            if myfile.state.name == "FAILED":
                raise ValueError("Gemini File processing failed.")

            print("Generating extraction...")
            
            # Simple retry mechanism for Rate Limits
            max_retries = 3
            base_delay = 10 # seconds
            
            for attempt in range(max_retries):
                try:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=[myfile, prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        )
                    )
                    break
                except Exception as e:
                    if "429" in str(e) or "ResourceExhausted" in str(e):
                        if attempt == max_retries - 1:
                            raise e
                        
                        sleep_time = base_delay * (2 ** attempt) + (time.time() % 1)
                        print(f"Rate limit hit. Retrying in {sleep_time:.2f}s...")
                        time.sleep(sleep_time)
                    else:
                        raise e
            
            # Response handling for google-genai
            # It might return a parsed object if response_mime_type is JSON, or text.
            # With google-genai and response_mime_type="application/json", it often validates JSON.
            
            if not response.text:
                print("Empty response from model.")
                return {}

            text_response = response.text.strip()
            # Cleanup just in case
            import re
            
            # Extract JSON block using regex
            json_match = re.search(r'\{.*\}|\[.*\]', text_response, re.DOTALL)
            if json_match:
                text_response = json_match.group(0)
            
            try:
                data = json.loads(text_response)
            except json.JSONDecodeError:
                # Fallback 1: try to clean common markdown issues if raw load fails
                cleaned = text_response.replace("```json", "").replace("```", "").strip()
                try:
                    data = json.loads(cleaned)
                except json.JSONDecodeError:
                    # Fallback 2: python literal eval (handles single quotes)
                    try:
                        data = ast.literal_eval(cleaned)
                    except (ValueError, SyntaxError):
                        print(f"Failed to parse JSON even with fallbacks: {text_response[:100]}...")
                        return {}

            # Handle list response (sometimes model returns [{}])
            if isinstance(data, list):
                if data:
                    data = data[0]
                else:
                    return {}
            
            return data

        except Exception as e:
            try:
                print(f"Error extracting data from {file_path} with Gemini: {e}")
            except UnicodeEncodeError:
                 safe_path = file_path.encode('utf-8', 'replace').decode('utf-8')
                 print(f"Error extracting data from {safe_path} with Gemini: {e}")
            raise e

    def _get_mime_type(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        if ext == '.pdf': return 'application/pdf'
        if ext in ['.jpg', '.jpeg']: return 'image/jpeg'
        if ext == '.png': return 'image/png'
        if ext == '.webp': return 'image/webp'
        return 'application/octet-stream'
