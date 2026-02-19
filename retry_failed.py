import os
import sys
import pandas as pd
import asyncio
from processor import InvoiceProcessor
from utils import save_to_excel

# Set stdout to handle utf-8 even if terminal doesn't default to it
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def main():
    input_xlsx = "gastos_2026.xlsx"
    if not os.path.exists(input_xlsx):
        print(f"Error: {input_xlsx} not found.")
        return

    print(f"Reading {input_xlsx}...")
    try:
        df = pd.read_excel(input_xlsx)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # Find failed files
    failed_rows = df[df["estado"] == "FALLIDO"]
    if failed_rows.empty:
        print("No failed files found in Excel.")
        return

    print(f"Found {len(failed_rows)} failed files. Retrying...")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
         print("\n🔑  Please enter your Google Gemini API Key (input will be hidden): ")
         from getpass import getpass
         api_key = getpass("API Key: ").strip()

    if not api_key:
        print("No API Key provided. Exiting.")
        return

    processor = InvoiceProcessor(api_key)
    
    # We will process them sequentially to avoid rate limits and better debugging
    results = []
    
    for idx, row in failed_rows.iterrows():
        filename = row['archivo']
        # We need to find the full path. The Excel only has the basename.
        # We'll search in invoices_input
        full_path = None
        for root, dirs, files in os.walk("invoices_input"):
            if filename in files:
                full_path = os.path.join(root, filename)
                break
        
        if not full_path:
            # Try to handle potential encoding mismatch in file finding
            print(f"Could not find file on disk: {filename.encode('utf-8', 'replace').decode('utf-8')}. Skipping.")
            continue

        safe_filename = filename.encode('utf-8', 'replace').decode('utf-8')
        print(f"Retrying: {safe_filename}...")
        
        # Delay to engage rate limit kindness
        await asyncio.sleep(5)
        
        try:
            # Re-process
            res = await processor.process_file(full_path)
            if res and res.get("estado") == "EXITOSO":
                print(f"✅ Success: {safe_filename}")
                results.append(res)
            else:
                print(f"❌ Failed again: {safe_filename} - {res.get('nota')}")
        except Exception as e:
            print(f"❌ Exception processing {safe_filename}: {e}")

    if results:
        print(f"Saving {len(results)} recovered files...")
        save_to_excel(results, input_xlsx)
    else:
        print("No files recovered this run.")

if __name__ == "__main__":
    asyncio.run(main())
