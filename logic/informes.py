import os
import locale
locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')  # Configurar locale para Argentina
from datetime import datetime
from fpdf import FPDF, HTMLMixin
from html import escape
import webbrowser

class PDF(FPDF, HTMLMixin):

    def header(self):
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png')
        if os.path.exists(logo_path):
            x_pos = self.w - 30 - 30  
            self.image(logo_path, x=x_pos, y=8, w=30)
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

    def check_page_break(self, threshold=15):
        if self.y + threshold > self.page_break_trigger:
            self.add_page()

def format_fecha(fecha_str):
    try:
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
        return fecha_obj.strftime('%d/%m/%Y')
    except:
        return fecha_str
    
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
    
    fecha_impresion = datetime.now().strftime('%d/%m/%Y')
    fecha_extraccion_fmt = format_fecha(fecha_extraccion)
    fecha_nacimiento_fmt = format_fecha(paciente['fecha_nacimiento'])

    def agrupar_hemograma_por_seccion(analisis):
        grupos = {
            "SERIE ROJA": [],
            "SERIE BLANCA": [],
            "FÓRMULA LEUCOCITARIA - SISTEMA MIELOIDE": [],
            "FÓRMULA LEUCOCITARIA - SISTEMA LINFOIDE": [],
            "FÓRMULA LEUCOCITARIA - SISTEMA RETICULO ENDOTELIAL": []
        }

        for item in analisis:
            desc = item['descripcion'].lower()
            if any(k in desc for k in ["hematíes", "hemoglobina", "volumen globular", "hematocrito"]):
                grupos["SERIE ROJA"].append(item)
            elif "leucocitos" in desc and "segmentado" not in desc and "cayado" not in desc:
                grupos["SERIE BLANCA"].append(item)
            elif any(k in desc for k in ["metamielocitos", "cayado", "segmentados", "eosinófilos", "basófilos"]):
                grupos["FÓRMULA LEUCOCITARIA - SISTEMA MIELOIDE"].append(item)
            elif "linfocitos" in desc:
                grupos["FÓRMULA LEUCOCITARIA - SISTEMA LINFOIDE"].append(item)
            elif "monocitos" in desc:
                grupos["FÓRMULA LEUCOCITARIA - SISTEMA RETICULO ENDOTELIAL"].append(item)

        return grupos
    
    def agrupar_orina_por_seccion(analisis):
        grupos = {
            "EXAMEN FÍSICO": [],
            "EXAMEN QUÍMICO": [],
            "EXAMEN MICROSCÓPICO": [],
        }

        for item in analisis:
            desc = item['descripcion'].lower()
            if any(k in desc for k in ["color", "aspecto", "espuma", "sedimento", "densidad", "reaccion", "ph"]):
                grupos["EXAMEN FÍSICO"].append(item)
            elif any(k in desc for k in ["protTotales", "hemoglobina", "glucosa", "acetona", "pigmentosBiliares", "acidosBiliares", "urobilina"]):
                grupos["EXAMEN QUÍMICO"].append(item)
            else:
                grupos["EXAMEN MICROSCÓPICO"].append(item)

        return grupos

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
    pdf.write(4, f"{paciente['dni']} ")
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


    hemograma = [a for a in lista_analisis if a['codigo'] == "475"]
    orina = [a for a in lista_analisis if a['codigo'] == "711"]
    otros = [a for a in lista_analisis if a['codigo'] not in ("475", "711")]

    
    if orina:
        pdf.check_page_break(30)
        pdf.set_font('Times', 'BU', 12)
        pdf.cell(0, 8, "ANÁLISIS DE ORINA", ln=1)

        grupos = agrupar_orina_por_seccion(orina)

        for titulo, items in grupos.items():
            pdf.check_page_break(15 + len(items) * 3)
            pdf.set_font('Times', 'BU', 11)
            pdf.cell(0, 6, titulo, ln=1)

            pdf.set_font('Courier', '', 10)
            for item in items:
                desc = item['descripcion'].strip()
                valor = formatear_valor(item['valor'])

                puntos = '.' * max(3, 30 - len(desc))
                texto = f"{desc} {puntos}  "

                pdf.set_font('Courier', '', 10)
                pdf.write(4, texto)

                pdf.set_font('Courier', 'B', 10)
                pdf.write(4, f"{valor}\n")

        pdf.ln(4)

    if hemograma:
        pdf.check_page_break(30)
        pdf.set_font('Times', 'BU', 12)
        pdf.cell(0, 8, "HEMOGRAMA", ln=1)

        grupos = agrupar_hemograma_por_seccion(hemograma)
        ya_mostro_formula = False  # para no repetir FÓRMULA LEUCOCITARIA

        for titulo, items in grupos.items():

            pdf.check_page_break(15 + len(items) * 3)
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
            elif titulo.startswith("FÓRMULA LEUCOCITARIA"):
                if not ya_mostro_formula:
                    pdf.set_font('Times', 'BU', 11)
                    pdf.cell(0, 4, "FÓRMULA LEUCOCITARIA", ln=1)
                    ya_mostro_formula = True
                subtitulo = titulo.split(" - ")[1]
                pdf.set_font('Times', 'BU', 10)
                pdf.cell(0, 3, subtitulo, ln=1)

            # DETALLES

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
        def dibujar_separador(pdf):
            pdf.ln(1)
            y = pdf.get_y()
            pdf.line(10, y, 200, y)
            pdf.ln(1)

        fill = False
        for analisis in otros:
            pdf.check_page_break(20)


            dibujar_separador(pdf)
            pdf.set_font('Arial', '', 11)
            # Obtener datos del análisis
            descripcion = analisis['descripcion'].strip()
            tecnica = analisis['tecnica'].strip()
            valor = analisis['valor'].strip()
            ref = analisis['valores_referencia'].strip()
            unidades = analisis['unidades'].strip() 
            codigo = analisis['codigo'].strip()
            
            # Construir el texto formateado
            linea1 = f"{escape(descripcion)} {escape(tecnica)}"
            valor_html = f"<b>{escape(valor)} {escape(unidades)}</b>"
            normal_html = f"{escape(ref)} {escape(unidades)}"

            if codigo == "1040":
                linea2_html = f"Resultado: {valor_html} - {normal_html}"
            else:
                linea2_html = f"Resultado: {valor_html} - Normal: {normal_html}"

            pdf.multi_cell(0, 4, linea1, 0, 'L')
            pdf.write_html(f"<font face='Arial' size='11'>{linea2_html}</font>")
            pdf.ln(2)


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
