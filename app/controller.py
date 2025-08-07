# app/controller.py
from app import db
from app import pdf_generator
from app.utils import generar_clave
from tkinter import messagebox


def crear_cajero(nombre: str, dni: str) -> bool:
    if not nombre or not dni.isdigit():
        messagebox.showerror("Error", "Nombre y DNI válidos requeridos.")
        return False

    nombre = nombre.strip().upper()
    clave = generar_clave(dni)

    try:
        db.insertar_cajero(nombre, dni, clave)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el cajero: {e}")
        return False


def editar_cajero(id_cajero: int, nombre: str, dni: str) -> bool:
    if not nombre or not dni.isdigit():
        messagebox.showerror("Error", "Nombre y DNI válidos requeridos.")
        return False

    nombre = nombre.strip().upper()
    clave = generar_clave(dni)

    try:
        db.actualizar_cajero(id_cajero, nombre, dni, clave)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar el cajero: {e}")
        return False


def eliminar_cajero(id_cajero: int) -> bool:
    try:
        db.eliminar_cajero(id_cajero)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo eliminar: {e}")
        return False


def buscar_cajeros(nombre: str):
    return db.buscar_por_nombre(nombre)


def obtener_cajeros():
    return db.obtener_todos()


def reimprimir_pdf(id_cajero: int) -> bool:
    cajero = db.obtener_por_id(id_cajero)
    if not cajero:
        messagebox.showerror("Error", "Cajero no encontrado.")
        return False

    nombre, clave = cajero[1], cajero[3]
    try:
        pdf_generator.generar_pdf(nombre, clave)
        messagebox.showinfo(
            "Reimpresión", f"PDF de {nombre} generado correctamente.")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el PDF: {e}")
        return False
