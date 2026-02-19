import pandas as pd

def fix_values(input_file="gastos_2026_cleaned.xlsx", output_file="gastos_2026.xlsx"):
    print(f"Reading {input_file}...")
    df = pd.read_excel(input_file)
    
    count_low = 0
    count_high = 0
    
    # Thresholds
    LOW_THRESHOLD = 500 # If total < 500, it's likely a decimal error (should be *1000)
    # Why 500? Invoices are rarely for 500 pesos. Maybe 1000? 
    # The smallest legitimate invoice might be for ~5000 pesos?
    # Lowest observed was 6.8 -> 6800. 
    # 11.9 -> 11900.
    
    # Iterate
    for idx, row in df.iterrows():
        val = row.get('total')
        if pd.isna(val) or not isinstance(val, (int, float)):
            continue
            
        # Check low values
        if 0 < val < LOW_THRESHOLD:
            # Heuristic: Multiply by 1000
            new_val = val * 1000
            df.at[idx, 'total'] = new_val
            count_low += 1
            # print(f"Fixed LOW value: {val} -> {new_val} (File: {row['archivo']})")
            
        # Check if any are just absurdly huge?
        # The top ones were ~200 million, which is possible for big companies.
        
    print(f"Fixed {count_low} suspiciously low values.")
    
    df.to_excel(output_file, index=False)
    print(f"Saved corrected file to {output_file}")

if __name__ == "__main__":
    fix_values()
