
# 🧾 Proyecto: Ordenar y Procesar Facturas PDF según Excel

## 📁 Estructura de carpetas propuesta

```
sorted_invoices/
├── data/
│   ├── listado_enero.xlsx
│   └── pdfs/
│       └── [todos los PDF]
├── output/
│   ├── resultados_facturas.csv
│   ├── no_match_log.csv
│   ├── faltan_pdfs.csv
│   └── facturas_ordenadas.pdf
├── 01process_invoices.py
├── 02refinar_no_match.py
├── 03process_pdf.py
└── README.md
```

## 📌 Objetivo

1. Leer un Excel (`listado_mes.xlsx`) con facturas y extraer:
   - Nº de orden
   - Nº de factura
   - Importe total con IVA

2. Cruzar cada factura PDF con el Excel usando:
   - Número de factura (en el nombre del archivo o dentro del PDF)
   - Importe total
   - Si no hay coincidencia, se loguea como no encontrada

3. Marcar las coincidencias encontradas en un CSV (`resultados_facturas.csv`).

4. Unir las facturas en un solo PDF ordenado por NºOrden, añadiendo “Orden: XXX” arriba a la derecha.

## ⚙️ Scripts

### ✅ `01process_invoices.py`

Extrae coincidencias entre los PDF y el Excel (por nombre, contenido o importe), y genera:

- `output/resultados_facturas.csv`
- `output/no_match_log.csv`

### ✅ `02refinar_no_match.py`

Refina el matcheo entre los csv `resultados_facturas.csv` y `no_match_log.csv`. Aquellas facturas que no se localizaron en el listado, **se tendrán que poner a mano**.

Para hacerlo, se coge el `listado_mes.xlsx` y se pega todo el refinado ahí, y se ajusta con el listado, y lo renombraremos como `listado_mes_con_pdf.xlsx`

### ✅ `03process_pdf.py`

Lee `listado_mes_con_pdf.xlsx` y genera el PDF final con los PDFs ordenados por Nº de Orden, añadiendo un “Orden: XXX” arriba al centro.

Si no encuentra un fichero o no lo liga al PDF final, genera un csv con los PDFs faltantes (`faltan_pdfs.csv`)

Genera el PDF esperado (`facturas_ordenadas_XX.mes.pdf`), y san se acabó 🥳

## 🚀 Pasos para ejecutar

1. Lleva todos las facturas en PDF a `data/pdfs/`
2. Lleva el listado en `data/listado_mes.xlsx`
3. Ejecuta los scripts en este orden:

```bash
python 01process_invoices.py
python 02refinar_no_match.py
python 03process_pdf.py
```

**Recordar que entre el paso 02 y 03 hay que hacer manualmente la corrección de los ficheros faltantes.**

## 🐙 GitHub (opcional)

```bash
git init ## Solo para iniciar sesión
git remote add origin https://github.com/tu_usuario/sorted_invoices.git ## Solo la primera vez
git add .
git commit -m "Primer commit: scripts para emparejar y ordenar facturas"
git branch -M main ## Para ubicarse en la rama main
git push -u origin main
```
