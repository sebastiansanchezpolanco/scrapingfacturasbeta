import pandas as pd
from utils import clean_nit

def fix_nits(excel_file="gastos_2026.xlsx"):
    print(f"Reading {excel_file}...")
    df = pd.read_excel(excel_file)
    
    count_fixed = 0
    
    # Iterate and fix
    for idx, row in df.iterrows():
        nit = row.get('nit')
        if not nit:
            continue
            
        nit_str = str(nit).strip()
        
        # Check if it looks like "123456-1" or has dots
        if '-' in nit_str or '.' in nit_str:
            clean = clean_nit(nit_str)
            
            # Logic from updated utils.py
            if '-' in clean:
                parts = clean.split('-')
                nit_num = parts[0]
                nit_dv = parts[-1]
            else:
                nit_num = clean
                nit_dv = None
            
            # Update if different
            if str(nit_num) != str(nit):
                df.at[idx, 'nit'] = nit_num
                # Also update DV column if empty? 
                # Or just ensure DV column is populated if we extracted it?
                current_dv = row.get('nit_dv_extraido')
                if (pd.isna(current_dv) or current_dv == '') and nit_dv:
                    df.at[idx, 'nit_dv_extraido'] = nit_dv
                    
                count_fixed += 1
            
            # ALWAYS update calculated DV
            # The function calculates based on the number part
            from utils import calculate_nit_verification_digit
            dv_calc = calculate_nit_verification_digit(str(nit_num))
            df.at[idx, 'nit_dv_calculado'] = dv_calc
            
            # If not counted yet (e.g. nit was already clean but DV missing)
            # Actually, I should probably enable DV calc for ALL rows, even if NIT was clean.
            # But here we are inside 'if - or .' block?
            # Let's move this outside.

    # 2nd pass or combined: Ensure DV is calculated for EVERY valid nit
    print("Calculating DV for all rows...")
    from utils import calculate_nit_verification_digit
    for idx, row in df.iterrows():
        nit = row.get('nit')
        if pd.isna(nit) or str(nit).strip() == '':
            continue
            
        # Ensure we have just the number (should be clean now from previous step)
        nit_str = str(nit).strip()
        # If still has hyphen inside loop (e.g. from previous run I only fixed dirty ones), 
        # clean it again just in case
        clean = clean_nit(nit_str)
        if '-' in clean:
             parts = clean.split('-')
             nit_num = parts[0]
        else:
             nit_num = clean
             
        dv = calculate_nit_verification_digit(nit_num)
        df.at[idx, 'nit_dv_calculado'] = dv
        count_fixed += 1 # Just to ensure we save

    if count_fixed > 0:
        print(f"Saving updates (NIT cleaning + DV calc) to {excel_file}...")
        df.to_excel(excel_file, index=False)
        print("Done.")
    else:
        print("No NITs needed fixing.")

if __name__ == "__main__":
    fix_nits()
