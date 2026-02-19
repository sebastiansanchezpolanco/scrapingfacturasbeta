
import asyncio
import os
from processor import InvoiceProcessor

async def test_single_file():
    # Path to the specific file we inspected
    # Note: The Pdf/Xml might have different names, but let's point to the XML's "companion" PDF or just any file path that resolves to that XML.
    # The processor takes a file path (usually PDF/Image) and looks for .xml with same basename.
    # So we should pass the PDF path if it exists, or just pass the XML path and let's see if processor handles it?
    # Processor logic:
    # 1. basename = os.path.basename(file_path)
    # 2. xml_path = base_no_ext + ".xml"
    # So if we pass ".../file.pdf", it looks for ".../file.xml".
    
    # We should pass the path that corresponds to `ad90129424100319FEV18569791.xml`.
    # Let's assume there is a .pdf with same name? Or we can hack it.
    
    target_xml = "invoices_input/01. FEBRERO PRUEBA/ad90129424100319FEV18569791.xml"
    # We can pass the XML path itself if we want, but processor logic expects to replace extension. 
    # If we pass .xml, base_no_ext is same, + .xml is same. So it works.
    
    abs_path = os.path.abspath(target_xml)
    print(f"Testing on: {abs_path}")
    
    # Dummy key since we expect XML success
    processor = InvoiceProcessor(api_key="dummy")
    
    # Run
    result = await processor.process_file(abs_path)
    
    print("\n--- Result ---")
    import json
    print(json.dumps(result, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(test_single_file())
