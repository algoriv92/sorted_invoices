import os
import fitz  # PyMuPDF

# === CONFIGURACIÓN ===
CARPETA_ORIGEN = r"C:\Users\alexg\Desktop\sorted_invoices\output\todos"
CARPETA_DESTINO = r"C:\Users\alexg\Desktop\sorted_invoices\output\comprimidos"
os.makedirs(CARPETA_DESTINO, exist_ok=True)

# === RECORRER TODOS LOS PDF DE LA CARPETA ===
for archivo in os.listdir(CARPETA_ORIGEN):
    if not archivo.lower().endswith(".pdf"):
        continue

    ruta_origen = os.path.join(CARPETA_ORIGEN, archivo)
    ruta_destino = os.path.join(CARPETA_DESTINO, archivo)

    try:
        doc = fitz.open(ruta_origen)
        doc.save(ruta_destino, garbage=4, deflate=True, clean=True)
        ## doc.save(ruta_destino, garbage=4, deflate=True, clean=True, compress_images=True, image_min_bytes=5000, recompress=True, dpi=100)
        doc.close()
        print(f"✅ Comprimido: {archivo}")
    except Exception as e:
        print(f"⚠️ Error al comprimir {archivo}: {e}")
