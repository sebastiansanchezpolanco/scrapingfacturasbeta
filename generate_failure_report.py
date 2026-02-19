import pandas as pd
import os
import argparse

def generate_report(excel_file="gastos_2026.xlsx", output_file="reporte_fallidos.txt"):
    if not os.path.exists(excel_file):
        print(f"Error: {excel_file} not found.")
        return

    print(f"Reading {excel_file}...")
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # Filter for failures
    if "estado" not in df.columns or "nota" not in df.columns:
        print("Error: Required columns 'estado' or 'nota' missing in Excel file.")
        return

    failures = df[df["estado"] == "FALLIDO"]
    
    if failures.empty:
        print("Great! No failed transactions found.")
        with open(output_file, "w") as f:
            f.write("No failed transactions found.\n")
        return

    print(f"Found {len(failures)} failed transactions.")
    
    # Categorize errors
    # We are specifically interested in 'INVALID_ARGUMENT' as per user request
    invalid_arg_failures = failures[failures["nota"].str.contains("INVALID_ARGUMENT", na=False)]
    other_failures = failures[~failures["nota"].str.contains("INVALID_ARGUMENT", na=False)]

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("REPORTE DE FACTURAS FALLIDAS\n")
        f.write("============================\n\n")
        
        if not invalid_arg_failures.empty:
            f.write(f"ERROR: INVALID_ARGUMENT (Total: {len(invalid_arg_failures)})\n")
            f.write("Posibles causas: Archivo corrupto, contraseña, formato no soportado, o nombre de archivo problemático.\n")
            f.write("-" * 80 + "\n")
            for idx, row in invalid_arg_failures.iterrows():
                f.write(f"- {row['archivo']}\n")
                # Clean up the error message for readability
                error_msg = str(row['nota']).replace('\n', ' ')
                # f.write(f"  Detalle: {error_msg}\n") 
            f.write("\n")

        if not other_failures.empty:
            f.write(f"OTROS ERRORES (Total: {len(other_failures)})\n")
            f.write("-" * 80 + "\n")
            for idx, row in other_failures.iterrows():
                f.write(f"- {row['archivo']}\n")
                f.write(f"  Error: {str(row['nota'])}\n")
            f.write("\n")
            
        f.write("\n============================\n")
        f.write(f"Total fallidos: {len(failures)}\n")

    print(f"Report generated: {output_file}")
    print("------------------------------------------------")
    with open(output_file, "r") as f:
        print(f.read())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate failure report from invoice processing")
    parser.add_argument("--input", default="gastos_2026.xlsx", help="Input Excel file")
    parser.add_argument("--output", default="reporte_fallidos.txt", help="Output text file")
    args = parser.parse_args()
    
    generate_report(args.input, args.output)
