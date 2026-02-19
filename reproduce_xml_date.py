import xml.etree.ElementTree as ET
import os

def strip_namespaces(elem):
    if elem.tag.startswith("{"):
        elem.tag = elem.tag.split("}", 1)[1]
    for child in elem:
        strip_namespaces(child)

def test_extraction(file_path):
    print(f"Testing {file_path}...")
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        strip_namespaces(root)
        
        print(f"Root tag: {root.tag}")
        
        if root.tag.endswith('AttachedDocument'):
            print("Found AttachedDocument")
            description = root.find(".//Attachment/ExternalReference/Description")
            if description is not None and description.text:
                print("Found Description with text")
                inner_xml = description.text.strip()
                inner_root = ET.fromstring(inner_xml)
                strip_namespaces(inner_root)
                print(f"Inner Root tag: {inner_root.tag}")
                print(f"Inner XML snippet (first 2000 chars): {inner_xml[:2000]}")
                
                # Test finding IssueDate
                # logic in xml_skill: self._get_text(root, "./IssueDate")
                issue_date = inner_root.find("./IssueDate")
                print(f"Direct Child IssueDate: {issue_date.text if issue_date is not None else 'Not Found'}")
                
                # Check where it actually is
                all_issue_dates = [elem.text for elem in inner_root.findall(".//IssueDate")]
                print(f"All IssueDates found in inner: {all_issue_dates}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_extraction("invoices_input/02. FEBRERO PRUEBA/ad0900260602016260000433b.xml")
