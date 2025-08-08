# app/ui_form.py
import tkinter as tk
from tkinter import messagebox
from app import controller


class FormularioCajero:
    def __init__(self, parent, actualizar_tabla_callback=None):
        self.parent = parent
        self.actualizar_tabla = actualizar_tabla_callback
        self._construir_ui()

    def _construir_ui(self):
        self.frame = tk.Frame(self.parent)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Layout responsive
        self.frame.grid_columnconfigure(0, weight=0)
        self.frame.grid_columnconfigure(1, weight=1)

        tk.Label(self.frame, text="Nombre completo:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_nombre = tk.Entry(self.frame, width=40)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5, sticky="we")

        tk.Label(self.frame, text="DNI:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_dni = tk.Entry(self.frame, width=40)
        self.entry_dni.grid(row=1, column=1, padx=5, pady=5, sticky="we")

        cont_botones = tk.Frame(self.frame)
        cont_botones.grid(row=2, column=0, columnspan=2, pady=12, sticky="e")

        # ÚNICO botón de acción: Agregar
        self.btn_agregar = tk.Button(
            cont_botones, text="Agregar cajero",
            command=self._agregar, bg="green", fg="white"
        )
        self.btn_agregar.pack(side="right", padx=(6, 0))

        # Botón Cancelar: sólo limpia
        self.btn_cancelar = tk.Button(
            cont_botones, text="Cancelar",
            command=self._limpiar
        )
        self.btn_cancelar.pack(side="right")

        # Atajos de teclado
        self.entry_nombre.bind("<Return>", self._agregar_event)
        self.entry_dni.bind("<Return>", self._agregar_event)
        self.frame.bind_all("<Escape>", self._cancelar_event)

        # Focus inicial
        self.entry_nombre.focus_set()

    # ----- Acciones -----
    def _agregar_event(self, _evt=None):
        self._agregar()

    def _cancelar_event(self, _evt=None):
        self._limpiar()

    def _agregar(self):
        nombre = self.entry_nombre.get().strip()
        dni = self.entry_dni.get().strip()

        if controller.crear_cajero(nombre, dni):
            messagebox.showinfo(
                "Éxito", f"Cajero '{nombre.upper()}' agregado.")
            self._limpiar()
            if self.actualizar_tabla:
                self.actualizar_tabla()

    def _limpiar(self):
        self.entry_nombre.delete(0, tk.END)
        self.entry_dni.delete(0, tk.END)
        self.entry_nombre.focus_set()
