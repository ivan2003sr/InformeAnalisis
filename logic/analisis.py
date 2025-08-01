import csv
import os

ANALISIS_CSV = os.path.join("data", "analisis_definiciones.csv")
SUBANALISIS_CSV = os.path.join("data", "subanalisis.csv")

def cargar_analisis_csv():
    analisis_info = {}
    if not os.path.exists(ANALISIS_CSV):
        return analisis_info

    with open(ANALISIS_CSV, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            codigo = row['codigo'].strip()
            analisis_info[codigo] = {
                'descripcion': row['descripcion'].strip(),
                'tecnica': row['tecnica'].strip(),
                'valores_referencia': row['valores_referencia'],
                'unidades': row['unidades'].strip()
            }
    return analisis_info

def cargar_subanalisis_csv():
    subanalisis_info = {}
    if not os.path.exists(SUBANALISIS_CSV):
        return subanalisis_info

    with open(SUBANALISIS_CSV, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            codigo_padre = row['codigo_padre'].strip()
            nombre = row['nombre_subanalisis'].strip()
            ref = row['valores_referencia'].strip()
            valor_default = row.get('valor_por_defecto', '').strip()

            if codigo_padre not in subanalisis_info:
                subanalisis_info[codigo_padre] = []
            subanalisis_info[codigo_padre].append({
                'nombre': nombre,
                'valores_referencia': ref,
                'valor_por_defecto': valor_default
            })
    return subanalisis_info

RUTA_CSV = os.path.join(os.path.dirname(__file__), "../data/analisis_definiciones.csv")

def guardar_nuevo_codigo(codigo, descripcion, tecnica, valores_referencia, unidades):
    existe = os.path.isfile(RUTA_CSV)
    with open(RUTA_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["codigo", "descripcion", "tecnica", "valores_referencia", "unidades"], delimiter=";")
        if not existe:
            writer.writeheader()
        writer.writerow({
            "codigo": codigo,
            "descripcion": descripcion,
            "tecnica": tecnica,
            "valores_referencia": valores_referencia,
            "unidades": unidades
        })