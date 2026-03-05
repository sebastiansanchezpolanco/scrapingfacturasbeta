# Arquitectura y flujo del proyecto de scraping de facturas

## Diagrama de flujo: ciclo de vida de una factura

```mermaid
flowchart TB
    subgraph ENTRADA["main.py — Orquestación"]
        A1[Inicio: argumentos, API key]
        A2[Crear directorio input_dir]
        A3[Listar PDF/PNG/JPG en input_dir]
        A4[Leer Excel existente → archivos ya EXITOSOS]
        A5[Filtrar: solo archivos no procesados]
        A6[InvoiceProcessor + asyncio Semaphore]
    end

    subgraph POR_ARCHIVO["processor.py — Por cada archivo"]
        B1[process_file: ruta PDF/imagen]
        B2[¿Existe .xml mismo nombre?]
        B3[XmlSkill.extract_data]
        B4[VisionSkill.extract_data]
        B5[Mapear campos Vision → estructura Excel]
        B6[_normalize]
    end

    subgraph XML["xml_skill.py — Extracción XML"]
        C1[Parsear XML]
        C2[Quitar namespaces]
        C3[¿AttachedDocument o Invoice?]
        C4[Si AttachedDocument: extraer XML interno de Description]
        C5[_parse_invoice: proveedor, NIT, fechas, totales, CUFE/UUID]
        C6[Devolver dict con fecha_emision, cufe, etc.]
    end

    subgraph NORMALIZACION["utils.py — normalize_data"]
        D1[fecha_emision → fecha si falta]
        D2[clean_colombian_number: base, impuestos, total]
        D3[correct_suspicious_low_total para total]
        D4[format_date_colombian: fechas → DD/MM/YYYY]
        D5[clean_nit: quitar puntos/espacios]
        D6[Separar NIT número y DV; calcular nit_dv_calculado]
    end

    subgraph SALIDA["utils.py — Persistencia"]
        E1[save_to_excel: DataFrame con columnas fijas]
        E2[¿Excel existe?]
        E3[Crear nuevo / Append openpyxl]
        E4[Guardar cada 5 registros + guardado final]
    end

    A1 --> A2 --> A3 --> A4 --> A5 --> A6
    A6 --> B1
    B1 --> B2
    B2 -->|Sí| B3
    B2 -->|No| B4
    B3 --> C1
    C1 --> C2 --> C3
    C3 --> C4
    C4 --> C5 --> C6
    C6 --> B6
    B3 -.->|Error| B4
    B4 --> B5 --> B6
    B6 --> D1
    D1 --> D2 --> D3 --> D4 --> D5 --> D6
    D6 --> E1
    E1 --> E2 --> E3
    E3 --> E4
```

## Explicación de cada paso

### 1. main.py — Orquestación
- **Argumentos y API key**: Se leen `--input_dir`, `--output_file`, `--reset`. Se exige `GOOGLE_API_KEY` (env o getpass).
- **Directorio**: Se crea `input_dir` si no existe.
- **Listado**: Se recorren recursivamente todos los archivos con extensión PDF o imagen (png, jpg, jpeg).
- **Resumen**: Se lee el Excel de salida (si existe) y se obtiene el conjunto de archivos ya procesados con estado EXITOSO para no repetirlos.
- **Filtrado**: Solo se procesan archivos cuyo nombre no esté en ese conjunto.
- **Procesamiento**: Se instancia `InvoiceProcessor` y se lanzan tareas asíncronas (una por archivo, con semáforo 1 y pausa de 15 s entre llamadas para respetar límites de la API).

### 2. processor.py — Procesamiento por archivo
- **process_file**: Recibe la ruta del PDF/imagen. Obtiene la ruta del XML compañero (mismo nombre, extensión `.xml`).
- **Decisión XML**: Si existe ese XML, se intenta extraer con `XmlSkill.extract_data(xml_path)`.
- **XmlSkill**: Si hay XML, se parsea y se extraen los campos; el resultado es un diccionario con la estructura esperada (incluye `fecha_emision`, `cufe`, etc.).
- **Fallback Vision**: Si no hay XML o falla el parseo, se usa `VisionSkill.extract_data(file_path)` (Gemini). La respuesta se mapea a la misma estructura (proveedor, nit, fechas, total, cufe, etc.).
- **_normalize**: Tanto el dato de XML como el de Vision pasan por `utils.normalize_data()` para unificar formato antes de devolver.

### 3. xml_skill.py — Extracción desde XML
- **Parse y namespaces**: Se parsea el XML y se eliminan namespaces de los tags para buscar por nombre.
- **Tipo de documento**: Se distingue entre `AttachedDocument` (contenedor DIAN) e `Invoice` directo.
- **AttachedDocument**: El Invoice real suele estar dentro de `Attachment/ExternalReference/Description` como XML embebido; se parsea ese contenido y se trabaja sobre el árbol interno.
- **_parse_invoice**: Se extraen proveedor, NIT, dirección, teléfono, ciudad, número de factura, fecha emisión/vencimiento, descripción, moneda, base, impuestos, total y **CUFE** (elemento `UUID`). Se devuelve un dict con esas claves.

### 4. utils.py — normalize_data (normalización)
- **fecha**: Si no viene `fecha` pero sí `fecha_emision` (típico del XML), se copia para tener siempre la columna “fecha” unificada.
- **Números**: Se aplica `clean_colombian_number` a base, impuestos y total (símbolos, miles con punto, decimal con coma).
- **Total bajo**: Se aplica `correct_suspicious_low_total` al total (p. ej. valores &lt; 500 se multiplican por 1000 como corrección heurística).
- **Fechas**: Todas las fechas presentes se formatean con `format_date_colombian` a DD/MM/YYYY.
- **NIT**: Se limpia con `clean_nit` (quitar puntos y espacios), se separa número y dígito de verificación (DV) si hay guion, y se calcula `nit_dv_calculado` con el algoritmo módulo 11 (pesos DIAN).

### 5. utils.py — save_to_excel (persistencia)
- **DataFrame**: La lista de diccionarios normalizados se convierte en DataFrame con el orden de columnas fijo (archivo, estado, proveedor, nit, factura_numero, fecha, etc., incluyendo cufe, nit_dv_calculado, nit_dv_extraido, nota).
- **Crear o anexar**: Si no existe el archivo Excel se crea; si existe se anexa con openpyxl (modo append). En fallo se hace concat con lo leído y reescritura completa.
- **Frecuencia**: Desde main se llama a `save_to_excel` cada 5 registros acumulados y al final con los restantes.

---

## Resumen de responsabilidades

| Módulo       | Responsabilidad principal |
|-------------|----------------------------|
| **main.py** | Entrada/salida, listado de archivos, resumen, concurrencia y llamadas a processor + save_to_excel. |
| **processor.py** | Decidir XML vs Vision por archivo, llamar a XmlSkill o VisionSkill, mapear Vision a estructura común y aplicar normalización. |
| **xml_skill.py** | Parsear XML UBL 2.1 (incl. AttachedDocument), extraer campos de factura y CUFE (UUID). |
| **utils.py** | Normalización (fechas, números, NIT, total bajo) y persistencia (save_to_excel, columnas estándar). |

El flujo de una factura es: **entrada (PDF/imagen)** → **decisión XML/Vision** → **extracción (xml_skill o vision_skill)** → **normalización (utils)** → **guardado en Excel (utils)**.
