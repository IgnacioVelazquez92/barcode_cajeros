# app/db.py
import sqlite3
from datetime import datetime
import os

# Ruta del archivo de base de datos
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # /credenciales_app/
DB_PATH = os.path.join(BASE_DIR, "data", "credenciales.db")

# Asegura que la carpeta 'data' exista
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)


def conectar():
    return sqlite3.connect(DB_PATH)


def crear_tabla():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cajeros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                dni TEXT NOT NULL,
                clave TEXT NOT NULL,
                fecha_creacion TEXT NOT NULL
            )
        """)
        conn.commit()


def insertar_cajero(nombre, dni, clave):
    fecha = datetime.now().strftime("%Y-%m-%d")
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cajeros (nombre, dni, clave, fecha_creacion)
            VALUES (?, ?, ?, ?)
        """, (nombre, dni, clave, fecha))
        conn.commit()


def obtener_todos():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cajeros ORDER BY id DESC")
        return cursor.fetchall()


def buscar_por_nombre(nombre):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM cajeros
            WHERE nombre LIKE ?
            ORDER BY id DESC
        """, (f"%{nombre.upper()}%",))
        return cursor.fetchall()


def eliminar_cajero(id_cajero):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cajeros WHERE id = ?", (id_cajero,))
        conn.commit()


def actualizar_cajero(id_cajero, nombre, dni, clave):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE cajeros
            SET nombre = ?, dni = ?, clave = ?
            WHERE id = ?
        """, (nombre, dni, clave, id_cajero))
        conn.commit()


def obtener_por_id(id_cajero):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cajeros WHERE id = ?", (id_cajero,))
        return cursor.fetchone()


# Ejecutar al importar para crear la tabla automáticamente
crear_tabla()
