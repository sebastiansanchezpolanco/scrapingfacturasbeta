import os
import asyncio
from dotenv import load_dotenv
from vision_skill import VisionSkill
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def debug_vision():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n🔑  Please enter your Google Gemini API Key: ")
        from getpass import getpass
        api_key = getpass("API Key: ").strip()

    if not api_key:
        print("ERROR: No API Key provided.")
        return

    print(f"API Key loaded: {api_key[:5]}...{api_key[-5:]}")
    
    # Path to a file that likely doesn't have a matching XML (or we force vision)
    # Using the one suspected: fv080900985000823000007c0.pdf
    file_path = "/Users/sebastiansanchez/Documents/scrapingfacturas/invoices_input/01. FEBRERO PRUEBA/fv080900985000823000007c0.pdf"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        # Try finding another one
        return

    print(f"Testing VisionSkill on: {file_path}")
    
    skill = VisionSkill(api_key)
    
    try:
        # Run directly (it handles sync/async internally in processor, but here we call direct method?)
        # VisionSkill.extract_data is synchronous (blocking)
        print("Calling extract_data...")
        data = skill.extract_data(file_path)
        
        import json
        print("\n--- Extraction Result ---")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if not data:
            print("\nRESULT: FAILED (Empty Data)")
        else:
            print("\nRESULT: SUCCESS")
            
    except Exception as e:
        print(f"\nRESULT: ERROR - {e}")

if __name__ == "__main__":
    asyncio.run(debug_vision())
