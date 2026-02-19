import pandas as pd
import os
from xml_skill import XmlSkill
from utils import normalize_data

def fix_missing_dates(excel_file="gastos_2026.xlsx", input_dir="invoices_input"):
    print(f"Reading {excel_file}...")
    df = pd.read_excel(excel_file)
    
    xml_skill = XmlSkill()
    
    # Identify rows with missing 'fecha' and 'archivo' ending in .xml
    mask = (df['fecha'].isna()) | (df['fecha'] == "")
    # Also include rows where 'archivo' is XML but date might be missing
    # Actually just check all missing dates
    
    missing_indices = df[mask].index
    print(f"Found {len(missing_indices)} rows with missing dates.")
    
    count_fixed = 0
    
    for idx in missing_indices:
        filename = df.at[idx, 'archivo']
        if not isinstance(filename, str):
            continue
            
        # Try to find the file in input_dir (recursive search if needed)
        # We know main.py uses os.walk, but here we might need to find where it is.
        # fast check: direct path?
        file_path = None
        for root, dirs, files in os.walk(input_dir):
            if filename in files:
                file_path = os.path.join(root, filename)
                break
        
        if not file_path:
            # print(f"File not found: {filename}")
            # Debug: print first 5 failures
            if idx < 5:
                 print(f"DEBUG: Could not find {filename} in {input_dir}")
            continue
            
        if filename.lower().endswith('.xml'):
             # Re-extract
             try:
                 # Debug specific file
                 if "ad0900260602016260000433b.xml" in filename:
                     print(f"DEBUG: Processing target file {filename}")
                 
                 data = xml_skill.extract_data(file_path)
                 if "ad0900260602016260000433b.xml" in filename:
                     print(f"DEBUG: Extracted data: {data}")

                 if data:
                     # Normalize
                     data = normalize_data(data)
                     
                     # Map extracted keys to Excel columns
                     extracted_date = data.get('fecha') or data.get('fecha_emision')
                     if extracted_date:
                         df.at[idx, 'fecha'] = extracted_date
                         
                         # Map due date
                         extracted_due_date = data.get('fecha_vencimiento')
                         if not df.at[idx, 'fecha_vencimiento'] and extracted_due_date:
                              df.at[idx, 'fecha_vencimiento'] = extracted_due_date
                         
                         count_fixed += 1
                         print(f"Fixed {filename}: {extracted_date}")
             except Exception as e:
                 print(f"Error processing {filename}: {e}")
                 
        # If it's PDF and missing date, we can't easily re-run without spending money/quota.
        # But user said "most" are empty, likely the XML ones are the bulk.
        
    if count_fixed > 0:
        print(f"Saving {count_fixed} updates to {excel_file}...")
        df.to_excel(excel_file, index=False)
        print("Done.")
    else:
        print("No dates were fixed.")

if __name__ == "__main__":
    fix_missing_dates()
