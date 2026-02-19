import pandas as pd

def clean_duplicates(excel_file="gastos_2026.xlsx"):
    print(f"Reading {excel_file}...")
    df = pd.read_excel(excel_file)
    
    initial_count = len(df)
    print(f"Initial rows: {initial_count}")
    
    # Logic to handle duplicates:
    # We want to keep the row with the most valid data.
    # We can count non-null values per row.
    df['completeness'] = df.notna().sum(axis=1)
    
    # Sort by filename and completeness (descending), so the best row is first
    df = df.sort_values(by=['archivo', 'completeness'], ascending=[True, False])
    
    # Drop duplicates keeping the first (best) one
    df_clean = df.drop_duplicates(subset=['archivo'], keep='first')
    
    # Remove the helper column
    df_clean = df_clean.drop(columns=['completeness'])
    
    final_count = len(df_clean)
    removed = initial_count - final_count
    
    print(f"Removed {removed} duplicate rows.")
    print(f"Final rows: {final_count}")
    
    if removed > 0:
        output_file = "gastos_2026_cleaned.xlsx"
        df_clean.to_excel(output_file, index=False)
        print(f"Saved cleaned file to {output_file}")
        
        # Verify specific Surtiplaza case
        surti = df_clean[df_clean['archivo'] == 'FEP1138374.pdf']
        if not surti.empty:
            print("Kept Surtiplaza record:")
            print(surti[['archivo', 'proveedor', 'total', 'fecha']].to_string())

if __name__ == "__main__":
    clean_duplicates()
