# Scraping Facturas

Este programa procesa facturas en formato PDF e imagen (PNG, JPG) para extraer información clave (proveedor, fecha, total, impuestos) y guardarla en un archivo Excel via IA.

## Requisitos

- Python 3.8+
- Una clave de API de Google Gemini configurada en el archivo `.env`.

## Instalación

1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

Para ejecutar el programa y procesar las facturas en la carpeta `invoices_input`:

```bash
python main.py
```

### Opciones

- **Reiniciar todo**: Si quieres borrar el archivo Excel existente y volver a procesar todas las facturas desde cero:
  ```bash
  python main.py --reset
  ```

- **Carpeta de entrada personalizada**:
  ```bash
  python main.py --input_dir "otra_carpeta"
  ```

- **Archivo de salida personalizado**:
  ```bash
  python main.py --output_file "mis_gastos.xlsx"
  ```

## Estructura

- `main.py`: Script principal.
- `processor.py`: Lógica de procesamiento de facturas usando IA.
- `utils.py`: Funciones de utilidad (manejo de archivos, Excel).
- `invoices_input/`: Carpeta por defecto para las facturas.
