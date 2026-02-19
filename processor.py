import os
import asyncio
from vision_skill import VisionSkill
from xml_skill import XmlSkill

class InvoiceProcessor:
    def __init__(self, api_key: str):
        self.vision = VisionSkill(api_key)
        self.xml_skill = XmlSkill()

    async def process_file(self, file_path: str) -> dict:
        """
        Processes a single file:
        1. Checks for companion XML file -> extract via XmlSkill
        2. If no XML or failure -> extract via VisionSkill (Gemini)
        """
        basename = os.path.basename(file_path)
        print(f"Processing: {basename}...")

        # 1. Try XML Strategy first
        # Assumption: XML file has same basename but .xml extension
        base_no_ext = os.path.splitext(file_path)[0]
        xml_path = base_no_ext + ".xml"
        
        if os.path.exists(xml_path):
            print(f"   found companion XML: {os.path.basename(xml_path)}")
            try:
                # XML parsing is fast/sync, no need for executor usually, 
                # but good practice to keep main loop free
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, self.xml_skill.extract_data, xml_path)
                
                if data:
                    print(f"   extracted data from XML successfully.")
                    # XML extraction already returns the mapped dict structure we need
                    # XML extraction already returns the mapped dict structure we need
                    return self._normalize(data)
            except Exception as e:
                print(f"   XML parsing failed, falling back to Vision: {e}")
        
        # 2. Vision Strategy (Fallback)
        try:
            print(f"   using Vision API (Gemini)...")
            
            # Since VisionSkill uses blocking network calls (genai lib is sync mostly), 
            # we should run it in a thread executor to keep asyncio happy.
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self.vision.extract_data, file_path)
            
            if not data:
                print(f"No data extracted from {basename}")
                return {
                    "archivo": basename,
                    "estado": "FALLIDO",
                    "nota": "No se pudo extraer JSON valido"
                }

            # Map the fields to match our excel structure
            mapped_data = {
                "archivo": basename,
                "estado": "EXITOSO",
                "proveedor": data.get("proveedor_nombre"),
                "nit": data.get("proveedor_nit"),
                "direccion": data.get("proveedor_direccion"),
                "telefono": data.get("proveedor_telefono"),
                "ciudad": data.get("proveedor_ciudad"),
                "factura_numero": data.get("factura_numero"),
                "fecha": data.get("fecha_emision"),
                "fecha_vencimiento": data.get("fecha_vencimiento"),
                "descripcion": data.get("descripcion_general"),
                "moneda": data.get("moneda"),
                "base": data.get("base_imponible"),
                "impuestos": data.get("impuestos"),
                "total": data.get("total"),
                "cufe": data.get("cufe")
            }
            
            
            return self._normalize(mapped_data)
        except Exception as e:
            print(f"Failed to process {file_path}: {e}")
            return {
                "archivo": basename,
                "estado": "FALLIDO",
                "nota": str(e)
            }
            
    def _normalize(self, data: dict) -> dict:
        from utils import normalize_data
        return normalize_data(data)
