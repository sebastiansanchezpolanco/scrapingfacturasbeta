from xml_skill import XmlSkill
import os

def test_skill_extraction(file_path):
    print(f"Testing XmlSkill on {os.path.basename(file_path)}...")
    skill = XmlSkill()
    data = skill.extract_data(file_path)
    print(f"Extracted Date: {data.get('fecha_emision')}")
    print(f"Extracted Due Date: {data.get('fecha_vencimiento')}")
    print(f"Full Data: {data}")

if __name__ == "__main__":
    # Test on the file that was failing in Excel
    test_skill_extraction("invoices_input/02. FEBRERO PRUEBA/ad0900260602016260000433b.xml")
