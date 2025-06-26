import ttkbootstrap as tb
from tkinter import Toplevel, StringVar, messagebox


class AgregarCodigoModal(Toplevel):
    def __init__(self, parent, codigo):
        super().__init__(parent)
        self.title(f"Agregar código {codigo}")
        self.codigo = codigo
        self.transient(parent)
        self.grab_set()
        self.resultado = None

        self.var_desc = StringVar()
        self.var_ref = StringVar()

        tb.Label(self, text=f"Código {codigo} no registrado.").pack(pady=5)
        tb.Label(self, text="Descripción").pack()
        tb.Entry(self, textvariable=self.var_desc).pack(padx=10, pady=5, fill="x")
        tb.Label(self, text="Valores de referencia").pack()
        tb.Entry(self, textvariable=self.var_ref).pack(padx=10, pady=5, fill="x")

        btns = tb.Frame(self)
        btns.pack(pady=10)
        tb.Button(btns, text="Guardar", bootstyle="success", command=self.guardar).grid(row=0, column=0, padx=10)
        tb.Button(btns, text="Cancelar", bootstyle="secondary", command=self.destroy).grid(row=0, column=1, padx=10)

    def guardar(self):
        desc = self.var_desc.get().strip()
        ref = self.var_ref.get().strip()
        if not desc or not ref:
            messagebox.showwarning("Campos requeridos", "Debe completar ambos campos.")
            return
        self.resultado = {
            'codigo': self.codigo,
            'descripcion': desc,
            'valores_referencia': ref
        }
        self.destroy()
