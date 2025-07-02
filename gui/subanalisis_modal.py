import ttkbootstrap as tb
from tkinter import Toplevel, StringVar, messagebox


class VentanaSubanalisis(Toplevel):
    def __init__(self, parent, codigo, lista_subanalisis, valores_precargados=None):
        super().__init__(parent)
        self.title(f"Subanálisis - Código {codigo}")
        self.transient(parent)
        self.grab_set()

        self.vars = []  # lista de StringVars por subanálisis
        self.resultado = None

        tb.Label(self, text="Complete los valores de cada ítem:").pack(pady=10)

        frame = tb.Frame(self)
        frame.pack(padx=10, pady=5)

        for i, sub in enumerate(lista_subanalisis):
            valor_inicial = sub.get("valor_por_defecto", "")
            if valores_precargados and i < len(valores_precargados):
                if valores_precargados[i].strip():  # si no está vacío
                    valor_inicial = valores_precargados[i]
            var = StringVar(value=valor_inicial)
            self.vars.append(var)
            tb.Label(frame, text=sub["nombre"]).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            tb.Entry(frame, textvariable=var).grid(row=i, column=1, padx=5, pady=2)


        btn_frame = tb.Frame(self)
        btn_frame.pack(pady=10)
        tb.Button(btn_frame, text="Aceptar", command=self.confirmar, bootstyle="success").grid(row=0, column=0, padx=10)
        tb.Button(btn_frame, text="Cancelar", command=self.destroy, bootstyle="secondary").grid(row=0, column=1, padx=10)

    def confirmar(self):
        valores = [var.get().strip() for var in self.vars]
        if any(not val for val in valores):
            messagebox.showwarning("Campos vacíos", "Debe completar todos los valores.")
            return
        self.resultado = valores
        self.destroy()
