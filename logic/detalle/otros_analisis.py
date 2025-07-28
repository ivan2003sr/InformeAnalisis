from html import escape

class OtrosAnalisisHandler:
    def __init__(self, pdf_instance, formatear_valor_func, dibujar_separador):
        self.pdf = pdf_instance
        self.formatear_valor = formatear_valor_func
        self.dibujar_separador = dibujar_separador

    def imprimir_otros_analisis(self, lista_otros_analisis):
        if not lista_otros_analisis:
            return
        self.pdf.ln(5)

        for analisis in lista_otros_analisis:
            self.pdf.check_page_break(20)

            self.dibujar_separador(self.pdf)
            self.pdf.set_font('Arial', '', 10)
            # Obtener datos del análisis
            descripcion = analisis['descripcion'].strip()
            tecnica = analisis['tecnica'].strip()
            valor = self.formatear_valor(analisis['valor']).strip()
            ref = analisis['valores_referencia'].strip()
            unidades = analisis['unidades'].strip() 
            codigo = analisis['codigo'].strip()
            
            # Construir el texto formateado
            linea1 = f"<b>{escape(descripcion)}</b> {escape(tecnica)}"
            
            valor_html = f"<b>{escape(valor)} {escape(unidades)}</b>"
            normal_html = f"{escape(ref)} {escape(unidades)}"

            if codigo == "1040":
                linea2_html = f"Resultado: {valor_html} - {normal_html}"
            elif codigo == "nose2":
                linea2_html = f"Contiene: {valor_html} - {normal_html}"
            elif "\n" in ref:
                linea2_html = f"Contiene: {valor_html} - Normal: {escape(ref.splitlines()[0].strip())}."

                for linea in ref.splitlines()[1:]:
                    if linea.strip():
                        linea2_html += f"<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{escape(linea)}."
             
            else:
                linea2_html = f"Resultado: {valor_html} - Normal: {normal_html}"

            self.pdf.write_html(f"<font face='Arial' size='10'>{linea1}</font>")
            self.pdf.write_html(f"<font face='Arial' size='10'>{linea2_html}</font>")
            self.pdf.ln(2)
        self.dibujar_separador(self.pdf)