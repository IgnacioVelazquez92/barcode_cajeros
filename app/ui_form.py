# app/ui_form.py
import tkinter as tk
from tkinter import messagebox
from app import controller


class FormularioCajero:
    def __init__(self, parent, actualizar_tabla_callback):
        self.parent = parent
        self.actualizar_tabla = actualizar_tabla_callback
        self.id_seleccionado = None

        self._construir_ui()

    def _construir_ui(self):
        self.frame = tk.Frame(self.parent)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        tk.Label(self.frame, text="Nombre completo:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_nombre = tk.Entry(self.frame, width=40)
        self.entry_nombre.grid(row=0, column=1, padx=5)

        tk.Label(self.frame, text="DNI:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_dni = tk.Entry(self.frame, width=40)
        self.entry_dni.grid(row=1, column=1, padx=5)

        # Botones
        self.btn_agregar = tk.Button(
            self.frame, text="Agregar cajero", command=self._agregar, bg="green", fg="white")
        self.btn_agregar.grid(row=2, columnspan=2, pady=10)

        self.btn_actualizar = tk.Button(
            self.frame, text="Actualizar", command=self._actualizar, state="disabled", bg="blue", fg="white")
        self.btn_actualizar.grid(row=3, column=0, pady=5)

        self.btn_eliminar = tk.Button(
            self.frame, text="Eliminar", command=self._eliminar, state="disabled", bg="red", fg="white")
        self.btn_eliminar.grid(row=3, column=1, pady=5)

        self.btn_cancelar = tk.Button(
            self.frame, text="Cancelar", command=self._cancelar, state="disabled")
        self.btn_cancelar.grid(row=4, columnspan=2, pady=5)

    def _agregar(self):
        nombre = self.entry_nombre.get()
        dni = self.entry_dni.get()

        if controller.crear_cajero(nombre, dni):
            messagebox.showinfo(
                "Éxito", f"Cajero '{nombre.upper()}' agregado.")
            self._limpiar()
            if self.actualizar_tabla:
                self.actualizar_tabla()

    def _actualizar(self):
        if self.id_seleccionado is None:
            return

        nombre = self.entry_nombre.get()
        dni = self.entry_dni.get()

        if controller.editar_cajero(self.id_seleccionado, nombre, dni):
            messagebox.showinfo(
                "Actualizado", f"Cajero ID {self.id_seleccionado} actualizado.")
            self._limpiar()
            if self.actualizar_tabla:
                self.actualizar_tabla()

    def _eliminar(self):
        if self.id_seleccionado is None:
            return

        confirmar = messagebox.askyesno(
            "Eliminar", "¿Seguro que desea eliminar este cajero?")
        if confirmar:
            if controller.eliminar_cajero(self.id_seleccionado):
                messagebox.showinfo("Eliminado", "Cajero eliminado.")
                self._limpiar()
                if self.actualizar_tabla:
                    self.actualizar_tabla()

    def _cancelar(self):
        self._limpiar()

    def _limpiar(self):
        self.id_seleccionado = None
        self.entry_nombre.delete(0, tk.END)
        self.entry_dni.delete(0, tk.END)
        self.btn_agregar.config(state="normal")
        self.btn_actualizar.config(state="disabled")
        self.btn_eliminar.config(state="disabled")
        self.btn_cancelar.config(state="disabled")

    def cargar_datos(self, id_cajero, nombre, dni):
        self.id_seleccionado = id_cajero
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, nombre)
        self.entry_dni.delete(0, tk.END)
        self.entry_dni.insert(0, dni)
        self.btn_agregar.config(state="disabled")
        self.btn_actualizar.config(state="normal")
        self.btn_eliminar.config(state="normal")
        self.btn_cancelar.config(state="normal")
