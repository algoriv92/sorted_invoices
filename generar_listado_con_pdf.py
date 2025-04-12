import os
import pandas as pd

# === CONFIGURACIÓN ===
MES = "01.enero" #<--- CAMBIA ESTO PARA CADA MES
EXCEL_LISTADO = f"data/{MES}/listado_enero.xlsx" # Asegúrate que coincida con el nombre del Excel del mes
PDF_DIR = f"data/{MES}/pdfs"
OUTPUT_EXCEL = f"data/{MES}/listado_{MES.split('.')[1]}_con_pdf.xlsx"

# Leer listado original
listado_df = pd.read_excel(EXCEL_LISTADO, dtype=str)

# Obtener nombres de los PDFs existentes en la carpeta correspondiente
pdfs_disponibles = {f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")}

# Crear columna nueva con el nombre del PDF asociado (si lo encuentra)
coincidencias = []

for _, row in listado_df.iterrows():
    num_factura = str(row.get("Núm.Fact.", "")).strip()
    orden = row.get("NºOrden", "")
    matched_pdf = ""

    if not num_factura:
        coincidencias.append("")
        continue

    for pdf in pdfs_disponibles:
        if num_factura in pdf:
            matched_pdf = pdf
            break

    coincidencias.append(matched_pdf)

# Agregar columna con coincidencias
listado_df["Archivo PDF"] = coincidencias

# Guardar resultado
listado_df.to_excel(OUTPUT_EXCEL, index=False)
print(f"✅ Archivo actualizado generado: {OUTPUT_EXCEL}")

# Cuando acabe, mételo dentro de la carpeta del mes correspondiente en data
