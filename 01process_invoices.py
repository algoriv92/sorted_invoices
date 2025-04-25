import os
import re
import fitz  # PyMuPDF
import pandas as pd

# --- CONFIGURACIÓN ---
MES = "12.diciembre"  # <--- CAMBIA ESTO PARA CADA MES
EXCEL_NAME = "listado_diciembre.xlsx"  # Asegúrate que coincida con el nombre del Excel del mes

# --- RUTAS DINÁMICAS ---
BASE_DIR = os.path.join("data", MES)
PDF_DIR = os.path.join(BASE_DIR, "pdfs")
EXCEL_PATH = os.path.join(BASE_DIR, EXCEL_NAME)

OUTPUT_DIR = os.path.join("output", MES)
os.makedirs(OUTPUT_DIR, exist_ok=True)

CSV_RESULTADOS = os.path.join(OUTPUT_DIR, "resultados_facturas.csv")
CSV_NO_MATCH = os.path.join(OUTPUT_DIR, "no_match_log.csv")

# --- CARGA Y LIMPIEZA DEL EXCEL ---
excel_df = pd.read_excel(EXCEL_PATH, dtype=str)
excel_df.columns = excel_df.columns.str.strip().str.lower()

# Nombre exacto de la columna de importe
col_total = "total fra."

# Limpieza y conversión
excel_df[col_total] = (
    excel_df[col_total]
    .str.replace(".", "", regex=False)
    .str.replace(",", ".")
    .astype(float)
)

# --- MAPAS DE FACTURAS E IMPORTES ---
factura_map = {}
importe_map = {}

# Filtrar filas sin número de orden o importe
excel_df = excel_df.dropna(subset=["nºorden", "núm.fact.", col_total])

for _, row in excel_df.iterrows():
    num_orden = int(row["nºorden"])
    num_fact = str(row["núm.fact."]).strip().lower()
    total = round(row[col_total], 2)

    claves_factura = [num_fact]
    if len(num_fact) > 5:
        claves_factura.extend([
            num_fact[-9:], num_fact[-8:], num_fact[-7:], num_fact[-6:]
        ])

    for clave in claves_factura:
        factura_map[clave] = num_orden
    importe_map[total] = num_orden

# --- FUNCIONES ---
def extraer_factura_nombre(nombre):
    return re.findall(r"\d{6,12}", nombre)

def extraer_factura_texto(texto):
    return re.findall(r"(?:factura[\s#:]*)([a-zA-Z0-9/\-_]+)", texto, flags=re.IGNORECASE)

def detectar_total(texto):
    patrones = [
        r"(?i)total[^0-9]{0,10}([\d.,]+)",
        r"(?i)importe total[^0-9]{0,10}([\d.,]+)",
        r"(?i)total factura[^0-9]{0,10}([\d.,]+)"
    ]
    for patron in patrones:
        matches = re.findall(patron, texto)
        for match in matches:
            limpio = re.sub(r"[^\d,.-]", "", match).replace(".", "").replace(",", ".")
            try:
                return round(float(limpio), 2)
            except:
                continue
    return None

# --- PROCESAMIENTO ---
coincidentes = []
no_encontradas = []

for archivo in sorted(os.listdir(PDF_DIR)):
    if not archivo.lower().endswith(".pdf"):
        continue

    ruta = os.path.join(PDF_DIR, archivo)
    nombre_base = os.path.splitext(archivo)[0].lower()

    metodo = "No encontrado"
    valor_detectado = "(no encontrado)"
    orden = ""
    coincide = "No"
    encontrado = False

    for posible in extraer_factura_nombre(nombre_base):
        if posible in factura_map:
            metodo = "Número de factura (archivo)"
            valor_detectado = posible
            orden = factura_map[posible]
            coincide = "Sí"
            encontrado = True
            break

    if not encontrado:
        try:
            doc = fitz.open(ruta)
            texto = "\n".join([page.get_text() for page in doc])
            doc.close()

            for posible in extraer_factura_texto(texto):
                if posible.lower() in factura_map:
                    metodo = "Número de factura (PDF)"
                    valor_detectado = posible
                    orden = factura_map[posible.lower()]
                    coincide = "Sí"
                    encontrado = True
                    break

            if not encontrado:
                imp = detectar_total(texto)
                if imp and imp in importe_map:
                    metodo = "Importe total"
                    valor_detectado = imp
                    orden = importe_map[imp]
                    coincide = "Sí"
                    encontrado = True

        except Exception as e:
            print(f"❌ Error procesando {archivo}: {e}")

    if encontrado:
        coincidentes.append({
            "Archivo": archivo,
            "Método": metodo,
            "Valor_detectado": valor_detectado,
            "¿Coincide?": coincide,
            "Nº Orden": orden
        })
    else:
        no_encontradas.append({
            "Archivo": archivo,
            "Método": metodo,
            "Valor_detectado": valor_detectado,
            "¿Coincide?": coincide,
            "Nº Orden": orden
        })

# --- GUARDAR RESULTADOS ---
pd.DataFrame(coincidentes).to_csv(CSV_RESULTADOS, index=False)
pd.DataFrame(no_encontradas).to_csv(CSV_NO_MATCH, index=False)

print(f"✅ Análisis completado para {MES}. Resultados en '{OUTPUT_DIR}'")
