import os
import pandas as pd

# --- CONFIGURACIÓN DEL MES ---
MES = "09.septiembre"  # <--- CAMBIA ESTO PARA CADA MES
EXCEL_NAME = "listado_septiembre.xlsx"
CSV_MATCH = f"output/{MES}/resultados_facturas.csv"
CSV_NO_MATCH = f"output/{MES}/no_match_log.csv"
EXCEL_PATH = f"data/{MES}/{EXCEL_NAME}"

# --- CARGAR ARCHIVOS ---
df_match = pd.read_csv(CSV_MATCH)
df_no_match = pd.read_csv(CSV_NO_MATCH)
df_excel = pd.read_excel(EXCEL_PATH, dtype=str)

# --- LIMPIAR Y NORMALIZAR ---
df_excel = df_excel.dropna(subset=["NºOrden", "Núm.Fact.", "Total Fra."])
df_excel["NºOrden"] = df_excel["NºOrden"].astype(int)
df_excel["Núm.Fact."] = df_excel["Núm.Fact."].str.strip().str.lower()
df_excel["Total Fra."] = df_excel["Total Fra."].str.replace(".", "", regex=False).str.replace(",", ".").astype(float)

# --- INTENTAR RECOGER COINCIDENCIAS QUE FALTABAN ---
nuevos_encontrados = []

for _, row in df_no_match.iterrows():
    archivo = row["Archivo"].strip().lower()

    # Buscar por número de factura en el nombre del PDF
    for _, fila in df_excel.iterrows():
        if fila["Núm.Fact."] in archivo:
            nuevos_encontrados.append({
                "Archivo": row["Archivo"],
                "Método": "Factura en nombre",
                "Valor_detectado": fila["Núm.Fact."],
                "¿Coincide?": "Sí",
                "Nº Orden": fila["NºOrden"]
            })
            break
    else:
        # Buscar por importe si no hay coincidencia de factura
        texto_valor = str(row["Valor_detectado"]).replace(",", ".").strip()
        try:
            valor_float = round(float(texto_valor), 2)
            match = df_excel[df_excel["Total Fra."].round(2) == valor_float]
            if len(match) == 1:
                fila = match.iloc[0]
                nuevos_encontrados.append({
                    "Archivo": row["Archivo"],
                    "Método": "Importe único",
                    "Valor_detectado": valor_float,
                    "¿Coincide?": "Sí",
                    "Nº Orden": fila["NºOrden"]
                })
        except:
            pass

# --- ACTUALIZAR Y GUARDAR ---
df_match = pd.concat([df_match, pd.DataFrame(nuevos_encontrados)], ignore_index=True)

# Eliminar ya localizados del no_match
nombres_nuevos = [n["Archivo"] for n in nuevos_encontrados]
df_no_match = df_no_match[~df_no_match["Archivo"].isin(nombres_nuevos)]

# Guardar actualizaciones
df_match.to_csv(CSV_MATCH, index=False)
df_no_match.to_csv(CSV_NO_MATCH, index=False)

print(f"✅ Refinado completado para {MES}. Nuevas coincidencias añadidas: {len(nuevos_encontrados)}")
