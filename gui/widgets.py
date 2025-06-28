import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import StringVar
from tkinter import messagebox
from datetime import datetime, date
from gui.subanalisis_modal import VentanaSubanalisis
from logic.db import guardar_cliente, buscar_cliente_por_dni

class ClienteFrame(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.var_dni = StringVar()
        self.var_nombre = StringVar()
        self.var_apellido = StringVar()
        self.var_fecha_nac = StringVar()
        self.var_edad = StringVar()

        tb.Label(self, text="DNI").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        tb.Entry(self, textvariable=self.var_dni).grid(row=0, column=1, sticky=EW, padx=5, pady=5)

        tb.Label(self, text="Nombre").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        tb.Entry(self, textvariable=self.var_nombre).grid(row=1, column=1, sticky=EW, padx=5, pady=5)

        tb.Label(self, text="Apellido").grid(row=2, column=0, sticky=W, padx=5, pady=5)
        tb.Entry(self, textvariable=self.var_apellido).grid(row=2, column=1, sticky=EW, padx=5, pady=5)

        tb.Label(self, text="Fecha de nacimiento (YYYY-MM-DD)").grid(row=3, column=0, sticky=W, padx=5, pady=5)
        tb.Entry(self, textvariable=self.var_fecha_nac).grid(row=3, column=1, sticky=EW, padx=5, pady=5)

        tb.Label(self, textvariable=self.var_edad).grid(row=4, column=1, sticky=W, padx=5)

        btn_guardar = tb.Button(self, text="Guardar Cliente", bootstyle="success", command=self.guardar)
        btn_guardar.grid(row=5, column=0, padx=5, pady=10)

        btn_buscar = tb.Button(self, text="Buscar por DNI", bootstyle="info", command=self.buscar)
        btn_buscar.grid(row=5, column=1, padx=5, pady=10)

        self.columnconfigure(1, weight=1)

    def guardar(self):
        dni = self.var_dni.get().strip()
        nombre = self.var_nombre.get().strip()
        apellido = self.var_apellido.get().strip()
        fecha_nac = self.var_fecha_nac.get().strip()

        if not dni or not nombre or not fecha_nac:
            messagebox.showwarning("Campos obligatorios", "Debe completar DNI, nombre y fecha de nacimiento.")
            return

        try:
            edad = self.calcular_edad(fecha_nac)
            self.var_edad.set(f"Edad: {edad} años")

            guardar_cliente(dni, nombre, apellido, fecha_nac)
            messagebox.showinfo("Cliente guardado", f"Cliente {apellido}, {nombre} guardado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")

    def buscar(self):
        dni = self.var_dni.get().strip()
        if not dni:
            messagebox.showwarning("DNI requerido", "Ingrese un DNI para buscar.")
            return
        cliente = buscar_cliente_por_dni(dni)
        if cliente:
            self.var_nombre.set(cliente['nombre'])
            self.var_apellido.set(cliente['apellido'])
            self.var_fecha_nac.set(cliente['fecha_nacimiento'])
            self.var_edad.set(f"Edad: {self.calcular_edad(cliente['fecha_nacimiento'])} años")
        else:
            messagebox.showinfo("No encontrado", "No se encontró ningún cliente con ese DNI.")
            self.var_nombre.set("")
            self.var_apellido.set("")
            self.var_fecha_nac.set("")
            self.var_edad.set("")

    def calcular_edad(self, fecha_nac_str):
        try:
            fecha_nac = datetime.strptime(fecha_nac_str, "%Y-%m-%d").date()
            hoy = date.today()
            edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            return edad
        except:
            return "?"

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

        # --- Input básico
        tb.Label(self, text="DNI del paciente").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        tb.Entry(self, textvariable=self.var_dni).grid(row=0, column=1, sticky=EW, padx=5)

        tb.Label(self, text="Protocolo").grid(row=1, column=2, sticky=W, padx=5, pady=5)
        tb.Entry(self, textvariable=self.var_protocolo).grid(row=1, column=3, sticky=EW, padx=5)

        tb.Label(self, text="Doctor/a").grid(row=2, column=2, sticky=W, padx=5, pady=5)
        tb.Entry(self, textvariable=self.var_doctor).grid(row=2, column=3, sticky=EW, padx=5)

        tb.Label(self, text="Fecha de extracción (YYYY-MM-DD)").grid(row=3, column=2, sticky=W, padx=5, pady=5)
        tb.Entry(self, textvariable=self.var_fecha_extraccion).grid(row=3, column=3, sticky=EW, padx=5)

        tb.Label(self, text="Código de análisis").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        entry_codigo = tb.Entry(self, textvariable=self.var_codigo)
        entry_codigo.grid(row=1, column=1, sticky=EW, padx=5)
        entry_codigo.bind("<FocusOut>", self.verificar_codigo)

        tb.Label(self, text="Valor").grid(row=2, column=0, sticky=W, padx=5, pady=5)
        tb.Entry(self, textvariable=self.var_valor).grid(row=2, column=1, sticky=EW, padx=5)

        self.lbl_desc = tb.Label(self, textvariable=self.var_descripcion, foreground="blue")
        self.lbl_desc.grid(row=3, column=0, columnspan=2, sticky=W, padx=5)

        tb.Button(self, text="Agregar a la lista", bootstyle="primary", command=self.agregar_analisis).grid(row=4, column=0, columnspan=2, pady=10)

        # --- Tabla
        self.tree = tb.Treeview(self, columns=("Código", "Descripción", "Valor", "Referencia"), show="headings", height=10)
        self.menu_ctx = tb.Menu(self, tearoff=0)
        self.menu_ctx.add_command(label="Eliminar análisis", command=self.eliminar_analisis)

        self.tree.bind("<Button-3>", self.mostrar_menu_contextual)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="w", stretch=True)
        self.tree.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=5)

        # --- Botón imprimir
        tb.Button(self, text="Imprimir informe", bootstyle="success", command=self.imprimir_informe).grid(row=6, column=0, columnspan=2, pady=10)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(5, weight=1)



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
                self.analisis_info[codigo] = {
                    "descripcion": modal.resultado["descripcion"],
                    "valores_referencia": modal.resultado["valores_referencia"]
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

        desc = self.analisis_info.get(codigo, {}).get("descripcion", "Sin descripción")
        ref = self.analisis_info.get(codigo, {}).get("valores_referencia", "-")

        # Si tiene subanálisis, mostrar modal
        if codigo in self.subanalisis_info:
            subanals = self.subanalisis_info[codigo]
            modal = VentanaSubanalisis(self, codigo, subanals)
            self.wait_window(modal)

            if modal.resultado:
                for sub, val in zip(subanals, modal.resultado):
                    self.lista_analisis.append({
                        'codigo': codigo,
                        'descripcion': sub['nombre'],
                        'valor': val,
                        'referencia': sub['valores_referencia']
                    })
                    self.tree.insert("", "end", values=(codigo, sub['nombre'], val, sub['valores_referencia']))
        else:
            if not valor:
                messagebox.showwarning("Dato requerido", "Debe ingresar el valor del análisis.")
                return

            self.lista_analisis.append({
                'codigo': codigo,
                'descripcion': desc,
                'valor': valor,
                'referencia': ref
            })
            self.tree.insert("", "end", values=(codigo, desc, valor, ref))

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
            self.lista_analisis = [a for a in self.lista_analisis if not (
                a['codigo'] == valores[0] and a['descripcion'] == valores[1] and str(a['valor']) == valores[2]
            )]
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
        else:
            desc = self.analisis_info[codigo]["descripcion"]
            self.var_descripcion.set(f"→ {desc}")