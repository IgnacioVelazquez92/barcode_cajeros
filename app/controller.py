# app/controller.py
import subprocess
import sys
from tkinter import messagebox
from app import db
from app import pdf_generator
from app.utils import generar_clave, ofuscar_clave, normalizar_fecha
import os
from datetime import datetime
import sqlite3


def crear_cajero(
    nombre_completo: str,
    dni: str,
    legajo: str | None = None,
    nombre_sistema: str | None = None,
    sucursal: str | None = None,
    fecha_creacion: str | None = None,
) -> bool:
    """
    Alta con campos opcionales (legajo, nombre_sistema, sucursal, fecha_creacion).
    DNI debe ser único. La fecha se normaliza a YYYY-MM-DD (acepta DD/MM/YYYY).
    """
    if not nombre_completo or not dni or not dni.isdigit():
        messagebox.showerror(
            "Error", "Nombre completo y DNI numérico son requeridos.")
        return False

    nombre_completo = nombre_completo.strip().upper()
    legajo = legajo.strip().upper() if legajo else None
    nombre_sistema = nombre_sistema.strip().upper() if nombre_sistema else None
    sucursal = sucursal.strip().upper() if sucursal else None

    # Fecha
    try:
        fecha_norm = normalizar_fecha(fecha_creacion)
    except ValueError as ve:
        messagebox.showerror("Fecha inválida", str(ve))
        return False

    if db.existe_dni(dni):
        messagebox.showerror("Error", f"Ya existe un cajero con el DNI {dni}.")
        return False

    clave_base = generar_clave(dni)
    clave_guardar = ofuscar_clave(clave_base)

    try:
        db.insertar_cajero(
            nombre_completo, dni, clave_guardar,
            legajo=legajo, nombre_sistema=nombre_sistema, sucursal=sucursal,
            fecha_creacion=fecha_norm
        )
        return True
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", f"Ya existe un cajero con el DNI {dni}.")
        return False
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el cajero: {e}")
        return False


def editar_cajero(
    id_cajero: int,
    nombre_completo: str,
    dni: str,
    legajo: str | None = None,
    nombre_sistema: str | None = None,
    sucursal: str | None = None,
    fecha_creacion: str | None = None,
) -> bool:
    """
    Edición completa, incluyendo fecha de creación.
    """
    if not nombre_completo or not dni.isdigit():
        messagebox.showerror(
            "Error", "Nombre completo y DNI válidos requeridos.")
        return False

    nombre_completo = nombre_completo.strip().upper()
    legajo = legajo.strip().upper() if legajo else None
    nombre_sistema = nombre_sistema.strip().upper() if nombre_sistema else None
    sucursal = sucursal.strip().upper() if sucursal else None

    try:
        fecha_norm = normalizar_fecha(
            fecha_creacion) if fecha_creacion is not None else None
    except ValueError as ve:
        messagebox.showerror("Fecha inválida", str(ve))
        return False

    clave_base = generar_clave(dni)
    clave_guardar = ofuscar_clave(clave_base)

    try:
        db.actualizar_cajero(
            id_cajero, nombre_completo, dni, clave_guardar,
            legajo=legajo, nombre_sistema=nombre_sistema, sucursal=sucursal,
            fecha_creacion=fecha_norm
        )
        return True
    except sqlite3.IntegrityError:
        messagebox.showerror(
            "Error", f"El DNI {dni} ya existe asignado a otro cajero.")
        return False
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar el cajero: {e}")
        return False


def actualizar_clave_personalizada(id_cajero: int, clave_plana: str, ofuscar: bool = True) -> bool:
    """
    Actualiza exclusivamente la clave del cajero.
    - Si ofuscar=True: aplica ofuscar_clave(clave_plana)
    - Si ofuscar=False: guarda tal cual (p.ej. 'pepe')
    Conserva legajo, nombre_sistema, sucursal y fecha_creacion sin cambios.
    """
    cajero = db.obtener_por_id(id_cajero)
    if not cajero:
        messagebox.showerror("Error", "Cajero no encontrado.")
        return False

    # Dataset: (id, legajo, nombre, nombre_sistema, dni, clave, fecha, sucursal)
    legajo = cajero[1]
    nombre = cajero[2]
    nombre_sistema = cajero[3]
    dni = cajero[4]
    sucursal = cajero[7]

    try:
        clave_a_guardar = ofuscar_clave(
            clave_plana) if ofuscar else clave_plana
        # No tocamos fecha_creacion (pasamos None para que COALESCE la mantenga)
        db.actualizar_cajero(
            id_cajero=id_cajero,
            nombre_completo=nombre,
            dni=dni,
            clave=clave_a_guardar,
            legajo=legajo,
            nombre_sistema=nombre_sistema,
            sucursal=sucursal,
            fecha_creacion=None,
        )
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

    # Dataset: (id, legajo, nombre, nombre_sistema, dni, clave, fecha, sucursal)
    nombre_completo = cajero[2] or ""
    nombre_sistema = cajero[3] or ""
    etiqueta = (nombre_sistema.strip() or nombre_completo.strip())
    clave = cajero[5]

    try:
        pdf_generator.generar_pdf(etiqueta, clave)
        messagebox.showinfo(
            "Reimpresión", f"PDF de {etiqueta} generado correctamente.")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el PDF: {e}")
        return False


def exportar_excel() -> bool:
    """Exporta todos los cajeros a /excel con timestamp, incluyendo legajo, nombre_sistema y sucursal."""
    try:
        from openpyxl import Workbook
    except ImportError:
        messagebox.showerror(
            "Falta dependencia", "Necesitas instalar openpyxl:\n\npip install openpyxl")
        return False

    # (id, legajo, nombre, nombre_sistema, dni, clave, fecha, sucursal)
    registros = db.obtener_todos()
    if not registros:
        messagebox.showinfo("Backup", "No hay registros para exportar.")
        return False

    import os
    from datetime import datetime
    base_dir = os.path.dirname(os.path.dirname(__file__))
    excel_dir = os.path.join(base_dir, "excel")
    os.makedirs(excel_dir, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    ruta = os.path.join(excel_dir, f"backup_{ts}.xlsx")

    wb = Workbook()
    ws = wb.active
    ws.title = "Cajeros"

    ws.append(["ID", "Legajo", "Nombre completo", "Nombre solutia",
              "DNI", "Clave", "Fecha creación", "Sucursal"])

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


def abrir_carpeta(path: str) -> bool:
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{e}")
        return False


def abrir_carpeta_pdfs() -> bool:
    from app.pdf_generator import PDF_DIR
    return abrir_carpeta(PDF_DIR)
