import os
from html import escape
from fpdf import FPDF

class ColesterolHdlHandler:
    def __init__(self, pdf_instance, formatear_valor_func, dibujar_separador):
        self.pdf = pdf_instance
        self.formatear_valor = formatear_valor_func
        self.dibujar_separador = dibujar_separador
    def imprimir_colesterol_hdl(self, lista_colesterol_hdl):
        if not lista_colesterol_hdl:
            return

        self.pdf.check_page_break(60)

        valor_hdl = self.formatear_valor(lista_colesterol_hdl[0]['valor'])
        unidades = lista_colesterol_hdl[0]['unidades']

        # Título principal
        self.pdf.set_font('Arial', 'BU', 10)
        self.pdf.cell(0, 5, f"Colesterol HDL: ", ln=1)
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(0,5,f"Valores obtenidos: {valor_hdl} {unidades}.")

        self.pdf.ln(2)

        # Título "NORMALES"
        self.pdf.set_font('Arial', 'BU', 10)
        self.pdf.cell(0, 4, "NORMALES", ln=1, align='C')

        # Encabezado de columnas
        col1_w = 80
        col2_w = 50
        col3_w = 50

        self.pdf.set_font('Courier', 'B', 10)
        self.pdf.cell(col1_w, 4, "", 0, 0)
        self.pdf.cell(col2_w, 4, "HOMBRES", 0, 0, 'L')
        self.pdf.cell(col3_w, 4, "MUJERES", 0, 1, 'L')

        # Datos
        self.pdf.set_font('Courier', '', 10)
        filas = [
            ("Pronóstico favorable", "Mayor a 0,55 g/l", "Mayor a 0,65 g/l"),
            ("Riesgo standard", "De 0,35 a 0,55 g/l", "De 0,45 a 0,65 g/l"),
            ("Indicador de riesgo", "Menor de 0,35 g/l", "Menor de 0,45 g/l"),
            ("Niños hasta 19 años", "De 0,32 a 0,62 g/l", "")
        ]

        for desc, hombres, mujeres in filas:
            texto_ancho = self.pdf.get_string_width(desc)
            espacio_restante = col1_w - texto_ancho
            ancho_punto = self.pdf.get_string_width('.')
            num_puntos = max(3, int(espacio_restante / ancho_punto))
            puntos = '.' * num_puntos
            texto_punteado = f"{desc} {puntos}"

            self.pdf.cell(col1_w, 4, texto_punteado, 0, 0, 'L')
            self.pdf.cell(col2_w, 4, hombres, 0, 0, 'L')
            self.pdf.cell(col3_w, 4, mujeres, 0, 1, 'L')
        self.dibujar_separador(self.pdf)