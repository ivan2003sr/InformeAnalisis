import ttkbootstrap as tb
from tkinter import Toplevel, StringVar, messagebox
from tkinter.ttk import Frame

class AgregarCodigoModal(Toplevel):
    def __init__(self, parent, codigo):
        super().__init__(parent)
        self.title(f"Agregar código {codigo}")
        self.resizable(False, False)
        
        # Configuración de la ventana modal
        self.codigo = codigo
        self.transient(parent)
        self.grab_set()
        self.resultado = None
        
        # Variables de control
        self.var_desc = StringVar()
        self.var_tecnica = StringVar()
        self.var_ref = StringVar()
        self.var_unidades = StringVar()
        
        # Contenedor principal con padding
        main_frame = Frame(self)
        main_frame.pack(padx=15, pady=15, fill="both", expand=True)
        
        # Título y código
        tb.Label(main_frame, 
                text=f"Registro de nuevo análisis - Código: {codigo}",
                bootstyle="primary",
                font=('Helvetica', 10, 'bold')).pack(pady=(0, 15))
        
        # Formulario
        form_frame = Frame(main_frame)
        form_frame.pack(fill="x", pady=5)
        
        # Campo Descripción (obligatorio)
        tb.Label(form_frame, text="Descripción *", bootstyle="danger").pack(anchor="w")
        tb.Entry(form_frame, textvariable=self.var_desc).pack(fill="x", pady=(0, 10))
        
        # Campo Técnica (opcional)
        tb.Label(form_frame, text="Técnica").pack(anchor="w")
        tb.Entry(form_frame, textvariable=self.var_tecnica).pack(fill="x", pady=(0, 10))
        
        # Campo Valores de referencia (opcional)
        tb.Label(form_frame, text="Valores de referencia").pack(anchor="w")
        tb.Entry(form_frame, textvariable=self.var_ref).pack(fill="x", pady=(0, 10))
        
        # Campo Unidades (opcional)
        tb.Label(form_frame, text="Unidades").pack(anchor="w")
        tb.Entry(form_frame, textvariable=self.var_unidades).pack(fill="x", pady=(0, 15))
        
        # Nota sobre campos obligatorios
        tb.Label(main_frame, 
                text="* Campos obligatorios",
                bootstyle="danger",
                font=('Helvetica', 8)).pack(anchor="w", pady=(0, 10))
        
        # Botones
        btn_frame = Frame(main_frame)
        btn_frame.pack(fill="x")
        
        tb.Button(
            btn_frame, 
            text="Cancelar", 
            bootstyle="secondary", 
            command=self.destroy
        ).pack(side="right", padx=5)
        
        tb.Button(
            btn_frame, 
            text="Guardar", 
            bootstyle="success", 
            command=self.guardar
        ).pack(side="right")

    def guardar(self):
        """Valida y guarda los datos ingresados en formato CSV"""
        desc = self.var_desc.get().strip()
        tecnica = self.var_tecnica.get().strip()
        ref = self.var_ref.get().strip()
        unidades = self.var_unidades.get().strip()
        
        # Validación de campos obligatorios
        if not desc:
            messagebox.showwarning(
                "Campo requerido", 
                "La descripción es obligatoria",
                parent=self
            )
            return
            
        # Estructura de datos para CSV
        self.resultado = {
            'codigo': self.codigo,
            'descripcion': desc,
            'tecnica': tecnica if tecnica else "",
            'valores_referencia': ref if ref else "",
            'unidades': unidades if unidades else ""
        }
        
        self.destroy()