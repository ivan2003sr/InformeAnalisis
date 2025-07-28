class BetaCuantHandler:
    def __init__(self, pdf_instance, formatear_valor_func, dibujar_separador):
        self.pdf = pdf_instance
        self.formatear_valor = formatear_valor_func
        self.dibujar_separador = dibujar_separador

    def imprimir_beta_cuant(self, lista_beta_cuant):
        if not lista_beta_cuant:
            return

        self.pdf.check_page_break(30)

        valor_beta = self.formatear_valor(lista_beta_cuant[0]['valor'])
        unidades = lista_beta_cuant[0]['unidades']
        descripcion = lista_beta_cuant[0]['descripcion']
        tecnica = lista_beta_cuant[0]['tecnica'].strip()

        self.pdf.set_font('Arial', 'B', 9)
        self.pdf.cell(0, 4, f"{descripcion}", ln=1)
        self.pdf.set_font('Arial', 'B', 8)
        self.pdf.cell(0, 4, f"Valor obtenido: {valor_beta} {unidades}", ln=1)
        self.pdf.set_font('Arial', '', 8)
        self.pdf.cell(0,4, f"{tecnica}.", ln=1)

        self.pdf.set_font('Arial', 'BU', 8)
        self.pdf.cell(0, 8, "Tabla de valores de referencia", ln=1)

# Encabezado
        self.pdf.set_font('Arial', 'B', 7)
        self.pdf.set_fill_color(220, 220, 220)  # Gris claro para encabezado
        self.pdf.cell(30, 4, "Etapa", border=1, align='C', fill=True)
        self.pdf.cell(30, 4, "Valores en [UI/l]", border=1, align='C', fill=True)

        self.pdf.ln()

# Datos de la tabla
        filas = [
            ("No embarazada", "Hasta 5"),
            ("4ta. Semana", "40 - 4.800"),
            ("5ta. Semana", "270 - 28.700"),
            ("6ta. Semana", "3.700 - 84.900"),
            ("7ma. semana", "9.700 - 120.000"),
            ("8va. semana", "31.100 - 184.000"),
            ("9na. semana", "61.000 - 152.000"),
            ("10a. semana", "22.000 - 143.000"),
            ("14a. semana", "14.300 - 75.800"),
            ("15a. semana", "12.300 - 60.300"),
            ("16a. semana", "8.800 - 54.500"),
            ("17a. semana", "8.100 - 51.300"),
            ("18a. semana", "3.900 - 49.400"),
            ("19a. semana", "3.600 - 56.600"),
        ]

        self.pdf.set_font('Courier', '', 7)
        for etapa, valores in filas:
            self.pdf.cell(30, 3, etapa, border=1, align='C')
            self.pdf.cell(30, 3, valores, border=1, align='C')

            self.pdf.ln()

        self.pdf.set_font('Arial', '', 7)
        self.pdf.cell(0, 3, "No embarazadas: hasta 5 UI/l", ln=1)
        self.pdf.cell(0, 3, "Hombres: hasta 2 UI/l", ln=1)
        self.dibujar_separador(self.pdf)