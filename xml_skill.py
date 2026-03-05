import xml.etree.ElementTree as ET
import os
from typing import Dict, Optional

class XmlSkill:
    """
    Skill to extract invoice data from UBL 2.1 XML files (DIAN Colombia Standard).
    """

    def extract_data(self, file_path: str) -> Dict:
        """
        Parses an XML file and returns a dictionary with extracted fields.
        Returns None or empty dict if parsing fails or not a valid invoice.
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Handle namespaces by stripping them for easier searching
            # This is a pragmatic, non-validating approach
            self._strip_namespaces(root)

            # Check if it's an AttachedDocument (container) or Invoice directly
            if root.tag.endswith('AttachedDocument'):
                # The actual Invoice is inside cbc:Description as CDATA string
                # path: AttachedDocument -> Attachment -> ExternalReference -> Description
                # Since we stripped namespaces, we search by tag name
                description = root.find(".//Attachment/ExternalReference/Description")
                if description is not None and description.text:
                    # Parse the inner XML
                    try:
                        inner_xml = description.text.strip()
                        inner_root = ET.fromstring(inner_xml)
                        self._strip_namespaces(inner_root)
                        return self._parse_invoice(inner_root, os.path.basename(file_path))
                    except ET.ParseError as e:
                        print(f"Error parsing inner XML in {os.path.basename(file_path)}: {e}")
                        # Print snippet for debugging
                        print(f"Snippet: {inner_xml[:100]}...")
                        return {}
            elif root.tag.endswith('Invoice'):
                 return self._parse_invoice(root, os.path.basename(file_path))
            
            # If we reach here, it might be a different dict type or failed to find invoice
            return {}

        except Exception as e:
            print(f"Error parsing XML {file_path}: {e}")
            return {}

    def _strip_namespaces(self, elem):
        """Removes namespaces from element tags in-place."""
        if elem.tag.startswith("{"):
            elem.tag = elem.tag.split("}", 1)[1]
        for child in elem:
            self._strip_namespaces(child)

    def _parse_invoice(self, root: ET.Element, filename: str) -> Dict:
        """Extracts fields from a raw Invoice element tree."""
        data = {
            "archivo": filename,
            "estado": "EXITOSO (XML)",
            "proveedor": self._get_text(root, ".//AccountingSupplierParty/Party/PartyTaxScheme/RegistrationName"),
            "nit": self._get_text(root, ".//AccountingSupplierParty/Party/PartyTaxScheme/CompanyID"),
            "direccion": self._get_text(root, ".//AccountingSupplierParty/Party/PhysicalLocation/Address/AddressLine/Line"),
            "telefono": self._get_text(root, ".//AccountingSupplierParty/Party/Contact/Telephone"),
            "ciudad": self._get_text(root, ".//AccountingSupplierParty/Party/PhysicalLocation/Address/CityName"),
            
            "factura_numero": self._get_text(root, "./ID"),
            "fecha_emision": self._get_text(root, ".//IssueDate"),
            "fecha_vencimiento": self._get_text(root, ".//DueDate"),
            
            "descripcion": self._get_text(root, ".//InvoiceLine/Item/Description"), # First item description
            
            "moneda": self._get_text(root, "./DocumentCurrencyCode"),
            "base": self._get_float(root, ".//LegalMonetaryTotal/TaxExclusiveAmount"),
            "impuestos": self._get_float(root, ".//TaxTotal/TaxAmount"),
            "total": self._get_float(root, ".//LegalMonetaryTotal/PayableAmount"),
            "cufe": self._get_text(root, "./UUID")
        }
        
        # Fallback for description if empty
        if not data["descripcion"]:
             data["descripcion"] = "Factura de Venta"
             
        return data

    def _get_text(self, root, path) -> Optional[str]:
        el = root.find(path)
        return el.text.strip() if el is not None and el.text else None

    def _get_float(self, root, path) -> Optional[float]:
        text = self._get_text(root, path)
        if text:
            try:
                return float(text)
            except ValueError:
                return 0.0
        return 0.0
