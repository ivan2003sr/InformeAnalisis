import os
from html import escape
from fpdf import FPDF

class HemoglobinaGlicosiladaHandler:
    def __init__(self, pdf_instance, formatear_valor_func, dibujar_separador):
        self.pdf = pdf_instance
        self.formatear_valor = formatear_valor_func
        self.dibujar_separador = dibujar_separador

    def imprimir_hemoglobina_glicosilada(self, lista_hemoglobina_glicosilada):
        if not lista_hemoglobina_glicosilada:
            return

        self.pdf.check_page_break(30)

        valor_hba1c = self.formatear_valor(lista_hemoglobina_glicosilada[0]['valor'])
        unidades = lista_hemoglobina_glicosilada[0]['unidades']

        self.pdf.set_font('Arial', 'BU', 10)
        self.pdf.cell(0, 4, f"HEMOGLOBINA GLICOSILADA (HBA1C).", ln=1)
        self.pdf.set_font('Arial', 'B', 8)
        self.pdf.cell(0, 4, f"Resultado: {valor_hba1c} {unidades}.", ln=1)

        self.pdf.cell(0, 4, f"{lista_hemoglobina_glicosilada[0]['tecnica']}. {lista_hemoglobina_glicosilada[0]['valores_referencia']}.", ln=1)
        self.pdf.set_font('Arial', '', 8)
        self.pdf.cell(0, 4, "Tabla de equivalencias de Hemoglobina Glicada, al valor teórico promedio ", ln=1)
        self.pdf.cell(0, 4, "       de glucemia de los últimos 40 a 45 días.", ln=1)

        self.pdf.set_font('Courier', 'B', 8)
        col1_w = 60
        col2_w = 40
        altura_fila = 4
        self.pdf.cell(col1_w, altura_fila, "GLUCEMIA PROMEDIO [g/l]", 0, 0, 'C')
        self.pdf.cell(col2_w, altura_fila, "Hb A1c [%]", 0, 1, 'C')

        # Datos
        self.pdf.set_font('Courier', '', 8)
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
            self.pdf.cell(col1_w, altura_fila, glucemia, 0, 0, 'C')
            self.pdf.cell(col2_w, altura_fila, hba1c, 0, 1, 'C')

        self.dibujar_separador(self.pdf)
