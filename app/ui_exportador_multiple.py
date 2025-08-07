import tkinter as tk
from tkinter import ttk, messagebox
from app import controller, pdf_generator


class ExportadorMultiple:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Exportar múltiples credenciales")
        self.top.geometry("700x500")
        self.top.grab_set()  # Bloquea ventana principal hasta cerrar

        self.seleccionados = set()
        self.todos_cajeros = []

        self._construir_ui()
        self._cargar_cajeros()

    def _construir_ui(self):
        frame_busqueda = tk.Frame(self.top)
        frame_busqueda.pack(fill="x", padx=10, pady=(10, 5))

        tk.Label(frame_busqueda, text="Buscar por nombre o DNI:").pack(
            side="left")

        self.entry_buscar = tk.Entry(frame_busqueda, width=30)
        self.entry_buscar.pack(side="left", padx=5)

        btn_buscar = tk.Button(
            frame_busqueda, text="Buscar", command=self._buscar)
        btn_buscar.pack(side="left")

        btn_ver_todos = tk.Button(
            frame_busqueda, text="Ver todos", command=self._cargar_cajeros)
        btn_ver_todos.pack(side="left", padx=5)

        self.tree = ttk.Treeview(self.top, columns=(
            "ID", "Nombre", "DNI"), show="headings", selectmode="none")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("DNI", text="DNI")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Nombre", width=300, anchor="w")
        self.tree.column("DNI", width=150, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Button-1>", self._toggle_check)

        self.btn_exportar = tk.Button(
            self.top, text="Exportar seleccionados", command=self._exportar)
        self.btn_exportar.pack(pady=10)

    def _cargar_cajeros(self):
        self.todos_cajeros = controller.obtener_cajeros()
        # Ordenar del más nuevo al más viejo
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
            id_, nombre, dni = cajero[0], cajero[1], cajero[2]
            checked = "\u2611" if id_ in self.seleccionados else "\u2610"
            self.tree.insert("", tk.END, iid=id_, values=(
                id_, nombre, dni), tags=("check",))

    def _toggle_check(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            item_id = int(self.tree.item(item, "values")[0])
            if item_id in self.seleccionados:
                self.seleccionados.remove(item_id)
            else:
                self.seleccionados.add(item_id)
            self._actualizar_tabla(self.todos_cajeros)

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
