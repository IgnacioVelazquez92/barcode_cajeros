import tkinter as tk
from tkinter import ttk, messagebox
from app import controller
from app.ui_exportador_multiple import ExportadorMultiple


class TablaCajeros:
    def __init__(self, parent, on_select_callback):
        self.parent = parent
        self.on_select_callback = on_select_callback
        self.cajero_seleccionado = None  # (id, nombre, dni)

        self._construir_interfaz()
        self.actualizar_tabla()

    def _construir_interfaz(self):
        # 🔍 Frame de búsqueda
        self.frame_busqueda = tk.Frame(self.parent)
        self.frame_busqueda.pack(fill="x", padx=10, pady=(10, 0))

        tk.Label(self.frame_busqueda, text="Buscar por nombre o DNI:").pack(
            side="left", padx=(0, 5))
        self.entry_busqueda = tk.Entry(self.frame_busqueda, width=30)
        self.entry_busqueda.pack(side="left", padx=(0, 5))

        btn_buscar = tk.Button(self.frame_busqueda,
                               text="Buscar", command=self.buscar)
        btn_buscar.pack(side="left", padx=(0, 5))

        btn_ver_todos = tk.Button(
            self.frame_busqueda, text="Ver todos", command=self.actualizar_tabla)
        btn_ver_todos.pack(side="left", padx=(0, 15))

        # 📤 Botón Exportar múltiples
        btn_exportar_varios = tk.Button(
            self.frame_busqueda, text="Exportar varios", command=self._abrir_modal_exportador)
        btn_exportar_varios.pack(side="right")

        # 📋 Tabla
        columnas = ("ID", "Nombre", "DNI", "Clave", "Fecha creación")
        self.tree = ttk.Treeview(
            self.parent,
            columns=columnas,
            show="headings",
            selectmode="browse",
            height=20
        )

        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        self.tree.bind("<<TreeviewSelect>>", self._fila_seleccionada)

        # ⚙️ Botones CRUD debajo de la tabla
        self.frame_acciones = tk.Frame(self.parent)
        self.frame_acciones.pack(fill="x", padx=10, pady=(0, 10))

        self.btn_editar = tk.Button(
            self.frame_acciones, text="🖊️ Editar", command=self._editar, state="disabled")
        self.btn_editar.pack(side="left", padx=5)

        self.btn_eliminar = tk.Button(
            self.frame_acciones, text="🗑️ Eliminar", command=self._eliminar, state="disabled")
        self.btn_eliminar.pack(side="left", padx=5)

        self.btn_exportar_pdf = tk.Button(
            self.frame_acciones, text="📄 Exportar PDF", command=self._exportar_pdf, state="disabled")
        self.btn_exportar_pdf.pack(side="left", padx=5)

    def _fila_seleccionada(self, event):
        seleccionado = self.tree.focus()
        if seleccionado:
            valores = self.tree.item(seleccionado, "values")
            id_cajero = int(valores[0])
            nombre = valores[1]
            dni = valores[2]
            self.cajero_seleccionado = (id_cajero, nombre, dni)
            self.on_select_callback(id_cajero, nombre, dni)
            self._habilitar_botones()
        else:
            self.cajero_seleccionado = None
            self._deshabilitar_botones()

    def _habilitar_botones(self):
        self.btn_editar["state"] = "normal"
        self.btn_eliminar["state"] = "normal"
        self.btn_exportar_pdf["state"] = "normal"

    def _deshabilitar_botones(self):
        self.btn_editar["state"] = "disabled"
        self.btn_eliminar["state"] = "disabled"
        self.btn_exportar_pdf["state"] = "disabled"

    def actualizar_tabla(self):
        self.entry_busqueda.delete(0, tk.END)
        self._cargar_datos(controller.obtener_cajeros())
        self._deshabilitar_botones()

    def buscar(self):
        filtro = self.entry_busqueda.get().strip()
        if filtro:
            resultados = controller.buscar_cajeros(filtro)
            self._cargar_datos(resultados)
            self._deshabilitar_botones()

    def _cargar_datos(self, datos):
        self.tree.delete(*self.tree.get_children())
        for cajero in datos:
            self.tree.insert("", tk.END, values=cajero)

    def obtener_seleccionados(self):
        """Devuelve lista de IDs seleccionados para exportar múltiples"""
        seleccionados = []
        for item in self.tree.selection():
            valores = self.tree.item(item, "values")
            seleccionados.append(int(valores[0]))
        return seleccionados

    def _abrir_modal_exportador(self):
        ExportadorMultiple(self.parent)

    def _editar(self):
        if self.cajero_seleccionado:
            id_cajero, nombre, dni = self.cajero_seleccionado
            self.on_select_callback(id_cajero, nombre, dni)

    def _eliminar(self):
        if self.cajero_seleccionado:
            id_cajero, *_ = self.cajero_seleccionado
            if messagebox.askyesno("Eliminar", "¿Estás seguro que deseas eliminar este cajero?"):
                if controller.eliminar_cajero(id_cajero):
                    self.actualizar_tabla()

    def _exportar_pdf(self):
        if self.cajero_seleccionado:
            id_cajero, *_ = self.cajero_seleccionado
            controller.reimprimir_pdf(id_cajero)
