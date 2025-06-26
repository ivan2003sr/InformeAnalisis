# logic/informes.py
import os
from datetime import datetime
from fpdf import FPDF
import webbrowser
import platform

class PDF(FPDF):
    def header(self):
        # Logo - usando ruta absoluta para evitar problemas
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png')
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 25)
        self.set_font('Arial', 'B', 15)
        # Calcular ancho del título y posición
        title = "INFORME DE LABORATORIO"
        self.cell(0, 10, title, 0, 1, 'C')
        self.ln(10)  # Espacio después del título

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')

def format_fecha(fecha_str):
    try:
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
        return fecha_obj.strftime('%d/%m/%Y')
    except:
        return fecha_str
    
def split_referencia(referencia):
    """Separa el valor de referencia de las unidades"""
    if not referencia:
        return referencia, ""
    
    # Buscamos el último espacio para separar valor de unidades
    last_space = referencia.rfind(' ')
    if last_space > 0:
        # Verificamos que después del espacio haya texto que parezca unidades
        possible_units = referencia[last_space+1:]
        if any(c.isalpha() for c in possible_units):  # Si contiene letras
            return referencia[:last_space], possible_units
    return referencia, ""
    
def generar_pdf_informe(paciente, lista_analisis, logo_path=None):

    # Configuración inicial
    if logo_path is None:
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png')
        if not os.path.exists(logo_path):
            logo_path = None

    # Crear carpeta para el paciente
    carpeta_nombre = f"{paciente['apellido'].upper()}-{paciente['nombre'].upper()}-{paciente['dni']}"
    carpeta_path = os.path.join(os.getcwd(), carpeta_nombre)
    os.makedirs(carpeta_path, exist_ok=True)

    # Nombre del archivo PDF
    fecha_str = datetime.now().strftime("%Y%m%d %H%M%S")
    archivo_pdf = os.path.join(carpeta_path, f"{paciente['apellido'].upper()}-{fecha_str}.pdf")

    # Crear PDF
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    # Información del paciente
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "DATOS DEL PACIENTE", ln=1)
    pdf.set_font('Arial', '', 11)

       # Formatear fecha de nacimiento
    fecha_nacimiento = format_fecha(paciente['fecha_nacimiento'])
    fecha_informe = datetime.now().strftime('%d/%m/%Y')
    
    paciente_info = [
        f"Nombre: {paciente['apellido'].title()}, {paciente['nombre'].title()}",
        f"DNI: {paciente['dni']}",
        f"Fecha de nacimiento: {fecha_nacimiento}",
        f"Edad: {paciente['edad']} años",
        f"Fecha del informe: {fecha_informe}"
    ]
    
    for info in paciente_info:
        pdf.cell(0, 7, info, 0, 1)
    
    pdf.ln(10)

    # Tabla de resultados
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "RESULTADOS DE ANÁLISIS", 0, 1)
    pdf.set_font('Arial', '', 11)
    
    # Encabezados de tabla
    pdf.set_fill_color(200, 220, 255)
    #pdf.cell(25, 10, "Código", 1, 0, 'C', True)
    pdf.cell(80, 10, "Análisis", 1, 0, 'C', True)
    pdf.cell(30, 10, "Valor", 1, 0, 'C', True)
    pdf.cell(50, 10, "Referencia", 1, 1, 'C', True)
    
    # Filas de datos
    pdf.set_fill_color(255, 255, 255)
    fill = False
    for analisis in lista_analisis:
        pdf.set_fill_color(240, 240, 240) if fill else pdf.set_fill_color(255, 255, 255)
        
        # Extraer unidades de la referencia (última palabra)
        referencia_parts = analisis['referencia'].rsplit(' ', 1)
        valor_ref = referencia_parts[0]
        unidades = referencia_parts[1] if len(referencia_parts) > 1 else ""
        
        # Mostrar fila
        pdf.cell(80, 8, analisis['descripcion'], 1, 0, 'L', fill)
        pdf.cell(30, 8, f"{analisis['valor']} {unidades}", 1, 0, 'C', fill)
        pdf.cell(50, 8, analisis['referencia'], 1, 1, 'C', fill)
        fill = not fill
    
    pdf.ln(15)
    
    # Firma
    pdf.set_font('Arial', 'I', 11)
    pdf.cell(0, 10, "Firma y sello del responsable:", 0, 1)
    pdf.cell(0, 5, "", 0, 1)  # Espacio para firma
    pdf.line(pdf.get_x() + 50, pdf.get_y(), pdf.get_x() + 150, pdf.get_y())
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, "Nombre y apellido:", 0, 1)
    pdf.cell(0, 5, "Nº de matrícula:", 0, 1)

    # Guardar PDF
    pdf.output(archivo_pdf)

    # Abrir PDF
    try:
        webbrowser.open_new(archivo_pdf)
    except Exception as e:
        print(f"No se pudo abrir el PDF automáticamente: {e}")

    return archivo_pdf