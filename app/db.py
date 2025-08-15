# app/db.py

import sqlite3
from datetime import datetime
import os
from app.paths import base_dir, ensure_dirs

BASE_DIR = base_dir()                    # carpeta estable para datos
DB_PATH = os.path.join(BASE_DIR, "data", "credenciales.db")
ensure_dirs("data")                      # crea /data si no existe


def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def crear_tabla():
    """Crea el esquema desde cero (proyecto nuevo)."""
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cajeros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,           -- nombre completo
                dni TEXT NOT NULL UNIQUE,       -- DNI único
                clave TEXT NOT NULL,
                fecha_creacion TEXT NOT NULL,
                legajo TEXT,                    -- opcional
                nombre_sistema TEXT,            -- opcional (nombre solutia)
                sucursal TEXT                   -- opcional
            )
        """)
        conn.commit()


def insertar_cajero(
    nombre_completo: str,
    dni: str,
    clave: str,
    legajo: str | None = None,
    nombre_sistema: str | None = None,
    sucursal: str | None = None,
    fecha_creacion: str | None = None,
):
    fecha = fecha_creacion or datetime.now().strftime("%Y-%m-%d")
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cajeros (nombre, dni, clave, fecha_creacion, legajo, nombre_sistema, sucursal)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nombre_completo, dni, clave, fecha, legajo, nombre_sistema, sucursal))
        conn.commit()


def obtener_todos():
    with conectar() as conn:
        cursor = conn.cursor()
        # Orden y columnas para la UI:
        # id | legajo | nombre | nombre_sistema | dni | clave | fecha_creacion | sucursal
        cursor.execute("""
            SELECT id, legajo, nombre, nombre_sistema, dni, clave, fecha_creacion, sucursal
            FROM cajeros
            ORDER BY id DESC
        """)
        return cursor.fetchall()


def buscar_por_nombre(texto: str):
    with conectar() as conn:
        cursor = conn.cursor()
        like = f"%{(texto or '').upper()}%"
        cursor.execute("""
            SELECT id, legajo, nombre, nombre_sistema, dni, clave, fecha_creacion, sucursal
            FROM cajeros
            WHERE UPPER(nombre) LIKE ?
               OR UPPER(COALESCE(legajo, '')) LIKE ?
               OR UPPER(COALESCE(nombre_sistema, '')) LIKE ?
               OR UPPER(COALESCE(sucursal, '')) LIKE ?
               OR dni LIKE ?
            ORDER BY id DESC
        """, (like, like, like, like, like))
        return cursor.fetchall()


def eliminar_cajero(id_cajero):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cajeros WHERE id = ?", (id_cajero,))
        conn.commit()


def actualizar_cajero(
    id_cajero: int,
    nombre_completo: str,
    dni: str,
    clave: str,
    legajo: str | None = None,
    nombre_sistema: str | None = None,
    sucursal: str | None = None,
    fecha_creacion: str | None = None,
):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE cajeros
            SET nombre = ?, dni = ?, clave = ?,
                legajo = COALESCE(?, legajo),
                nombre_sistema = COALESCE(?, nombre_sistema),
                sucursal = COALESCE(?, sucursal),
                fecha_creacion = COALESCE(?, fecha_creacion)
            WHERE id = ?
        """, (nombre_completo, dni, clave, legajo, nombre_sistema, sucursal, fecha_creacion, id_cajero))
        conn.commit()


def obtener_por_id(id_cajero):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, legajo, nombre, nombre_sistema, dni, clave, fecha_creacion, sucursal
            FROM cajeros
            WHERE id = ?
        """, (id_cajero,))
        return cursor.fetchone()


def existe_dni(dni: str) -> bool:
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM cajeros WHERE dni = ? LIMIT 1", (dni,))
        return cursor.fetchone() is not None


# Crear esquema al importar
crear_tabla()
