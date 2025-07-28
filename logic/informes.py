import os
import locale

from logic.detalle.betaCuant import BetaCuantHandler
from logic.detalle.colesterolHDL import ColesterolHdlHandler
from logic.detalle.hemoglobinaGlicosilada import HemoglobinaGlicosiladaHandler
from logic.detalle.ionograma import IonogramaHandler
from logic.detalle.otros_analisis import OtrosAnalisisHandler
from logic.detalle.hemograma import HemogramaHandler
from logic.detalle.orina import OrinaHandler
from logic.detalle.proteinograma import ProteinogramaHandler
from logic.detalle.colesterolLDL import ColesterolLdlHandler
locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')  # Configurar locale para Argentina
from datetime import datetime
from fpdf import FPDF, HTMLMixin
import webbrowser

class PDF(FPDF, HTMLMixin):

    def header(self):
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png')
        if os.path.exists(logo_path):
            #Alinear logo a la derecha
            self.image(logo_path, x=self.w - 40, y=5, w=30)
        self.set_font('Arial', 'BU', 15)
        self.cell(0, 6, "LABORATORIO DE ANÁLISIS CLÍNICOS", 0, 1, 'L')
        self.set_font('Arial', 'B', 10)
        self.cell(0, 4, "DRA. NORA SILVIA CRESTÁN.", 0, 1, 'L')
        self.set_font('Arial', 'B', 8)
        self.cell(0, 4, "OLASCOAGA 237 - TEL. 0260 - 4422824", 0, 1, 'L')
        self.set_font('Arial', 'I', 8)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')

    def check_page_break(self, threshold=15):
        if self.y + threshold > self.page_break_trigger:
            self.add_page()

def formatear_valor(valor):
    try:
        num = float(valor)
        if num.is_integer():
            return f"{int(num):,}".replace(",", ".")
        else:
            return f"{num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(valor)

def generar_pdf_informe(paciente, lista_analisis, protocolo, doctor, fecha_extraccion):
    
    from collections import defaultdict

    def format_fecha(fecha_str):
        try:
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
            return fecha_obj.strftime('%d/%m/%Y')
        except:
            return fecha_str
    
    fecha_impresion = datetime.now().strftime('%d/%m/%Y')
    fecha_extraccion_fmt = format_fecha(fecha_extraccion)
    fecha_nacimiento_fmt = format_fecha(paciente['fecha_nacimiento'])



    # Crear carpeta para el paciente
    carpeta_nombre = f"{paciente['apellido'].upper()}-{paciente['nombre'].upper()}-{paciente['dni']}"
    carpeta_path = os.path.join(os.getcwd(), carpeta_nombre)
    os.makedirs(carpeta_path, exist_ok=True)

    # Nombre del archivo PDF
    fecha_str = datetime.now().strftime("%Y%m%d %H%M%S")
    archivo_pdf = os.path.join(carpeta_path, f"{paciente['apellido'].upper()}-{fecha_str}.pdf")

    # Crear PDF
    pdf = PDF()
    locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')  # Asegurarse de que el locale esté configurado
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    # Información del paciente
    pdf.set_font('Arial', '', 9)
    pdf.write(4, "Protocolo: ")
    pdf.set_font('Arial', 'B', 9)
    pdf.write(4, f"{formatear_valor(protocolo)}\n")

    pdf.set_font('Arial', '', 9)
    pdf.write(4, "Perteneciente a: ")
    pdf.set_font('Arial', 'B', 9)
    pdf.write(4, f"{paciente['apellido']}, {paciente['nombre']}\n")

    pdf.set_font('Arial', '', 9)
    pdf.write(4, "DNI: ")
    pdf.set_font('Arial', 'B', 9)
    pdf.write(4, f"{formatear_valor(paciente['dni'])} ")
    pdf.set_font('Arial', '', 9)
    pdf.write(4, "Edad: ")
    pdf.set_font('Arial', 'B', 9)
    pdf.write(4, f"{paciente['edad']} años\n")

    pdf.set_font('Arial', '', 9)
    pdf.write(4, "Doctor/a: ")
    pdf.set_font('Arial', 'B', 9)
    pdf.write(4, f"{doctor}\n")

    pdf.set_font('Arial', '', 9)
    pdf.write(4, "Fecha de extracción: ")
    pdf.set_font('Arial', 'B', 9)
    pdf.write(4, f"{fecha_extraccion_fmt}\n")

    pdf.ln(10)

    CODIGOS_ESPECIALES = {
    "hemograma":"475",
    "orina": "711",
    "ionograma": "546",
    "hdl": "1035",
    "ldl": "1040",
    "hba1c": "1070",
    "betaCuant": "1175",
    "proteinograma": "nose"
    }

# Extracción de análisis especiales
    analisis_especiales = {
        nombre: [a for a in lista_analisis if a['codigo'] == cod]
        for nombre, cod in CODIGOS_ESPECIALES.items()
    }

# Resto de los análisis
    todos_codigos_especiales = set(CODIGOS_ESPECIALES.values())
    otros = [a for a in lista_analisis if a['codigo'] not in todos_codigos_especiales]

    hemograma = analisis_especiales["hemograma"]
    orina = analisis_especiales["orina"]
    ionograma = analisis_especiales["ionograma"]
    colesterolHDL = analisis_especiales["hdl"]
    hemoglobinaGlicosilada = analisis_especiales["hba1c"]
    betaCuant = analisis_especiales["betaCuant"]
    proteinograma = analisis_especiales["proteinograma"]
    colesterolLDL = analisis_especiales["ldl"]

    def dibujar_separador(pdf):
            pdf.ln(1)
            y = pdf.get_y()
            pdf.line(10, y, 200, y)
            pdf.ln(1)

  
    hemograma_handler = HemogramaHandler(pdf, formatear_valor, dibujar_separador)
    hemograma_handler.imprimir_hemograma(hemograma)
    
    ionograma_handler = IonogramaHandler(pdf, formatear_valor, dibujar_separador)
    ionograma_handler.imprimir_ionograma(ionograma)

    colesterolHdl_handler = ColesterolHdlHandler(pdf, formatear_valor, dibujar_separador)
    colesterolHdl_handler.imprimir_colesterol_hdl(colesterolHDL)

    colesterolLdl_handler = ColesterolLdlHandler(pdf, formatear_valor, dibujar_separador)
    colesterolLdl_handler.imprimir_colesterol_ldl(colesterolLDL)

    hemoglobina_glicosilada_handler = HemoglobinaGlicosiladaHandler(pdf, formatear_valor, dibujar_separador)
    hemoglobina_glicosilada_handler.imprimir_hemoglobina_glicosilada(hemoglobinaGlicosilada)

    orina_handler = OrinaHandler(pdf, formatear_valor, dibujar_separador)
    orina_handler.imprimir_orina(orina)

    beta_cuant_handler = BetaCuantHandler(pdf, formatear_valor, dibujar_separador)
    beta_cuant_handler.imprimir_beta_cuant(betaCuant)

    proteinograma_handler = ProteinogramaHandler(pdf, formatear_valor, dibujar_separador)
    proteinograma_handler.imprimir_proteinograma(proteinograma)

    otros_analisis_handler = OtrosAnalisisHandler(pdf, formatear_valor, dibujar_separador)
    otros_analisis_handler.imprimir_otros_analisis(otros)

    # Firma
    pdf.ln(15)
    pdf.set_font('Arial', 'I', 11)
    pdf.cell(0, 10, "Firma y sello del responsable:", 0, 1)
    pdf.cell(0, 5, "", 0, 1)
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
