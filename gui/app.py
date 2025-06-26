import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import StringVar
from logic.db import init_db
from gui.widgets import ClienteFrame, AnalisisFrame

def run_app():
    init_db()  # crea las tablas si no existen

    app = tb.Window(themename="flatly")
    app.title("Sistema de Informes de Análisis")
    app.geometry("800x600")

    notebook = tb.Notebook(app, bootstyle="primary")
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Pestaña de clientes
    frame_clientes = ClienteFrame(notebook)
    notebook.add(frame_clientes, text="Clientes")

    # Pestaña de análisis
    frame_analisis = AnalisisFrame(notebook)
    notebook.add(frame_analisis, text="Análisis")

    app.mainloop()
