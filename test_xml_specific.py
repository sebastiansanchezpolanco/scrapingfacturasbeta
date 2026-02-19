from xml_skill import XmlSkill
import os

def test_specific():
    file_path = "invoices_input/02. FEBRERO PRUEBA/dian_FEP1137009.xml"
    print(f"Testing {file_path}...")
    
    skill = XmlSkill()
    data = skill.extract_data(file_path)
    
    print(f"Extracted Data: {data}")
    print(f"Total: {data.get('total')}")
    print(f"Type of Total: {type(data.get('total'))}")

if __name__ == "__main__":
    test_specific()
