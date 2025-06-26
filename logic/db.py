# logic/db.py
import sqlite3
import os

DB_PATH = os.path.join("data", "db", "analisis.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        dni TEXT PRIMARY KEY,
        nombre TEXT,
        apellido TEXT,
        fecha_nacimiento TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS informes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dni_cliente TEXT,
        codigo_analisis TEXT,
        nombre_analisis TEXT,
        valor TEXT,
        fecha TEXT,
        FOREIGN KEY(dni_cliente) REFERENCES clientes(dni)
    )
    """)

    conn.commit()
    conn.close()

def guardar_cliente(dni, nombre, apellido, fecha_nac):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO clientes (dni, nombre, apellido, fecha_nacimiento)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(dni) DO UPDATE SET
            nombre = excluded.nombre,
            apellido = excluded.apellido,
            fecha_nacimiento = excluded.fecha_nacimiento
    """, (dni, nombre, apellido, fecha_nac))
    conn.commit()
    conn.close()

def buscar_cliente_por_dni(dni):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM clientes WHERE dni = ?", (dni,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'dni': row[0],
            'nombre': row[1],
            'apellido': row[2],
            'fecha_nacimiento': row[3]
        }
    return None
