import os
from collections import defaultdict
from html import escape

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

def alinear_referencia(referencia, ancho_total=33):
    if not referencia or '-' not in referencia:
        return referencia.strip()

    izq, der = referencia.split('-', 1)
    izq = izq.strip()
    der = der.strip()

    mitad = ancho_total // 2

    izq_ajustado = izq.rjust(mitad)
    der_ajustado = der.ljust(ancho_total - mitad)

    return f"{izq_ajustado} - {der_ajustado}"



class HemogramaHandler:
    def __init__(self, pdf_instance, formatear_valor, dibujar_separador):
        self.pdf = pdf_instance
        self.formatear_valor = formatear_valor
        self.dibujar_separador = dibujar_separador

    def imprimir_hemograma(self, hemograma):

        if not hemograma:
            return
        
        self.pdf.check_page_break(30)
        self.pdf.set_font('Arial', 'BU', 11)
        self.pdf.cell(0, 8, "HEMOGRAMA", ln=1)

        grupos = agrupar_hemograma_por_seccion(hemograma)
        ya_mostro_formula = False  # para no repetir FÓRMULA LEUCOCITARIA

        for titulo, items in grupos.items():

            self.pdf.check_page_break(15 + len(items) * 3)
            # TITULARES
            if titulo == "SERIE ROJA":
                self.dibujar_separador(self.pdf)
                self.pdf.set_font('Arial', 'BU', 10)
                self.pdf.cell(75, 7, "SERIE ROJA", 0, 0, 'L')
                self.pdf.cell(20, 7, "VALORES", 0, 0, 'R')  # espacio vacío para columna valor (que no tiene encabezado)
                self.pdf.cell(75, 7, "VALORES NORMALES", 0, 1, 'C')
            elif titulo == "SERIE BLANCA":
                self.pdf.set_font('Arial', 'BU', 10)
                self.pdf.cell(0, 4, titulo, ln=1)
            elif titulo.startswith("FÓRMULA LEUCOCITARIA"):
                if not ya_mostro_formula:
                    self.pdf.set_font('Arial', 'BU', 10)
                    self.pdf.cell(0, 4, "FÓRMULA LEUCOCITARIA", ln=1)
                    ya_mostro_formula = True
                subtitulo = titulo.split(" - ")[1]
                self.pdf.set_font('Arial', 'BU', 9)
                self.pdf.cell(0, 3, subtitulo, ln=1)

            for item in items:
                desc = item['descripcion']
                valor = self.formatear_valor(item['valor'])
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
                self.pdf.set_font('Courier', '', 10)
                self.pdf.cell(ancho_desc, 3, texto, 0, 0, 'L')

            # Valor en negrita, alineado derecha
                self.pdf.set_font('Courier', 'B', 10)
                self.pdf.cell(ancho_valor, 3, valor, 0, 0, 'R')

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

                self.pdf.set_font('Courier', '', 10)
                self.pdf.cell(ancho_ref, 3, alinear_referencia(ref), 0, 1, 'C')
            self.pdf.ln(3)
        self.dibujar_separador(self.pdf)