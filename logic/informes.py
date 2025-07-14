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
    "hemograma": "475",
    "orina": "711",
    "ionograma": "546",
    "hdl": "1035",
    "hba1c": "1070"
    }

# Extracción de análisis especiales
    analisis_especiales = {
        nombre: [a for a in lista_analisis if a['codigo'] == cod]
        for nombre, cod in CODIGOS_ESPECIALES.items()
    }

# Resto de los análisis
    otros = [
        a for a in lista_analisis
        if a['codigo'] not in CODIGOS_ESPECIALES.values()
    ]

    hemograma = analisis_especiales["hemograma"]
    orina = analisis_especiales["orina"]
    ionograma = analisis_especiales["ionograma"]
    colesterolHDL = analisis_especiales["hdl"]
    hemoglobinaGlicosilada = analisis_especiales["hba1c"]

    def dibujar_separador(pdf):
            pdf.ln(1)
            y = pdf.get_y()
            pdf.line(10, y, 200, y)
            pdf.ln(1)

    if hemograma:
        pdf.check_page_break(30)
        pdf.set_font('Arial', 'BU', 11)
        pdf.cell(0, 8, "HEMOGRAMA", ln=1)

        grupos = agrupar_hemograma_por_seccion(hemograma)
        ya_mostro_formula = False  # para no repetir FÓRMULA LEUCOCITARIA

        for titulo, items in grupos.items():

            pdf.check_page_break(15 + len(items) * 3)
            # TITULARES
            if titulo == "SERIE ROJA":
                pdf.set_font('Arial', 'BU', 10)
                pdf.set_font('Arial', 'BU', 10)
                pdf.cell(75, 7, "SERIE ROJA", 0, 0, 'L')
                pdf.cell(20, 7, "VALORES", 0, 0, 'R')  # espacio vacío para columna valor (que no tiene encabezado)
                pdf.cell(75, 7, "VALORES NORMALES", 0, 1, 'C')
            elif titulo == "SERIE BLANCA":
                pdf.set_font('Arial', 'BU', 10)
                pdf.cell(0, 4, titulo, ln=1)
            elif titulo.startswith("FÓRMULA LEUCOCITARIA"):
                if not ya_mostro_formula:
                    pdf.set_font('Arial', 'BU', 10)
                    pdf.cell(0, 4, "FÓRMULA LEUCOCITARIA", ln=1)
                    ya_mostro_formula = True
                subtitulo = titulo.split(" - ")[1]
                pdf.set_font('Arial', 'BU', 9)
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
        dibujar_separador(pdf)
    

    if ionograma:
        pdf.check_page_break(30)
        pdf.set_font('Arial', 'BU', 11)
        pdf.cell(0, 8, "IONOGRAMA", ln=1)
        pdf.set_font('Courier', '', 10)
        for item in ionograma:
            desc = item['descripcion'].strip()
            valor = formatear_valor(item['valor'])
            ref = item['referencia'].strip()
            
            puntos = '.' * max(3, 20 - len(desc))
            texto = f"{desc} {puntos}  "

            pdf.set_font('Courier', '', 10)
            pdf.write(4, texto)

            pdf.set_font('Courier', 'B', 10)
            pdf.write(4, f"{valor} mEq/l - ")

            if ref:
                pdf.set_font('Courier', '', 10)
                pdf.write(4, f"{ref}\n")
        dibujar_separador(pdf)

    if colesterolHDL:
        pdf.check_page_break(60)
        
        valor_hdl = formatear_valor(colesterolHDL[0]['valor'])
        unidades = colesterolHDL[0]['unidades']

        # Título principal
        pdf.set_font('Arial', 'BU', 10)
        pdf.cell(0, 8, f"Colesterol HDL: ", ln=1)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0,8,f"Valores obtenidos: {valor_hdl} {unidades}.")

        pdf.ln(2)

        # Título "NORMALES"
        pdf.set_font('Arial', 'BU', 10)
        pdf.cell(0, 6, "NORMALES", ln=1, align='C')

        # Encabezado de columnas
        col1_w = 80
        col2_w = 40
        col3_w = 40

        pdf.set_font('Courier', 'B', 10)
        pdf.cell(col1_w, 4, "", 0, 0)
        pdf.cell(col2_w, 4, "HOMBRES", 0, 0, 'L')
        pdf.cell(col3_w, 4, "MUJERES", 0, 1, 'L')

        # Datos
        pdf.set_font('Courier', '', 10)
        filas = [
            ("Pronóstico favorable", "Mayor a 0,55 g/l", "Mayor a 0,65 g/l"),
            ("Riesgo standard", "De 0,35 a 0,55 g/l", "De 0,45 a 0,65 g/l"),
            ("Indicador de riesgo", "Menor de 0,35 g/l", "Menor de 0,45 g/l"),
            ("Niños hasta 19 años", "De 0,32 a 0,62 g/l", "")
        ]

        for desc, hombres, mujeres in filas:
            texto_ancho = pdf.get_string_width(desc)
            espacio_restante = col1_w - texto_ancho
            ancho_punto = pdf.get_string_width('.')
            num_puntos = max(3, int(espacio_restante / ancho_punto))
            puntos = '.' * num_puntos
            texto_punteado = f"{desc} {puntos}"

            pdf.cell(col1_w, 4, texto_punteado, 0, 0, 'L')
            pdf.cell(col2_w, 4, hombres, 0, 0, 'L')
            pdf.cell(col3_w, 4, mujeres, 0, 1, 'L')
        dibujar_separador(pdf)

    if hemoglobinaGlicosilada:
        pdf.check_page_break(30)
        
        valor_hba1c = formatear_valor(hemoglobinaGlicosilada[0]['valor'])
        unidades = hemoglobinaGlicosilada[0]['unidades']

        pdf.set_font('Arial', 'BU', 10)
        pdf.cell(0, 4, f"HEMOGLOBINA GLICOSILADA (HBA1C).", ln=1)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(0, 4, f"Resultado: {valor_hba1c} {unidades}.", ln=1)
        pdf.set_font('Arial', '', 8)
        pdf.cell(0, 4, f"{hemoglobinaGlicosilada[0]['tecnica']}. {hemoglobinaGlicosilada[0]['valores_referencia']}.", ln=1)
        pdf.cell(0, 4, "Tabla de equivalencias de Hemoglobina Glicada, al valor teórico promedio ", ln=1)
        pdf.cell(0, 4, "de glucemia de los últimos 40 a 45 días.", ln=1)

        pdf.set_font('Courier', 'B', 8)
        col1_w = 60
        col2_w = 40
        altura_fila = 4
        pdf.cell(col1_w, altura_fila, "GLUCEMIA PROMEDIO [g/l]", 0, 0, 'L')
        pdf.cell(col2_w, altura_fila, "Hb A1c [%]", 0, 1, 'L')

        # Datos
        pdf.set_font('Courier', '', 8)
        tabla_equivalencias = [
            ("0,6", "4"),
            ("0,9", "5"),
            ("1,2", "6"),
            ("1,5", "7"),
            ("1,8", "8"),
            ("2,1", "9"),
            ("2,4", "10"),
            ("2,7", "11"),
            ("3,0", "12"),
        ]

        for glucemia, hba1c in tabla_equivalencias:
            pdf.cell(col1_w, altura_fila, glucemia, 0, 0, 'C')
            pdf.cell(col2_w, altura_fila, hba1c, 0, 1, 'C')

        dibujar_separador(pdf)

    if orina:
        pdf.check_page_break(30)
        pdf.set_font('Arial', 'BU', 11)
        pdf.cell(0, 8, "ANÁLISIS DE ORINA", ln=1)

        grupos = agrupar_orina_por_seccion(orina)

        for titulo, items in grupos.items():
            pdf.check_page_break(15 + len(items) * 3)
            pdf.set_font('Arial', 'B', 10)
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
        dibujar_separador(pdf)

    # Otros análisis
    if otros:
        
        pdf.ln(5)
        for analisis in otros:
            pdf.check_page_break(20)


            dibujar_separador(pdf)
            pdf.set_font('Arial', '', 10)
            # Obtener datos del análisis
            descripcion = analisis['descripcion'].strip()
            tecnica = analisis['tecnica'].strip()
            valor = formatear_valor(analisis['valor']).strip()
            ref = analisis['valores_referencia'].strip()
            unidades = analisis['unidades'].strip() 
            codigo = analisis['codigo'].strip()
            
            # Construir el texto formateado
            linea1 = f"{escape(descripcion)} {escape(tecnica)}"
            valor_html = f"<b>{escape(valor)} {escape(unidades)}</b>"
            normal_html = f"{escape(ref)} {escape(unidades)}"

            if codigo == "1040":
                linea2_html = f"Resultado: {valor_html} - {normal_html}"
            elif "\n" in ref:
            # Multilínea: usar formato especial "Contiene" con saltos
                linea2_html = f"Contiene: {valor_html} - Normal: {escape(ref.splitlines()[0].strip())}."

                for linea in ref.splitlines()[1:]:
                    if linea.strip():
                        linea2_html += f"<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{escape(linea)}."
             
            else:
                linea2_html = f"Resultado: {valor_html} - Normal: {normal_html}"

            pdf.multi_cell(0, 4, linea1, 0, 'L')
            pdf.write_html(f"<font face='Arial' size='10'>{linea2_html}</font>")
            pdf.ln(2)
        dibujar_separador(pdf)

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
