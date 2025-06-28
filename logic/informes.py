import os
from datetime import datetime
from fpdf import FPDF
import webbrowser

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'BU', 15)
        self.cell(0, 6, "LABORATORIO DE ANÁLISIS CLÍNICOS", 0, 1, 'L')
        self.set_font('Arial', 'B', 10)
        self.cell(0, 4, "DRA. NORA SILVIA CRESTÁN.", 0, 1, 'L')
        self.set_font('Arial', 'B', 8)
        self.cell(0, 4, "OLASCOAGA 237 - TEL. 0260 - 4422824", 0, 1, 'L')
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'PÁGINA {self.page_no()}/{{nb}}', 0, 0, 'R')
        self.ln(5)

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

def generar_pdf_informe(paciente, lista_analisis, protocolo, doctor, fecha_extraccion, logo_path=None):
    
    from collections import defaultdict
    
    fecha_impresion = datetime.now().strftime('%d/%m/%Y')
    fecha_extraccion_fmt = format_fecha(fecha_extraccion)
    fecha_nacimiento_fmt = format_fecha(paciente['fecha_nacimiento'])

    def agrupar_hemograma_por_seccion(analisis):
        grupos = {
            "SERIE ROJA": [],
            "SERIE BLANCA": [],
            "FORMULA LEUCOCITARIA - SISTEMA MIELOIDE": [],
            "FORMULA LEUCOCITARIA - SISTEMA LINFOIDE": [],
            "FORMULA LEUCOCITARIA - SISTEMA RETICULO ENDOTELIAL": []
        }

        for item in analisis:
            desc = item['descripcion'].lower()
            if any(k in desc for k in ["hematíes", "hemoglobina", "volumen globular", "hematocrito"]):
                grupos["SERIE ROJA"].append(item)
            elif "leucocitos" in desc and "segmentado" not in desc and "cayado" not in desc:
                grupos["SERIE BLANCA"].append(item)
            elif any(k in desc for k in ["metamielocitos", "cayado", "segmentados", "eosinófilos", "basófilos"]):
                grupos["FORMULA LEUCOCITARIA - SISTEMA MIELOIDE"].append(item)
            elif "linfocitos" in desc:
                grupos["FORMULA LEUCOCITARIA - SISTEMA LINFOIDE"].append(item)
            elif "monocitos" in desc:
                grupos["FORMULA LEUCOCITARIA - SISTEMA RETICULO ENDOTELIAL"].append(item)

        return grupos
    
    # Configuración del logo (si se desea usar luego)
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
    pdf.set_font('Arial', '', 9)
    pdf.cell(0, 4, f"Protocolo: {protocolo}", ln=1)
    pdf.cell(0, 4, f"Perteneciente a: {paciente['apellido']}, {paciente['nombre']}", ln=1)
    pdf.cell(0, 4, f"DNI: {paciente['dni']}", ln=1)
    pdf.cell(0, 4, f"Fecha de nacimiento: {fecha_nacimiento_fmt}", ln=1)
    pdf.cell(0, 4, f"Edad: {paciente['edad']} años", ln=1)
    pdf.cell(0, 4, f"Doctor/a: {doctor}", ln=1)
    pdf.cell(0, 4, f"Fecha de extracción: {fecha_extraccion_fmt}", ln=1)
    pdf.cell(0, 4, f"Fecha de impresión: {fecha_impresion}", ln=1)
    pdf.ln(10)

    hemograma = [a for a in lista_analisis if a['codigo'] == "475"]
    otros = [a for a in lista_analisis if a['codigo'] != "475"]

    if hemograma:
        pdf.set_font('Times', 'BU', 12)
        pdf.cell(0, 8, "HEMOGRAMA", ln=1)

        grupos = agrupar_hemograma_por_seccion(hemograma)
        ya_mostro_formula = False  # para no repetir FORMULA LEUCOCITARIA

        for titulo, items in grupos.items():
            # TITULARES
            if titulo == "SERIE ROJA":
                pdf.set_font('Times', 'BU', 11)
                pdf.set_font('Times', 'BU', 11)
                pdf.cell(75, 7, "SERIE ROJA", 0, 0, 'L')
                pdf.cell(20, 7, "VALORES", 0, 0, 'R')  # espacio vacío para columna valor (que no tiene encabezado)
                pdf.cell(75, 7, "VALORES NORMALES", 0, 1, 'C')
            elif titulo == "SERIE BLANCA":
                pdf.set_font('Times', 'BU', 11)
                pdf.cell(0, 4, titulo, ln=1)
            elif titulo.startswith("FORMULA LEUCOCITARIA"):
                if not ya_mostro_formula:
                    pdf.set_font('Times', 'BU', 11)
                    pdf.cell(0, 4, "FORMULA LEUCOCITARIA", ln=1)
                    ya_mostro_formula = True
                subtitulo = titulo.split(" - ")[1]
                pdf.set_font('Times', 'BU', 10)
                pdf.cell(0, 3, subtitulo, ln=1)

            # DETALLES

            def formatear_valor(valor):
                try:
                    num = float(valor)
                    if num.is_integer():
                        return f"{int(num):,}".replace(",", ".")
                    else:
                        return f"{num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                except:
                    return str(valor)

            for item in items:
                desc = item['descripcion']
                valor = formatear_valor(item['valor'])
                ref = item['referencia']

            # Ajuste de columnas
                ancho_desc = 75
                ancho_valor = 20
                ancho_ref = 75
                max_chars = int(ancho_desc / 2.5)
                len_desc = len(desc)

            # Descripción + puntos (todo en misma celda)
                cant_puntos = max(3, max_chars - len_desc - 1)
                puntos = '.' * cant_puntos
                texto = f"{desc} {puntos}"
                pdf.set_font('Courier', '', 10)
                pdf.cell(ancho_desc, 3, texto, 0, 0, 'L')

            # Valor en negrita, alineado derecha
                pdf.set_font('Courier', 'B', 10)
                pdf.cell(ancho_valor, 3, valor, 0, 0, 'R')

            # Referencia, centrado

                def alinear_referencia(referencia, ancho_total=33):
                    if not referencia or '-' not in referencia:
                        return referencia.strip()

                    izq, der = referencia.split('-', 1)
                    izq = izq.strip()
                    der = der.strip()

                # Dividimos el total entre ambos lados (más espacio para izq si necesario)
                    mitad = ancho_total // 2

                    izq_ajustado = izq.rjust(mitad)
                    der_ajustado = der.ljust(ancho_total - mitad)

                    return f"{izq_ajustado} - {der_ajustado}"
                
                pdf.set_font('Courier', '', 10)
                pdf.cell(ancho_ref, 3, alinear_referencia(ref), 0, 1, 'C')

            pdf.ln(3)



        

    # Otros análisis
    if otros:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "OTROS ANÁLISIS", 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(80, 10, "Análisis", 1, 0, 'C', True)
        pdf.cell(30, 10, "Valor", 1, 0, 'C', True)
        pdf.cell(50, 10, "Referencia", 1, 1, 'C', True)

        fill = False
        for analisis in otros:
            valor = str(analisis['valor'])
            referencia = analisis['referencia']
            partes = referencia.rsplit(' ', 1)
            valor_unidades = f"{valor}"
            if len(partes) == 2 and any(c.isalpha() for c in partes[1]):
                valor_unidades += f" {partes[1]}"
            pdf.set_fill_color(240, 240, 240) if fill else pdf.set_fill_color(255, 255, 255)
            pdf.cell(80, 8, analisis['descripcion'], 1, 0, 'L', fill)
            pdf.cell(30, 8, valor_unidades, 1, 0, 'C', fill)
            pdf.cell(50, 8, referencia, 1, 1, 'C', fill)
            fill = not fill


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
