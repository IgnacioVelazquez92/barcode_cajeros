# main.py
import tkinter as tk
from tkinter import ttk
from app.ui_form import FormularioCajero
from app.ui_table import TablaCajeros


def main():
    root = tk.Tk()
    root.title("Gestor de Credenciales")
    root.geometry("800x700")  # podés ajustar esto si querés

    # Contenedor de pestañas
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Frame: Tabla de cajeros
    frame_tabla = ttk.Frame(notebook)

    # ⚠️ Vamos a crear primero una tabla "vacía" y luego completar el callback
    tabla_ref = {}  # Referencia temporal para pasar al form más tarde

    def on_select_callback(id, nombre, dni):
        form_ref["obj"].cargar_datos(id, nombre, dni)

    tabla = TablaCajeros(frame_tabla, on_select_callback)
    tabla_ref["obj"] = tabla  # guardamos para usar en callback
    notebook.add(frame_tabla, text="Ver Cajeros")

    # Frame: Formulario de carga
    frame_formulario = ttk.Frame(notebook)
    form = FormularioCajero(
        frame_formulario, actualizar_tabla_callback=tabla.actualizar_tabla)
    form_ref = {"obj": form}  # Para usar en callback cruzado
    notebook.add(frame_formulario, text="Agregar Cajero")

    root.mainloop()


if __name__ == "__main__":
    main()
