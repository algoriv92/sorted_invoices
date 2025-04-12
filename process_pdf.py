import os
import fitz  # PyMuPDF
import pandas as pd

# --- CONFIGURACIÓN DEL MES ---
MES = "01.enero"  # <--- CAMBIA ESTO PARA CADA MES
EXCEL_NAME = "listado_enero_con_pdf.xlsx"
SHEET_NAME = None  # Si el Excel tiene varias hojas y necesitas una en concreto

# --- RUTAS ---
BASE_DIR = os.path.join("data", MES)
PDF_DIR = os.path.join(BASE_DIR, "pdfs")
EXCEL_PATH = os.path.join(BASE_DIR, EXCEL_NAME)

OUTPUT_DIR = os.path.join("output", MES)
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_PDF = os.path.join(OUTPUT_DIR, f"facturas_ordenadas_{MES}.pdf")
CSV_FALTANTES = os.path.join(OUTPUT_DIR, "faltan_pdfs.csv")

# --- LEER EXCEL ---
df = pd.read_excel(EXCEL_PATH, dtype=str, sheet_name=0)
df = df.dropna(subset=["Archivo PDF", "NºOrden"])
df["Archivo PDF"] = df["Archivo PDF"].str.strip()
df["NºOrden"] = df["NºOrden"].astype(int)

# --- INICIALIZACIÓN PDF ---
pdf_final = fitz.open()
faltan = []

for _, row in df.sort_values("NºOrden").iterrows():
    nombre_pdf = row["Archivo PDF"]
    orden = int(row["NºOrden"])
    ruta_pdf = os.path.join(PDF_DIR, nombre_pdf)

    if not os.path.exists(ruta_pdf):
        faltan.append({"NºOrden": orden, "Archivo PDF": nombre_pdf})
        continue

    try:
        doc = fitz.open(ruta_pdf)
        for page in doc:
            text = f"Orden: {orden:03}"
            rect = fitz.Rect(page.rect.width - 150, 20, page.rect.width - 20, 40)
            page.insert_textbox(rect, text, fontsize=10, fontname="helv", align=1)
            pdf_final.insert_pdf(doc, from_page=page.number, to_page=page.number)
        doc.close()
    except Exception as e:
        print(f"⚠️ Error con {nombre_pdf}: {e}")
        faltan.append({"NºOrden": orden, "Archivo PDF": nombre_pdf})

# --- GUARDAR PDF FINAL ---
pdf_final.save(OUTPUT_PDF)
pdf_final.close()
print(f"\n✅ PDF final generado en: {OUTPUT_PDF}")

# --- GUARDAR CSV DE FALTANTES ---
if faltan:
    pd.DataFrame(faltan).to_csv(CSV_FALTANTES, index=False)
    print(f"⚠️  {len(faltan)} PDFs faltantes. Revisa '{CSV_FALTANTES}'")
else:
    print("🎉 Todos los PDFs fueron procesados correctamente.")
