import asyncio
import argparse
import os
import time
from dotenv import load_dotenv

load_dotenv()

from processor import InvoiceProcessor
from utils import setup_directories, save_to_excel

async def main():
    parser = argparse.ArgumentParser(description="Async Invoice Processor")
    parser.add_argument("--input_dir", type=str, default="invoices_input", help="Directory containing invoices")
    parser.add_argument("--output_file", type=str, default="gastos_2026.xlsx", help="Output Excel file")
    parser.add_argument("--reset", action="store_true", help="Delete existing output file and start from scratch")
    args = parser.parse_args()

    input_dir = args.input_dir
    output_file = args.output_file

    # Check for API Key
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        print("\n🔑  Please enter your Google Gemini API Key (input will be hidden): ")
        from getpass import getpass
        key = getpass("API Key: ").strip()
        
    if not key:
        print("❌  No key provided. Exiting.")
        return

    # We do NOT save it to .env as requested by user

    if args.reset and os.path.exists(output_file):
        print(f"Resetting... Deleting existing file: {output_file}")
        os.remove(output_file)

    setup_directories(input_dir)

    # Get list of files
    files = []
    for root, _, filenames in os.walk(input_dir):
        for f in filenames:
            if f.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
                files.append(os.path.join(root, f))

    if not files:
        print(f"No PDF or Image files found in {input_dir}")
        return

    print(f"Found {len(files)} files. Starting processing...")
    start_time = time.time()

    processor = InvoiceProcessor(api_key=key)
    
    # Load processed files to avoid re-processing
    processed_files = set()
    if os.path.exists(output_file):
        try:
            import pandas as pd
            df = pd.read_excel(output_file)
            if 'archivo' in df.columns and 'estado' in df.columns:
                # Only skip files that were SUCCESSFULLY processed
                processed_files = set(df[df['estado'] == 'EXITOSO']['archivo'].astype(str))
            elif 'archivo' in df.columns:
                # Fallback for old format
                processed_files = set(df['archivo'].astype(str))
            print(f"Resuming... {len(processed_files)} files already processed.")
        except Exception as e:
            print(f"Could not read existing file, starting fresh: {e}")

    # Helper to check if file should be processed
    files_to_process = []
    for f in files:
        if os.path.basename(f) not in processed_files:
            files_to_process.append(f)
            
    skipped_count = len(files) - len(files_to_process)
    if skipped_count > 0:
        print(f"Skipping {skipped_count} files already in database.")
        
    if not files_to_process:
        print("All files already processed.")
        return

    total_files = len(files_to_process)
    print(f"Starting processing of {total_files} new files...")
    
    # Create async tasks with concurrency limit
    # Free tier limit is very low (approx 2-5 RPM), so we must be very conservative
    semaphore = asyncio.Semaphore(1) 

    async def safe_process(f):
        async with semaphore:
            res = await processor.process_file_with_retry(f) if hasattr(processor, 'process_file_with_retry') else await processor.process_file(f)
            # Wait to respect rate limits (approx 15s delay ensures < 4 RPM)
            await asyncio.sleep(15) 
            return res

    tasks = [safe_process(f) for f in files_to_process]
    
    # Process results as they complete
    results = []
    pending_save = []
    completed_count = 0
    
    for future in asyncio.as_completed(tasks):
        res = await future
        completed_count += 1
        percentage = (completed_count / total_files) * 100
        print(f"[{completed_count}/{total_files}] {percentage:.1f}% - Processed")

        if res:
            results.append(res)
            pending_save.append(res)
            
            # Incremental save every 5 files
            if len(pending_save) >= 5:
                print(f"Saving batch of {len(pending_save)} records...")
                save_to_excel(pending_save, output_file)
                pending_save = []
    
    # Final save
    if pending_save:
        save_to_excel(pending_save, output_file)
        
    print("Processing complete.")
    
    elapsed = time.time() - start_time
    print(f"Total time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
