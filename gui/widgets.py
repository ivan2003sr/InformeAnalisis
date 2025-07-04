import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import StringVar
from tkinter import messagebox
from datetime import datetime, date
from gui.subanalisis_modal import VentanaSubanalisis
from logic.db import guardar_cliente, buscar_cliente_por_dni


class AnalisisFrame(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tb.Label(self, text="(Aquí irá la interfaz de análisis)").pack(pady=20)


from logic.db import buscar_cliente_por_dni
from logic.analisis import cargar_analisis_csv, cargar_subanalisis_csv
from logic.informes import generar_pdf_informe

class AnalisisFrame(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.analisis_info = cargar_analisis_csv()
        self.subanalisis_info = cargar_subanalisis_csv()
        self.lista_analisis = []
        self.var_protocolo = StringVar()
        self.var_doctor = StringVar()
        self.var_fecha_extraccion = StringVar()
        self.build_ui()

    def build_ui(self):
        self.var_dni = StringVar()
        self.var_codigo = StringVar()
        self.var_valor = StringVar()
        self.var_descripcion = StringVar()
        self.var_nombre_apellido = StringVar()

        # Fila 0
        tb.Label(self, text="DNI del paciente").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.entry_dni = tb.Entry(self, textvariable=self.var_dni)
        self.entry_dni.grid(row=0, column=1, sticky=EW, padx=5)
        self.entry_dni.bind("<FocusOut>", self.verificar_dni)

        tb.Label(self, text="Protocolo").grid(row=0, column=2, sticky=W, padx=5, pady=5)
        self.entry_protocolo = tb.Entry(self, textvariable=self.var_protocolo)
        self.entry_protocolo.grid(row=0, column=3, sticky=EW, padx=5)

        # Fila 1: nombre y apellido
        self.lbl_nombre_apellido = tb.Label(self, textvariable=self.var_nombre_apellido, foreground="blue")
        self.lbl_nombre_apellido.grid(row=1, column=1, sticky="w", padx=5, pady=(0, 5))

        # Fila 2
        tb.Label(self, text="Código de análisis").grid(row=2, column=0, sticky=W, padx=5, pady=5)
        self.entry_codigo = tb.Entry(self, textvariable=self.var_codigo)
        self.entry_codigo.grid(row=2, column=1, sticky=EW, padx=5)
        self.entry_codigo.bind("<FocusOut>", self.verificar_codigo)

        tb.Label(self, text="Doctor/a").grid(row=2, column=2, sticky=W, padx=5, pady=5)
        self.entry_doctor = tb.Entry(self, textvariable=self.var_doctor)
        self.entry_doctor.grid(row=2, column=3, sticky=EW, padx=5)

        # Fila 3
        tb.Label(self, text="Valor").grid(row=3, column=0, sticky=W, padx=5, pady=5)
        self.entry_valor = tb.Entry(self, textvariable=self.var_valor)
        self.entry_valor.grid(row=3, column=1, sticky=EW, padx=5)

        tb.Label(self, text="Fecha de extracción (YYYY-MM-DD)").grid(row=3, column=2, sticky=W, padx=5, pady=5)
        self.entry_fecha = tb.Entry(self, textvariable=self.var_fecha_extraccion)
        self.entry_fecha.grid(row=3, column=3, sticky=EW, padx=5)

        # Descripción análisis
        self.lbl_desc = tb.Label(self, textvariable=self.var_descripcion, foreground="blue")
        self.lbl_desc.grid(row=4, column=0, columnspan=2, sticky=W, padx=5)

        # Botón agregar
        tb.Button(self, text="Agregar a la lista", bootstyle="primary", command=self.agregar_analisis).grid(row=5, column=0, columnspan=2, pady=10)

        # Treeview tabla
        self.tree = tb.Treeview(self, columns=("codigo", "descripcion"), show="headings", height=10)
        self.tree.heading("codigo", text="Código", anchor="w")
        self.tree.heading("descripcion", text="Descripción", anchor="w")
        self.tree.column("codigo", anchor="w", width=100)
        self.tree.column("descripcion", anchor="w", width=300)
        self.tree.grid(row=6, column=0, columnspan=4, sticky="nsew", padx=5, pady=(0, 10))

        self.menu_ctx = tb.Menu(self, tearoff=0)
        self.menu_ctx.add_command(label="Eliminar análisis", command=self.eliminar_analisis)
        self.tree.bind("<Button-3>", self.mostrar_menu_contextual)

        # Botón imprimir
        tb.Button(self, text="Imprimir informe", bootstyle="success", command=self.imprimir_informe).grid(row=7, column=0, columnspan=2, pady=10)

        # Expandir columnas
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(6, weight=1)

        # Orden manual de TAB (columna por columna)

        self.entry_dni.bind("<Tab>", lambda e: (self.entry_codigo.focus_set(), "break")[1])
        self.entry_codigo.bind("<Tab>", lambda e: (self.entry_valor.focus_set(), "break")[1])
        self.entry_valor.bind("<Tab>", lambda e: (self.entry_protocolo.focus_set(), "break")[1])
        self.entry_protocolo.bind("<Tab>", lambda e: (self.entry_doctor.focus_set(), "break")[1])
        self.entry_doctor.bind("<Tab>", lambda e: (self.entry_fecha.focus_set(), "break")[1])
        self.entry_fecha.bind("<Tab>", lambda e: (self.entry_dni.focus_set(), "break")[1])

    def actualizar_descripcion(self, *args):
        codigo = self.var_codigo.get().strip()
        if not codigo:
            self.var_descripcion.set("")
            return
        if codigo not in self.analisis_info:
            from gui.definir_codigo_modal import AgregarCodigoModal
            modal = AgregarCodigoModal(self, codigo)
            self.wait_window(modal)

            if modal.resultado:
                from logic.analisis import guardar_nuevo_codigo
                guardar_nuevo_codigo(**modal.resultado)
                # Guardar TODOS los campos en analisis_info
                self.analisis_info[codigo] = {
                    "descripcion": modal.resultado["descripcion"],
                    "tecnica": modal.resultado.get("tecnica", ""),
                    "valores_referencia": modal.resultado["valores_referencia"],
                    "unidades": modal.resultado.get("unidades", "")
                }
                self.var_descripcion.set(f"→ {modal.resultado['descripcion']}")
            else:
                self.var_descripcion.set("Código no reconocido.")
        else:
            desc = self.analisis_info[codigo]["descripcion"]
            self.var_descripcion.set(f"→ {desc}")

    def agregar_analisis(self):
        codigo = self.var_codigo.get().strip()
        valor = self.var_valor.get().strip()

        if not codigo:
            messagebox.showwarning("Datos requeridos", "Debe ingresar un código de análisis.")
            return
        analisis_data = self.analisis_info.get(codigo, {})
        desc = analisis_data.get("descripcion", "Sin descripción")
        tecnica = analisis_data.get("tecnica", "")
        ref = analisis_data.get("valores_referencia", "-")
        unidades = analisis_data.get("unidades", "")

        # Si tiene subanálisis, mostrar modal
        if codigo in self.subanalisis_info:
            subanals = self.subanalisis_info[codigo]
            modal = VentanaSubanalisis(self, codigo, subanals)
            self.wait_window(modal)
            self.entry_codigo.focus_set()

            if modal.resultado:
                for sub, val in zip(subanals, modal.resultado):
                    if not val.strip():
                        continue
                    self.lista_analisis.append({
                        'codigo': codigo,
                        'descripcion': sub['nombre'],
                        'valor': val,
                        'referencia': sub['valores_referencia']
                    })
                    self.tree.insert("", "end", values=(codigo, sub['nombre']))
        else:
            if not valor:
                messagebox.showwarning("Dato requerido", "Debe ingresar el valor del análisis.")
                return
            
            self.eliminar_analisis_por_codigo(codigo)
            self.lista_analisis.append({
                'codigo': codigo,
                'descripcion': desc,
                'tecnica': tecnica,
                'valor': valor,
                'referencia': ref,
                'unidades': unidades,
                'valores_referencia': ref 
            })
            self.tree.insert("", "end", values=(codigo, desc))

        self.var_codigo.set("")
        self.var_valor.set("")
        self.var_descripcion.set("")

    def imprimir_informe(self):
        from logic.informes import generar_pdf_informe
        dni = self.var_dni.get().strip()
        protocolo = self.var_protocolo.get().strip()
        doctor = self.var_doctor.get().strip()
        fecha_extraccion = self.var_fecha_extraccion.get().strip() or datetime.today().strftime('%Y-%m-%d')

        if not dni or not self.lista_analisis:
            messagebox.showwarning("Datos faltantes", "Debe ingresar un DNI válido y al menos un análisis.")
            return

        paciente = buscar_cliente_por_dni(dni)
        if not paciente:
            messagebox.showerror("Paciente no encontrado", "El DNI ingresado no está registrado.")
            return



        paciente['edad'] = self.calcular_edad(paciente['fecha_nacimiento'])
        generar_pdf_informe(
            paciente=paciente,
            lista_analisis=self.lista_analisis,
            protocolo=protocolo,
            doctor=doctor,
            fecha_extraccion=fecha_extraccion
        )

        self.lista_analisis.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)

    def calcular_edad(self, fecha_nac_str):
        try:
            fecha_nac = datetime.strptime(fecha_nac_str, "%Y-%m-%d").date()
            hoy = date.today()
            edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            return edad
        except:
            return "?"
        
    def mostrar_menu_contextual(self, event):
        selected = self.tree.identify_row(event.y)
        if selected:
            self.tree.selection_set(selected)
            self.menu_ctx.post(event.x_root, event.y_root)

    def eliminar_analisis(self):
        selected = self.tree.selection()
        if not selected:
            return
        for item in selected:
            valores = self.tree.item(item, "values")
            codigo = valores[0]
            descripcion = valores[1]
            self.lista_analisis = [
                a for a in self.lista_analisis
                if not (a['codigo'] == codigo and a['descripcion'] == descripcion)
            ]
            self.tree.delete(item)

    def verificar_codigo(self, event=None):
        codigo = self.var_codigo.get().strip()
        if not codigo:
            self.var_descripcion.set("")
            return

        if codigo not in self.analisis_info:
            from gui.definir_codigo_modal import AgregarCodigoModal
            modal = AgregarCodigoModal(self, codigo)
            self.wait_window(modal)
            self.entry_codigo.focus_set()

            if modal.resultado:
                from logic.analisis import guardar_nuevo_codigo
                guardar_nuevo_codigo(**modal.resultado)
                self.analisis_info[codigo] = {
                    "descripcion": modal.resultado["descripcion"],
                    "valores_referencia": modal.resultado["valores_referencia"]
                }
                self.var_descripcion.set(f"→ {modal.resultado['descripcion']}")
            else:
                self.var_descripcion.set("Código no reconocido.")
                return
        else:
            desc = self.analisis_info[codigo]["descripcion"]
            self.var_descripcion.set(f"→ {desc}")

        if codigo in self.subanalisis_info:
            subanals = self.subanalisis_info[codigo]
            # Buscar si ya se cargó este código
            valores_precargados = []
            for sub in subanals:
                encontrado = next((a for a in self.lista_analisis
                                if a['codigo'] == codigo and a['descripcion'] == sub['nombre']), None)
                valores_precargados.append(encontrado['valor'] if encontrado else "")

            modal = VentanaSubanalisis(self, codigo, subanals, valores_precargados)
            self.wait_window(modal)

            if modal.resultado:
                self.eliminar_analisis_por_codigo(codigo)
                for sub, val in zip(subanals, modal.resultado):
                    if not val.strip():
                        continue
                    self.lista_analisis.append({
                        'codigo': codigo,
                        'descripcion': sub['nombre'],
                        'valor': val,
                        'referencia': sub['valores_referencia']
                    })
                self.tree.insert("", "end", values=(codigo, sub['nombre'], val, sub['valores_referencia']))

                # Limpiar campos
                self.var_codigo.set("")
                self.var_valor.set("")
                self.var_descripcion.set("")

    def eliminar_analisis_por_codigo(self, codigo):
    # Eliminar del Treeview
        for item in self.tree.get_children():
            valores = self.tree.item(item, "values")
            if valores[0] == codigo:
                self.tree.delete(item)

    # Eliminar de la lista
        self.lista_analisis = [a for a in self.lista_analisis if a['codigo'] != codigo]

    
    def verificar_dni(self, event=None):
        dni = self.var_dni.get().strip()
        if not dni:
            return

        paciente = buscar_cliente_por_dni(dni)
        if paciente:
            nombre = paciente.get("nombre", "")
            apellido = paciente.get("apellido", "")
            self.var_nombre_apellido.set(f"→ {nombre} {apellido}")
            self.paciente_data = paciente
        else:
            from gui.nuevo_paciente_modal import VentanaNuevoPaciente
            modal = VentanaNuevoPaciente(self, dni)
            self.wait_window(modal)
            if modal.resultado:
                self.var_dni.set(modal.resultado["dni"])
                self.var_nombre_apellido.set(f"→ {modal.resultado['nombre']} {modal.resultado['apellido']}")
                self.paciente_data = modal.resultado
            else:
                self.var_dni.set("")
                self.var_nombre_apellido.set("")
                self.paciente_data = None
