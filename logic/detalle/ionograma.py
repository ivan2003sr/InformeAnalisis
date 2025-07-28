class IonogramaHandler:
    def __init__(self, pdf_instance, formatear_valor_func, dibujar_separador):
        self.pdf = pdf_instance
        self.formatear_valor = formatear_valor_func
        self.dibujar_separador = dibujar_separador

    def imprimir_ionograma(self, lista_ionograma):
        if not lista_ionograma:
            return
        descripcion = "IONOGRAMA"
        self.pdf.check_page_break(30)
        self.pdf.set_font('Arial', 'BU', 11)
        self.pdf.cell(0, 8, f"{descripcion}", ln=1)
        self.pdf.set_font('Courier', '', 10)
        for item in lista_ionograma:
            desc = item['descripcion'].strip()
            valor = self.formatear_valor(item['valor'])
            ref = item['referencia'].strip()
            
            puntos = '.' * max(3, 20 - len(desc))
            texto = f"{desc} {puntos}  "

            self.pdf.set_font('Courier', '', 10)
            self.pdf.write(4, texto)

            self.pdf.set_font('Courier', 'B', 10)
            self.pdf.write(4, f"{valor} mEq/l - ")

            if ref:
                self.pdf.set_font('Courier', '', 10)
                self.pdf.write(4, f"{ref}\n")
        self.dibujar_separador(self.pdf)
