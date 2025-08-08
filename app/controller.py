# app/controller.py
from tkinter import messagebox
from app import db
from app import pdf_generator
from app.utils import generar_clave, ofuscar_clave  # ya existente
import os
from datetime import datetime


def crear_cajero(nombre: str, dni: str) -> bool:
    if not nombre or not dni.isdigit():
        messagebox.showerror("Error", "Nombre y DNI válidos requeridos.")
        return False

    nombre = nombre.strip().upper()
    clave_base = generar_clave(dni)
    clave_guardar = ofuscar_clave(clave_base)

    try:
        db.insertar_cajero(nombre, dni, clave_guardar)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el cajero: {e}")
        return False


def editar_cajero(id_cajero: int, nombre: str, dni: str) -> bool:
    if not nombre or not dni.isdigit():
        messagebox.showerror("Error", "Nombre y DNI válidos requeridos.")
        return False

    nombre = nombre.strip().upper()
    clave_base = generar_clave(dni)
    clave_guardar = ofuscar_clave(clave_base)

    try:
        db.actualizar_cajero(id_cajero, nombre, dni, clave_guardar)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar el cajero: {e}")
        return False


def actualizar_clave_personalizada(id_cajero: int, clave_plana: str, ofuscar: bool = True) -> bool:
    """
    Permite setear una clave específica (a pedido).
    - ofuscar=True: aplica la misma ofuscación que usamos siempre.
    - ofuscar=False: guarda tal cual (útil si la dueña quiere exactamente esa clave).
    """
    cajero = db.obtener_por_id(id_cajero)
    if not cajero:
        messagebox.showerror("Error", "Cajero no encontrado.")
        return False

    _, nombre, dni, _, _ = cajero
    try:
        clave_a_guardar = ofuscar_clave(
            clave_plana) if ofuscar else clave_plana
        db.actualizar_cajero(id_cajero, nombre, dni, clave_a_guardar)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar la clave: {e}")
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


def exportar_excel() -> bool:
    """Exporta todos los cajeros a un archivo Excel en /excel con timestamp."""
    try:
        # Lazy import para no cargar si no se usa
        from openpyxl import Workbook
    except ImportError:
        messagebox.showerror(
            "Falta dependencia",
            "Necesitas instalar openpyxl:\n\npip install openpyxl"
        )
        return False

    registros = db.obtener_todos()  # [(id, nombre, dni, clave, fecha)]
    if not registros:
        messagebox.showinfo("Backup", "No hay registros para exportar.")
        return False

    # Carpeta destino
    base_dir = os.path.dirname(os.path.dirname(__file__))
    excel_dir = os.path.join(base_dir, "excel")
    os.makedirs(excel_dir, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    ruta = os.path.join(excel_dir, f"backup_{ts}.xlsx")

    # Crear workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Cajeros"

    # Encabezados
    ws.append(["ID", "Nombre", "DNI", "Clave", "Fecha creación"])

    # Filas
    for row in registros:
        ws.append(list(row))

    # Auto ancho simple
    for col in ws.columns:
        max_len = 0
        col_letter = col[0].column_letter
        for cell in col:
            val = str(cell.value) if cell.value is not None else ""
            max_len = max(max_len, len(val))
        ws.column_dimensions[col_letter].width = min(max_len + 2, 40)

    try:
        wb.save(ruta)
        messagebox.showinfo("Backup", f"Excel generado:\n{ruta}")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el Excel:\n{e}")
        return False
