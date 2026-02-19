import asyncio
import os
from processor import InvoiceProcessor

async def main():
    # Use a file we know exists and has an XML
    test_file = "invoices_input/01. FEBRERO PRUEBA/ad08002152270062600002B93.pdf"
    
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return

    # We don't need a real API key for XML extraction if logic works
    processor = InvoiceProcessor(api_key="DUMMY_KEY")
    
    print(f"Testing extraction for {test_file}...")
    data = await processor.process_file(test_file)
    
    import json
    print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
