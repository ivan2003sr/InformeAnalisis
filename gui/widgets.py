import ttkbootstrap as tb
import os
from ttkbootstrap.constants import *
from tkinter import StringVar
from tkinter import messagebox
from datetime import datetime, date
from gui.subanalisis_modal import VentanaSubanalisis
from logic.db import buscar_cliente_por_dni
from logic.analisis import cargar_analisis_csv, cargar_subanalisis_csv
from tkinter import BooleanVar

class AnalisisFrame(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.analisis_info = cargar_analisis_csv()
        self.subanalisis_info = cargar_subanalisis_csv()
        # Ahora lista_analisis almacenará diccionarios con un 'iid' para referencia con el Treeview
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
        self.entry_codigo.bind("<FocusOut>", self.verificar_codigo) # Se activa al salir del campo

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

        # Treeview tabla - Mantenemos todas las columnas para una vista detallada interna
        # pero para el "padre" de subanálisis, solo mostraremos código y descripción principal.
        self.tree = tb.Treeview(self, columns=("codigo", "descripcion", "valor", "referencia"), show="headings", height=10)
        self.tree.heading("codigo", text="Código", anchor="w")
        self.tree.heading("descripcion", text="Descripción", anchor="w")
        self.tree.heading("valor", text="Valor", anchor="w")
        self.tree.heading("referencia", text="Referencia", anchor="w")
        self.tree.column("codigo", anchor="w", width=80)
        self.tree.column("descripcion", anchor="w", width=250)
        self.tree.column("valor", anchor="w", width=100)
        self.tree.column("referencia", anchor="w", width=150)
        self.tree.grid(row=6, column=0, columnspan=4, sticky="nsew", padx=5, pady=(0, 10))

        # Menú contextual para eliminar
        self.menu_ctx = tb.Menu(self, tearoff=0)
        self.menu_ctx.add_command(label="Eliminar análisis", command=self.eliminar_analisis)
        self.tree.bind("<Button-3>", self.mostrar_menu_contextual) # Botón derecho del ratón

        self.generar_word = BooleanVar(value=False)
        tb.Checkbutton(self, text="Generar Word", variable=self.generar_word).grid(row=7, column=3, columnspan=2, sticky="w", padx=5)
        
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
                    "tecnica": modal.resultado.get("tecnica", ""),
                    "valores_referencia": modal.resultado["valores_referencia"],
                    "unidades": modal.resultado.get("unidades", "")
                }
                self.var_descripcion.set(f"→ {modal.resultado['descripcion']}")
            else:
                self.var_descripcion.set("Código no reconocido.")
                return 
        else:
            desc = self.analisis_info[codigo]["descripcion"]
            self.var_descripcion.set(f"→ {desc}")

        # Si el código tiene subanálisis, abrir la ventana de subanálisis
        if codigo in self.subanalisis_info:
            subanals = self.subanalisis_info[codigo]
            
            # Preparar valores precargados si ya existen para este código
            valores_precargados = []
            # Necesitamos buscar los valores precargados del "padre"
            # y los subanálisis asociados a ese padre.
            # Identificamos el item "padre" en el treeview para obtener los sub-items asociados.
            padre_iid_existente = None
            for item in self.tree.get_children():
                if self.tree.item(item, 'values')[0] == codigo and self.tree.item(item, 'tags') == ('padre_subanalisis',):
                    padre_iid_existente = item
                    break

            if padre_iid_existente:
                # Si el padre ya existe, sus "hijos" en lista_analisis son los subanálisis
                # Filtramos self.lista_analisis por el código y la propiedad 'es_subanalisis': True
                subanalisis_cargados = [a for a in self.lista_analisis if a['codigo'] == codigo and a.get('es_subanalisis', False)]
                # Mapear los valores a la misma estructura que subanals para precarga
                for sub_def in subanals:
                    encontrado = next((sa for sa in subanalisis_cargados if sa['descripcion'] == sub_def['nombre']), None)
                    valores_precargados.append(encontrado['valor'] if encontrado else "")
            else:
                valores_precargados = [""] * len(subanals)


            modal = VentanaSubanalisis(self, codigo, subanals, valores_precargados)
            self.wait_window(modal)

            if modal.resultado:
                # Si el padre ya existe en el Treeview, lo eliminamos para reinsertarlo
                if padre_iid_existente:
                    self.tree.delete(padre_iid_existente)
                    # No es necesario eliminar de lista_analisis aquí, ya que se hará al reinsertar los hijos.

                # Eliminar todos los subanálisis existentes de este código de lista_analisis
                self.lista_analisis = [a for a in self.lista_analisis if not (a['codigo'] == codigo and a.get('es_subanalisis', False))]
                
                # Insertar el "padre" en el Treeview
                desc_padre = self.analisis_info[codigo]["descripcion"]
                # Usa un tag para identificar este como un "padre" de subanálisis
                iid_padre = self.tree.insert("", "end", values=(codigo, desc_padre, "[Ver subanálisis]", ""), tags=('padre_subanalisis',))

                # Agregar cada subanálisis a self.lista_analisis (no al Treeview directamente)
                for i, val in enumerate(modal.resultado):
                    if not val.strip():
                        continue
                    sub = subanals[i]
                    analisis_item = {
                        'codigo': codigo,
                        'descripcion': sub['nombre'],
                        'valor': val,
                        'referencia': sub['valores_referencia'],
                        'tecnica': self.analisis_info[codigo].get("tecnica", ""),
                        'unidades': self.analisis_info[codigo].get("unidades", ""),
                        'es_subanalisis': True, # Marca para identificar que es un subanálisis
                        'padre_iid': iid_padre # Referencia al padre en el Treeview
                    }
                    self.lista_analisis.append(analisis_item)
            
            # Limpiar campos después de procesar el subanálisis
            self.var_codigo.set("")
            self.var_valor.set("") 
            self.var_descripcion.set("")
            self.entry_codigo.focus_set()


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

        # Si tiene subanálisis, ya se manejó en verificar_codigo,
        # así que aquí no se debería poder agregar directamente.
        if codigo in self.subanalisis_info:
            messagebox.showinfo("Información", "Este código es un análisis principal con sub-análisis. Por favor, asegúrese de que el foco esté en el campo 'Código' y presione TAB o haga clic fuera para abrir el asistente de sub-análisis.")
            self.entry_codigo.focus_set()
            return

        # Para análisis sin subanálisis (simple)
        if not valor:
            messagebox.showwarning("Dato requerido", "Debe ingresar el valor del análisis.")
            return
        
        # Antes de agregar, si ya existe un análisis simple con este código, lo reemplazamos
        # Se elimina la entrada anterior para este código (si existe y no es parte de un subanálisis ya agrupado).
        self._eliminar_analisis_simple_por_codigo(codigo)

        analisis_item = {
            'codigo': codigo,
            'descripcion': desc,
            'tecnica': tecnica,
            'valor': valor,
            'referencia': ref,
            'unidades': unidades,
            'valores_referencia': ref 
        }
        # Inserta en el Treeview y guarda el iid
        iid = self.tree.insert("", "end", values=(codigo, desc, valor, ref))
        analisis_item['iid'] = iid # Asigna el iid al diccionario de análisis
        self.lista_analisis.append(analisis_item)

        self.var_codigo.set("")
        self.var_valor.set("")
        self.var_descripcion.set("")
        self.entry_codigo.focus_set() 


    def imprimir_informe(self):
        from logic.informes import generar_pdf_informe
        dni = self.var_dni.get().strip()
        protocolo = self.var_protocolo.get().strip()
        doctor = self.var_doctor.get().strip()
        fecha_extraccion = self.var_fecha_extraccion.get().strip() or datetime.today().strftime('%Y-%m-%d')

        if not dni:
            messagebox.showwarning("Datos faltantes", "Debe ingresar un DNI válido.")
            return
        
        if not self.lista_analisis:
            messagebox.showwarning("Datos faltantes", "Debe agregar al menos un análisis.")
            return

        paciente = buscar_cliente_por_dni(dni)
        if not paciente:
            messagebox.showerror("Paciente no encontrado", "El DNI ingresado no está registrado.")
            return

        paciente['edad'] = self.calcular_edad(paciente['fecha_nacimiento'])
        archivo_pdf = generar_pdf_informe(
            paciente=paciente,
            lista_analisis=self.lista_analisis,
            protocolo=protocolo,
            doctor=doctor,
            fecha_extraccion=fecha_extraccion
        )

        # Limpiar la interfaz después de imprimir
        self.lista_analisis.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.var_dni.set("")
        self.var_nombre_apellido.set("")
        self.var_protocolo.set("")
        self.var_doctor.set("")
        self.var_fecha_extraccion.set("")
        self.var_codigo.set("")
        self.var_valor.set("")
        self.var_descripcion.set("")
        self.entry_dni.focus_set() 

        if self.generar_word.get():
            try:
                from pdf2docx import Converter
                docx_path = archivo_pdf.replace('.pdf', '.docx')
                cv = Converter(archivo_pdf)
                cv.convert(docx_path, start=0, end=None)
                cv.close()
                messagebox.showinfo("Conversión Word", f"Archivo Word generado en: {os.path.basename(docx_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo generar el Word: {e}")

    def calcular_edad(self, fecha_nac_str):
        try:
            fecha_nac = datetime.strptime(fecha_nac_str, "%Y-%m-%d").date()
            hoy = date.today()
            edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            return edad
        except:
            return "?"
        
    def mostrar_menu_contextual(self, event):
        selected_iid = self.tree.identify_row(event.y)
        if selected_iid:
            self.tree.selection_set(selected_iid) 
            self.menu_ctx.post(event.x_root, event.y_root)

    def eliminar_analisis(self):
        selected_iids = self.tree.selection() 
        if not selected_iids:
            return
        
        confirm = messagebox.askyesno("Confirmar eliminación", "¿Está seguro de que desea eliminar el/los análisis seleccionado(s)?")
        if not confirm:
            return

        # Para cada iid seleccionado en el Treeview
        for iid_to_delete in selected_iids:
            # Obtener los valores del elemento seleccionado
            item_values = self.tree.item(iid_to_delete, 'values')
            codigo_seleccionado = item_values[0]
            
            # Verificar si es un "padre_subanalisis"
            item_tags = self.tree.item(iid_to_delete, 'tags')
            if 'padre_subanalisis' in item_tags:
                # Si es un padre, eliminar todos los subanálisis asociados a ese código
                self.lista_analisis = [
                    a for a in self.lista_analisis 
                    if not (a['codigo'] == codigo_seleccionado and a.get('es_subanalisis', False))
                ]
                self.tree.delete(iid_to_delete) # Eliminar solo el padre del Treeview
            else:
                # Si es un análisis simple (no un padre de subanálisis), eliminarlo por su iid
                self.lista_analisis = [
                    a for a in self.lista_analisis 
                    if a.get('iid') != iid_to_delete
                ]
                self.tree.delete(iid_to_delete)


        messagebox.showinfo("Eliminación", "Análisis(s) eliminado(s) correctamente.")

    # Se elimina la función _eliminar_analisis_por_codigo ya que la lógica ahora está en eliminar_analisis y _eliminar_analisis_simple_por_codigo

    def _eliminar_analisis_simple_por_codigo(self, codigo_a_eliminar):
        """
        Elimina un análisis simple (no subanálisis ni padre de subanálisis) 
        asociado a un código específico. Se usa para reemplazarlo si ya existe.
        """
        iids_to_delete = []
        new_lista_analisis = []

        for analisis_item in self.lista_analisis:
            # Un análisis simple es aquel cuyo código coincide Y NO es_subanalisis
            # y cuyo código NO es un padre de subanálisis (porque el padre no se elimina así)
            if analisis_item['codigo'] == codigo_a_eliminar and not analisis_item.get('es_subanalisis', False):
                # Además, verificamos que no sea la entrada "padre" en el Treeview
                # (aunque la lógica del 'padre_iid' debería evitar esto)
                # La mejor forma es que no tenga el tag 'padre_subanalisis' en el Treeview.
                # Sin embargo, esta función solo se llama para reemplazar, no para eliminar "padres".
                
                # Buscamos el iid correspondiente en el Treeview para eliminarlo
                # Esta búsqueda es necesaria porque un análisis simple puede haber sido reinsertado
                # con un nuevo iid si se reemplazó antes.
                found_in_tree = False
                for item_tree_iid in self.tree.get_children():
                    tree_values = self.tree.item(item_tree_iid, 'values')
                    if tree_values[0] == analisis_item['codigo'] and tree_values[1] == analisis_item['descripcion']:
                        iids_to_delete.append(item_tree_iid)
                        found_in_tree = True
                        break # Asumimos que solo hay un item simple por código
                
                # Si no se encontró en el treeview, es porque fue eliminado previamente
                # o es un item "huérfano" que no se mostró.
            else:
                new_lista_analisis.append(analisis_item)
        
        self.lista_analisis = new_lista_analisis
        
        for iid in set(iids_to_delete): # Usar set para evitar duplicados si la misma lógica marca el mismo iid
            if self.tree.exists(iid):
                self.tree.delete(iid)
                
    def verificar_dni(self, event=None):
        dni = self.var_dni.get().strip()
        if not dni:
            self.var_nombre_apellido.set("") 
            self.paciente_data = None
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