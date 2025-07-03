import ttkbootstrap as tb
from tkinter import Toplevel, StringVar, messagebox


class VentanaSubanalisis(Toplevel):
    def __init__(self, parent, codigo, lista_subanalisis, valores_precargados=None):
        super().__init__(parent)
        self.title(f"Subanálisis - Código {codigo}")
        self.transient(parent)
        self.grab_set()

        self.vars = []     # lista de StringVars
        self.entries = []  # lista de widgets Entry
        self.resultado = None

        tb.Label(self, text="Complete los valores de cada ítem:").pack(pady=10)

        frame = tb.Frame(self)
        frame.pack(padx=10, pady=5)

        max_rows = 12  # Máximo de filas por columna

        for i, sub in enumerate(lista_subanalisis):
            valor_inicial = sub.get("valor_por_defecto", "")
            if valores_precargados and i < len(valores_precargados):
                if valores_precargados[i].strip():
                    valor_inicial = valores_precargados[i]

            var = StringVar(value=valor_inicial)
            self.vars.append(var)

            col = i // max_rows
            row = i % max_rows

            tb.Label(frame, text=sub["nombre"]).grid(row=row, column=col * 2, sticky="w", padx=5, pady=2)
            entry = tb.Entry(frame, textvariable=var)
            entry.grid(row=row, column=col * 2 + 1, padx=5, pady=2)

            self.entries.append(entry)

        # Navegación con Tab entre los campos visibles
        for i, entry in enumerate(self.entries):
            entry.bind("<Tab>", self._crear_tab_handler(i))

        # Foco inicial
        if self.entries:
            self.entries[0].focus_set()

        # Atajos Enter / Escape
        self.bind("<Return>", lambda event: self.confirmar())
        self.bind("<Escape>", lambda event: self.destroy())

        # Botones
        btn_frame = tb.Frame(self)
        btn_frame.pack(pady=10)
        tb.Button(btn_frame, text="Aceptar", command=self.confirmar, bootstyle="success").grid(row=0, column=0, padx=10)
        tb.Button(btn_frame, text="Cancelar", command=self.destroy, bootstyle="secondary").grid(row=0, column=1, padx=10)

    def _crear_tab_handler(self, i):
        def handler(event):
            next_idx = (i + 1) % len(self.entries)
            self.entries[next_idx].focus_set()
            return "break"
        return handler

    def confirmar(self):
        valores = [var.get().strip() for var in self.vars]

        if self.title().endswith("711"):
            self.resultado = valores  # permite campos vacíos
            self.destroy()
        elif any(not val for val in valores):
            messagebox.showwarning("Campos vacíos", "Debe completar todos los valores.")
            return
        else:
            self.resultado = valores
            self.destroy()
