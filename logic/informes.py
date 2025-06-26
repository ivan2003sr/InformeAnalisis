# logic/informes.py
import os
from datetime import datetime
from fpdf import FPDF
import webbrowser
import platform

def limpiar_texto_pdf(texto):
    return (
        texto.replace("μ", "u")
             .replace("°", " grados")
             .replace("–", "-")
             .replace("º", "o")
    )

def generar_pdf_informe(paciente, lista_analisis, logo_path=None):
    """
    paciente = dict con 'dni', 'nombre', 'apellido', 'fecha_nacimiento', 'edad'
    lista_analisis = lista de dicts con 'codigo', 'descripcion', 'valor', 'referencia'
    """
    carpeta_nombre = f"{paciente['apellido'].upper()}-{paciente['nombre'].upper()}-{paciente['dni']}"
    carpeta_path = os.path.join(os.getcwd(), carpeta_nombre)
    os.makedirs(carpeta_path, exist_ok=True)

    fecha_str = datetime.now().strftime("%Y%m%d")
    archivo_pdf = os.path.join(carpeta_path, f"{paciente['apellido'].upper()}-{fecha_str}.pdf")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Logo (si hay)
    if logo_path and os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=30)
        pdf.ln(20)

    # Encabezado
    pdf.cell(0, 10, limpiar_texto_pdf(f"Informe de Análisis de Laboratorio"), ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", size=11)
    pdf.cell(0, 10, f"Paciente: {paciente['apellido'].title()}, {paciente['nombre'].title()} (DNI: {paciente['dni']})", ln=True)
    pdf.cell(0, 10, f"Fecha de nacimiento: {paciente['fecha_nacimiento']} - Edad: {paciente['edad']} años", ln=True)
    pdf.cell(0, 10, f"Fecha del informe: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(10)

    # Tabla de análisis
    for analisis in lista_analisis:
        linea = f"{analisis['codigo']} - {analisis['descripcion']}: {analisis['valor']} (Ref: {analisis['referencia']})"
        pdf.cell(0, 10, limpiar_texto_pdf(linea), ln=True)

    pdf.ln(15)
    pdf.cell(0, 10, "Firma y Sello: ____________________________", ln=True)

    pdf.output(archivo_pdf)

    try:
        webbrowser.open_new(archivo_pdf)
    except Exception as e:
        print(f"No se pudo abrir el PDF automáticamente: {e}")

    try:
        if platform.system() == "Windows":
            os.startfile(archivo_pdf, "print")
        elif platform.system() == "Darwin":
            os.system(f"lp '{archivo_pdf}'")
        else:
            os.system(f"lpr '{archivo_pdf}'")
    except Exception as e:
        print(f"No se pudo imprimir automáticamente: {e}")

    return archivo_pdf
