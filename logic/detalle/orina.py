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

class OrinaHandler:
    def __init__(self, pdf_instance, formatear_valor_func, dibujar_separador_func):
        self.pdf = pdf_instance
        self.formatear_valor = formatear_valor_func
        self.dibujar_separador = dibujar_separador_func

    def imprimir_orina(self, orina_data):
        if not orina_data:
            return

        self.pdf.check_page_break(30)
        self.pdf.set_font('Arial', 'BU', 11)
        self.pdf.cell(0, 8, "ANÁLISIS DE ORINA", ln=1)

        grupos = agrupar_orina_por_seccion(orina_data)

        for titulo, items in grupos.items():
            self.pdf.set_font('Arial', 'B', 10)
            self.pdf.cell(0, 6, titulo, ln=1)

            self.pdf.set_font('Courier', '', 10)
            for item in items:
                desc = item['descripcion'].strip()
                valor = self.formatear_valor(item['valor'])

                puntos = '.' * max(3, 30 - len(desc))
                texto = f"{desc} {puntos}  "

                self.pdf.set_font('Courier', '', 10)
                self.pdf.write(4, texto)

                self.pdf.set_font('Courier', 'B', 10)
                self.pdf.write(4, f"{valor}\n")
        self.dibujar_separador(self.pdf)