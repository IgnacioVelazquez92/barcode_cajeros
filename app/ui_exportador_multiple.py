# app/ui_exportador_multiple.py
import tkinter as tk
from tkinter import ttk, messagebox
from app import controller, pdf_generator

CHECKED = "\u2611"   # ☑
UNCHECKED = "\u2610"  # ☐


class ExportadorMultiple:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Exportar múltiples credenciales")
        self.top.geometry("750x520")
        self.top.grab_set()  # Bloquea la ventana principal hasta cerrar

        self.seleccionados = set()
        self.todos_cajeros = []

        self._construir_ui()
        self._cargar_cajeros()

    def _construir_ui(self):
        # --- Barra de búsqueda ---
        frame_busqueda = tk.Frame(self.top)
        frame_busqueda.pack(fill="x", padx=10, pady=(10, 5))

        tk.Label(frame_busqueda, text="Buscar por nombre o DNI:").pack(
            side="left")
        self.entry_buscar = tk.Entry(frame_busqueda, width=35)
        self.entry_buscar.pack(side="left", padx=6)

        btn_buscar = tk.Button(
            frame_busqueda, text="Buscar", command=self._buscar)
        btn_buscar.pack(side="left")

        btn_ver_todos = tk.Button(
            frame_busqueda, text="Ver todos", command=self._cargar_cajeros)
        btn_ver_todos.pack(side="left", padx=6)

        # --- Contador de seleccionados ---
        self.lbl_contador = tk.Label(frame_busqueda, text="Seleccionados: 0")
        self.lbl_contador.pack(side="right")

        # --- Tabla con columna de selección ---
        columnas = ("Sel", "ID", "Nombre", "DNI")
        self.tree = ttk.Treeview(
            self.top,
            columns=columnas,
            show="headings",
            selectmode="none",
            height=16
        )

        self.tree.heading("Sel", text="Sel")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("DNI", text="DNI")

        self.tree.column("Sel", width=50, anchor="center")
        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Nombre", width=380, anchor="w")
        self.tree.column("DNI", width=160, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Click: toggle sólo si se hace clic en la columna Sel o en la fila
        self.tree.bind("<Button-1>", self._on_click)

        # --- Pie: Exportar ---
        frame_acciones = tk.Frame(self.top)
        frame_acciones.pack(fill="x", padx=10, pady=(0, 10))

        self.btn_exportar = tk.Button(
            frame_acciones, text="Exportar seleccionados", command=self._exportar)
        self.btn_exportar.pack(side="right")

    # ----------------- Datos / Búsqueda -----------------
    def _cargar_cajeros(self):
        self.todos_cajeros = controller.obtener_cajeros()
        # Orden del más nuevo al más viejo (id DESC)
        self.todos_cajeros.sort(key=lambda x: x[0], reverse=True)
        self._actualizar_tabla(self.todos_cajeros)

    def _buscar(self):
        texto = self.entry_buscar.get().strip()
        if texto:
            resultados = controller.buscar_cajeros(texto)
            resultados.sort(key=lambda x: x[0], reverse=True)
            self._actualizar_tabla(resultados)

    def _actualizar_tabla(self, datos):
        self.tree.delete(*self.tree.get_children())
        for cajero in datos:
            id_ = cajero[0]
            nombre = cajero[2]
            dni = cajero[4]
            marcado = CHECKED if id_ in self.seleccionados else UNCHECKED
            self.tree.insert("", tk.END, iid=id_,
                             values=(marcado, id_, nombre, dni))
        self._actualizar_contador()
    # ----------------- Interacción UI -----------------

    def _on_click(self, event):
        # Identificar fila y columna clickeada
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)  # e.g. '#1' para 'Sel'
        if not row_id:
            return

        # Permitir toggle al clickear la fila completa; si querés, limitá a col_id == '#1'
        self._toggle(row_id)

    def _toggle(self, item_id_str):
        try:
            item_id = int(item_id_str)
        except ValueError:
            # Por si iid no es numérico (no debería)
            item_vals = self.tree.item(item_id_str, "values")
            if not item_vals:
                return
            item_id = int(item_vals[1])  # posición 1 es ID

        if item_id in self.seleccionados:
            self.seleccionados.remove(item_id)
        else:
            self.seleccionados.add(item_id)

        # Redibuja sólo ese item para mayor eficiencia
        vals = self.tree.item(item_id_str, "values")
        if vals:
            marcado = CHECKED if item_id in self.seleccionados else UNCHECKED
            nuevos = (marcado,) + tuple(vals[1:])
            self.tree.item(item_id_str, values=nuevos)

        self._actualizar_contador()

    def _actualizar_contador(self):
        self.lbl_contador.config(
            text=f"Seleccionados: {len(self.seleccionados)}")

    # ----------------- Exportación -----------------
    def _exportar(self):
        if not self.seleccionados:
            messagebox.showwarning(
                "Sin selección", "Seleccioná al menos un cajero para exportar.")
            return

        ids = list(self.seleccionados)
        if pdf_generator.generar_pdf_multiples(ids):
            messagebox.showinfo("Exportación completa",
                                "PDF generado correctamente en carpeta /pdfs.")
            self.top.destroy()
        else:
            messagebox.showerror("Error", "No se pudo generar el PDF.")
