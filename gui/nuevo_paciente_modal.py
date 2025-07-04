import ttkbootstrap as tb
from tkinter import Toplevel, StringVar, messagebox
from datetime import datetime, date
from logic.db import guardar_cliente

class VentanaNuevoPaciente(Toplevel):
    def __init__(self, parent, dni_inicial=""):
        super().__init__(parent)
        self.title("Nuevo Paciente")
        self.transient(parent)
        self.grab_set()
        self.resultado = None

        self.var_dni = StringVar(value=dni_inicial)
        self.var_nombre = StringVar()
        self.var_apellido = StringVar()
        self.var_fecha_nac = StringVar()
        self.var_edad = StringVar()

        tb.Label(self, text="DNI").pack()
        tb.Entry(self, textvariable=self.var_dni).pack()

        tb.Label(self, text="Nombre").pack()
        tb.Entry(self, textvariable=self.var_nombre).pack()

        tb.Label(self, text="Apellido").pack()
        tb.Entry(self, textvariable=self.var_apellido).pack()

        tb.Label(self, text="Fecha de nacimiento (YYYY-MM-DD)").pack()
        tb.Entry(self, textvariable=self.var_fecha_nac).pack()

        btn_frame = tb.Frame(self)
        btn_frame.pack(pady=10)

        tb.Button(btn_frame, text="Guardar", bootstyle="success", command=self.guardar).pack(side="left", padx=5)
        tb.Button(btn_frame, text="Cancelar", bootstyle="secondary", command=self.destroy).pack(side="left", padx=5)

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
            guardar_cliente(dni, nombre, apellido, fecha_nac)
            self.resultado = {
                'dni': dni,
                'nombre': nombre,
                'apellido': apellido,
                'fecha_nacimiento': fecha_nac,
                'edad': edad
            }
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")

    def calcular_edad(self, fecha_nac_str):
        fecha_nac = datetime.strptime(fecha_nac_str, "%Y-%m-%d").date()
        hoy = date.today()
        return hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
