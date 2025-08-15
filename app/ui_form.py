# app/ui_form.py
import tkinter as tk
from tkinter import messagebox
from app import controller
from app.utils import hoy_str


class FormularioCajero:
    def __init__(self, parent, actualizar_tabla_callback=None):
        self.parent = parent
        self.actualizar_tabla = actualizar_tabla_callback
        self._construir_ui()

    def _construir_ui(self):
        self.frame = tk.Frame(self.parent)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Layout
        self.frame.grid_columnconfigure(0, weight=0)
        self.frame.grid_columnconfigure(1, weight=1)

        # Requeridos
        tk.Label(self.frame, text="Nombre completo:*").grid(
            row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_nombre = tk.Entry(self.frame, width=40)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5, sticky="we")

        tk.Label(self.frame, text="DNI:*").grid(
            row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_dni = tk.Entry(self.frame, width=40)
        self.entry_dni.grid(row=1, column=1, padx=5, pady=5, sticky="we")

        # Opcionales
        tk.Label(self.frame, text="Nombre solutia:").grid(
            row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_solutia = tk.Entry(self.frame, width=40)
        self.entry_solutia.grid(row=2, column=1, padx=5, pady=5, sticky="we")

        tk.Label(self.frame, text="Legajo:").grid(
            row=3, column=0, padx=5, pady=5, sticky="e")
        self.entry_legajo = tk.Entry(self.frame, width=40)
        self.entry_legajo.grid(row=3, column=1, padx=5, pady=5, sticky="we")

        tk.Label(self.frame, text="Sucursal:").grid(
            row=4, column=0, padx=5, pady=5, sticky="e")
        self.entry_sucursal = tk.Entry(self.frame, width=40)
        self.entry_sucursal.grid(row=4, column=1, padx=5, pady=5, sticky="we")

        tk.Label(self.frame, text="Fecha de alta:").grid(
            row=5, column=0, padx=5, pady=5, sticky="e")
        self.entry_fecha = tk.Entry(self.frame, width=40)
        self.entry_fecha.grid(row=5, column=1, padx=5, pady=5, sticky="we")
        self.entry_fecha.insert(0, hoy_str())  # por defecto hoy

        # Botones
        cont_botones = tk.Frame(self.frame)
        cont_botones.grid(row=6, column=0, columnspan=2, pady=12, sticky="e")

        self.btn_agregar = tk.Button(
            cont_botones, text="Agregar cajero", command=self._agregar, bg="green", fg="white")
        self.btn_agregar.pack(side="right", padx=(6, 0))

        self.btn_cancelar = tk.Button(
            cont_botones, text="Cancelar", command=self._limpiar)
        self.btn_cancelar.pack(side="right")

        # Atajos
        for w in (self.entry_nombre, self.entry_dni, self.entry_solutia, self.entry_legajo, self.entry_sucursal, self.entry_fecha):
            w.bind("<Return>", self._agregar_event)
        self.frame.bind_all("<Escape>", self._cancelar_event)

        self.entry_nombre.focus_set()

    # Acciones
    def _agregar_event(self, _evt=None):
        self._agregar()

    def _cancelar_event(self, _evt=None):
        self._limpiar()

    def _agregar(self):
        nombre = self.entry_nombre.get().strip()
        dni = self.entry_dni.get().strip()
        nombre_sistema = self.entry_solutia.get().strip()
        legajo = self.entry_legajo.get().strip()
        sucursal = self.entry_sucursal.get().strip()
        fecha = self.entry_fecha.get().strip()

        ok = controller.crear_cajero(
            nombre_completo=nombre,
            dni=dni,
            legajo=legajo or None,
            nombre_sistema=nombre_sistema or None,
            sucursal=sucursal or None,
            fecha_creacion=fecha or None,
        )
        if ok:
            messagebox.showinfo(
                "Éxito", f"Cajero '{nombre.upper()}' agregado.")
            self._limpiar()
            if self.actualizar_tabla:
                self.actualizar_tabla()

    def _limpiar(self):
        for e in (self.entry_nombre, self.entry_dni, self.entry_solutia, self.entry_legajo, self.entry_sucursal, self.entry_fecha):
            e.delete(0, tk.END)
        self.entry_fecha.insert(0, hoy_str())
        self.entry_nombre.focus_set()
