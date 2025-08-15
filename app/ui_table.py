# app/ui_table.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app import controller
from app.ui_exportador_multiple import ExportadorMultiple


class TablaCajeros:
    def __init__(self, parent, on_select_callback=lambda *args, **kwargs: None):
        self.parent = parent
        self.on_select_callback = on_select_callback
        # Dataset: (id, legajo, nombre, nombre_sistema, dni, clave, fecha, sucursal)
        self.cajero_seleccionado = None
        self.current_rows = []
        self.sort_state = {"col": None, "reverse": False}

        self._construir_interfaz()
        self.actualizar_tabla()

    def _construir_interfaz(self):
        # 🔍 Búsqueda
        self.frame_busqueda = tk.Frame(self.parent)
        self.frame_busqueda.pack(fill="x", padx=10, pady=(10, 0))

        tk.Label(self.frame_busqueda,
                 text="Buscar :").pack(side="left", padx=(0, 5))
        self.entry_busqueda = tk.Entry(self.frame_busqueda, width=30)
        self.entry_busqueda.pack(side="left", padx=(0, 5))

        tk.Button(self.frame_busqueda, text="Buscar",
                  command=self.buscar).pack(side="left", padx=(0, 5))
        tk.Button(self.frame_busqueda, text="Ver todos",
                  command=self.actualizar_tabla).pack(side="left", padx=(0, 15))

        tk.Button(self.frame_busqueda, text="Backup Excel",
                  command=self._backup_excel).pack(side="right")
        tk.Button(self.frame_busqueda, text="Exportar varios",
                  command=self._abrir_modal_exportador).pack(side="right", padx=(0, 8))

        tk.Button(self.frame_busqueda, text="📂PDFs",
                  command=self._abrir_carpeta_pdfs).pack(side="right", padx=(0, 8))

        # 📋 Tabla
        self.columnas = ("ID", "Legajo", "Nombre completo",
                         "Nombre solutia", "DNI", "Clave", "Fecha creación", "Sucursal")
        self.tree = ttk.Treeview(
            self.parent,
            columns=self.columnas,
            show="headings",
            selectmode="browse",
            height=20
        )
        for col in self.columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        # Encabezados clickeables
        self.tree.heading("ID", command=lambda: self._ordenar_por("ID"))
        self.tree.heading("Nombre completo",
                          command=lambda: self._ordenar_por("Nombre completo"))
        self.tree.heading("Fecha creación",
                          command=lambda: self._ordenar_por("Fecha creación"))

        self.tree.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        self.tree.bind("<<TreeviewSelect>>", self._fila_seleccionada)
        self.tree.bind("<Double-1>", self._doble_click_editar)

        # Menú contextual
        self.menu = tk.Menu(self.parent, tearoff=0)
        self.menu.add_command(
            label="Copiar Nombre + Clave (TAB)", command=self._copiar_nombre_clave)
        self.menu.add_command(label="Copiar Clave", command=self._copiar_clave)
        self.menu.add_command(label="Copiar Nombre",
                              command=self._copiar_nombre)
        self.menu.add_command(label="Copiar DNI", command=self._copiar_dni)
        self.menu.add_separator()
        self.menu.add_command(label="Editar…", command=self._editar)
        self.menu.add_command(label="Cambiar clave…",
                              command=self._abrir_modal_cambiar_clave)
        self.menu.add_command(label="Eliminar", command=self._eliminar)
        self.tree.bind("<Button-3>", self._abrir_menu_contextual)

        # ⚙️ Botones
        self.frame_acciones = tk.Frame(self.parent)
        self.frame_acciones.pack(fill="x", padx=10, pady=(0, 10))

        self.btn_editar = tk.Button(
            self.frame_acciones, text="🖊️ Editar", command=self._editar, state="disabled")
        self.btn_editar.pack(side="left", padx=5)

        self.btn_cambiar_clave = tk.Button(
            self.frame_acciones, text="🔑 Cambiar clave", command=self._abrir_modal_cambiar_clave, state="disabled")
        self.btn_cambiar_clave.pack(side="left", padx=5)

        self.btn_eliminar = tk.Button(
            self.frame_acciones, text="🗑️ Eliminar", command=self._eliminar, state="disabled")
        self.btn_eliminar.pack(side="left", padx=5)

        self.btn_exportar_pdf = tk.Button(
            self.frame_acciones, text="📄 Exportar PDF", command=self._exportar_pdf, state="disabled")
        self.btn_exportar_pdf.pack(side="left", padx=5)

        self.btn_copiar_nc = tk.Button(
            self.frame_acciones, text="📋 Copiar Nombre + Clave", command=self._copiar_nombre_clave, state="disabled")
        self.btn_copiar_nc.pack(side="right", padx=5)
        self.btn_copiar_clave = tk.Button(
            self.frame_acciones, text="📋 Copiar Clave", command=self._copiar_clave, state="disabled")
        self.btn_copiar_clave.pack(side="right", padx=5)

    # ====== Ordenamiento ======
    def _ordenar_por(self, columna_nombre: str):
        if not self.current_rows:
            return

        if columna_nombre == "ID":
            def key_fn(r): return int(r[0])
        elif columna_nombre == "Nombre completo":
            def key_fn(r): return (r[2] or "").upper()
        elif columna_nombre == "Fecha creación":
            def key_fn(r):
                try:
                    return datetime.strptime(r[6], "%Y-%m-%d")
                except Exception:
                    return datetime.min
        else:
            return

        if self.sort_state["col"] == columna_nombre:
            self.sort_state["reverse"] = not self.sort_state["reverse"]
        else:
            self.sort_state["col"] = columna_nombre
            self.sort_state["reverse"] = False

        ordenada = sorted(self.current_rows, key=key_fn,
                          reverse=self.sort_state["reverse"])
        self._pintar_tabla(ordenada)
        self._actualizar_encabezados(
            columna_nombre, self.sort_state["reverse"])

    def _actualizar_encabezados(self, activa: str, reverse: bool):
        for col in self.columnas:
            self.tree.heading(col, text=col)
        if activa in self.columnas:
            flecha = " ▼" if reverse else " ▲"
            self.tree.heading(activa, text=activa + flecha)

        self.tree.heading("ID", command=lambda: self._ordenar_por("ID"))
        self.tree.heading("Nombre completo",
                          command=lambda: self._ordenar_por("Nombre completo"))
        self.tree.heading("Fecha creación",
                          command=lambda: self._ordenar_por("Fecha creación"))

    # ====== Eventos de tabla ======
    def _fila_seleccionada(self, _event):
        seleccionado = self.tree.focus()
        if seleccionado:
            valores = self.tree.item(seleccionado, "values")
            # (id, legajo, nombre, nombre_sistema, dni, clave, fecha, sucursal)
            try:
                id_cajero = int(valores[0])
            except (TypeError, ValueError):
                return
            self.cajero_seleccionado = tuple(valores)
            self._habilitar_botones()
        else:
            self.cajero_seleccionado = None
            self._deshabilitar_botones()

    def _doble_click_editar(self, _event):
        if self.cajero_seleccionado:
            self._editar()

    def _abrir_menu_contextual(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.tree.focus(row_id)
            self._fila_seleccionada(None)
            self.menu.tk_popup(event.x_root, event.y_root)

    # ====== Acciones ======
    def _editar(self):
        if not self.cajero_seleccionado:
            return
        # Desempaquetar por claridad
        id_cajero = int(self.cajero_seleccionado[0])
        legajo = self.cajero_seleccionado[1] or ""
        nombre = self.cajero_seleccionado[2]
        nombre_sistema = self.cajero_seleccionado[3] or ""
        dni = self.cajero_seleccionado[4]
        sucursal = self.cajero_seleccionado[7] or ""
        self._abrir_modal_edicion(
            id_cajero, legajo, nombre, nombre_sistema, dni, sucursal)

    def _abrir_modal_cambiar_clave(self):
        if not self.cajero_seleccionado:
            return
        id_cajero, nombre = int(
            self.cajero_seleccionado[0]), self.cajero_seleccionado[2]
        top = tk.Toplevel(self.parent)
        top.title(f"Cambiar clave: {nombre}")
        top.geometry("420x180")
        top.transient(self.parent)
        top.grab_set()

        tk.Label(top, text="Nueva clave (texto tal cual):").grid(
            row=0, column=0, padx=8, pady=8, sticky="e")
        entry_clave = tk.Entry(top, width=35)
        entry_clave.grid(row=0, column=1, padx=8, pady=8)

        var_ofuscar = tk.BooleanVar(value=True)
        tk.Checkbutton(top, text="Ofuscar (recomendado)", variable=var_ofuscar).grid(
            row=1, column=1, sticky="w", padx=8)

        cont = tk.Frame(top)
        cont.grid(row=2, column=0, columnspan=2, pady=10, sticky="e")

        def guardar():
            nueva = entry_clave.get().strip()
            if not nueva:
                messagebox.showerror("Error", "Ingresá una clave.")
                return
            if controller.actualizar_clave_personalizada(int(self.cajero_seleccionado[0]), nueva, ofuscar=var_ofuscar.get()):
                self.actualizar_tabla()
                top.destroy()

        tk.Button(cont, text="Guardar", command=guardar, bg="blue",
                  fg="white").pack(side="right", padx=(6, 0))
        tk.Button(cont, text="Cancelar",
                  command=top.destroy).pack(side="right")

        entry_clave.bind("<Return>", lambda _e: guardar())
        top.bind("<Escape>", lambda _e: top.destroy())
        entry_clave.focus_set()

    def _eliminar(self):
        if self.cajero_seleccionado:
            id_cajero = int(self.cajero_seleccionado[0])
            if messagebox.askyesno("Eliminar", "¿Estás seguro que deseas eliminar este cajero?"):
                if controller.eliminar_cajero(id_cajero):
                    self.actualizar_tabla()

    def _exportar_pdf(self):
        if self.cajero_seleccionado:
            id_cajero = int(self.cajero_seleccionado[0])
            controller.reimprimir_pdf(id_cajero)

    # ====== Copiar ======
    def _copiar_al_clipboard(self, texto: str):
        try:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(texto)
            self.parent.update_idletasks()
        except Exception:
            pass

    def _copiar_nombre_clave(self):
        if not self.cajero_seleccionado:
            return
        # Dataset: (id, legajo, nombre, nombre_sistema, dni, clave, fecha, sucursal)
        nombre_solutia = (self.cajero_seleccionado[3] or "").strip()
        nombre = nombre_solutia if nombre_solutia else self.cajero_seleccionado[2]
        clave = self.cajero_seleccionado[5]
        self._copiar_al_clipboard(f"{nombre}\t{clave}")

    def _copiar_clave(self):
        if not self.cajero_seleccionado:
            return
        self._copiar_al_clipboard(self.cajero_seleccionado[5])

    def _copiar_nombre(self):
        if not self.cajero_seleccionado:
            return
        self._copiar_al_clipboard(self.cajero_seleccionado[2])

    def _copiar_dni(self):
        if not self.cajero_seleccionado:
            return
        self._copiar_al_clipboard(self.cajero_seleccionado[4])

    # ====== Buscar / Actualizar ======
    def actualizar_tabla(self):
        self.entry_busqueda.delete(0, tk.END)
        self._cargar_datos(controller.obtener_cajeros())
        self._deshabilitar_botones()
        self.sort_state = {"col": None, "reverse": False}
        self._actualizar_encabezados("", False)

    def buscar(self):
        filtro = self.entry_busqueda.get().strip()
        if filtro:
            resultados = controller.buscar_cajeros(filtro)
            self._cargar_datos(resultados)
            self._deshabilitar_botones()
            self.sort_state = {"col": None, "reverse": False}
            self._actualizar_encabezados("", False)

    def _cargar_datos(self, datos):
        self.current_rows = list(datos)
        self._pintar_tabla(self.current_rows)

    def _pintar_tabla(self, filas):
        self.tree.delete(*self.tree.get_children())
        for cajero in filas:
            self.tree.insert("", tk.END, values=cajero)

    # ====== Util ======
    def _abrir_modal_exportador(self):
        ExportadorMultiple(self.parent)

    def _backup_excel(self):
        controller.exportar_excel()

    def _habilitar_botones(self):
        self.btn_editar["state"] = "normal"
        self.btn_cambiar_clave["state"] = "normal"
        self.btn_eliminar["state"] = "normal"
        self.btn_exportar_pdf["state"] = "normal"
        self.btn_copiar_nc["state"] = "normal"
        self.btn_copiar_clave["state"] = "normal"

    def _deshabilitar_botones(self):
        self.btn_editar["state"] = "disabled"
        self.btn_cambiar_clave["state"] = "disabled"
        self.btn_eliminar["state"] = "disabled"
        self.btn_exportar_pdf["state"] = "disabled"
        self.btn_copiar_nc["state"] = "disabled"
        self.btn_copiar_clave["state"] = "disabled"

    # ====== Modal de edición: incluye Legajo / Solutia / Sucursal / Fecha ======
    def _abrir_modal_edicion(self, id_cajero: int, legajo: str, nombre: str, nombre_sistema: str, dni: str, sucursal: str):
        # OJO: la fecha está en índice 6 del dataset
        fecha_actual = ""
        if self.cajero_seleccionado and len(self.cajero_seleccionado) >= 7:
            fecha_actual = self.cajero_seleccionado[6] or ""

        top = tk.Toplevel(self.parent)
        top.title(f"Editar cajero #{id_cajero}")
        top.geometry("540x320")
        top.transient(self.parent)
        top.grab_set()

        tk.Label(top, text="Legajo:").grid(
            row=0, column=0, padx=8, pady=6, sticky="e")
        entry_legajo = tk.Entry(top, width=46)
        entry_legajo.grid(row=0, column=1, padx=8, pady=6)
        entry_legajo.insert(0, legajo)

        tk.Label(top, text="Nombre completo:*").grid(
            row=1, column=0, padx=8, pady=6, sticky="e")
        entry_nombre = tk.Entry(top, width=46)
        entry_nombre.grid(row=1, column=1, padx=8, pady=6)
        entry_nombre.insert(0, nombre)

        tk.Label(top, text="Nombre solutia:*").grid(
            row=2, column=0, padx=8, pady=6, sticky="e")
        entry_solutia = tk.Entry(top, width=46)
        entry_solutia.grid(row=2, column=1, padx=8, pady=6)
        entry_solutia.insert(0, nombre_sistema)

        tk.Label(top, text="DNI:*").grid(
            row=3, column=0, padx=8, pady=6, sticky="e")
        entry_dni = tk.Entry(top, width=46)
        entry_dni.grid(row=3, column=1, padx=8, pady=6)
        entry_dni.insert(0, dni)

        tk.Label(top, text="Sucursal:").grid(
            row=4, column=0, padx=8, pady=6, sticky="e")
        entry_sucursal = tk.Entry(top, width=46)
        entry_sucursal.grid(row=4, column=1, padx=8, pady=6)
        entry_sucursal.insert(0, sucursal)

        tk.Label(top, text="Fecha alta:*").grid(
            row=5, column=0, padx=8, pady=6, sticky="e")
        entry_fecha = tk.Entry(top, width=46)
        entry_fecha.grid(row=5, column=1, padx=8, pady=6)
        entry_fecha.insert(0, fecha_actual)

        cont = tk.Frame(top)
        cont.grid(row=6, column=0, columnspan=2, pady=10, sticky="e")

        def guardar():
            nuevo_legajo = entry_legajo.get().strip() or None
            nuevo_nombre = entry_nombre.get().strip()
            nuevo_solutia = entry_solutia.get().strip() or None
            nuevo_dni = entry_dni.get().strip()
            nueva_sucursal = entry_sucursal.get().strip() or None
            nueva_fecha = entry_fecha.get().strip() or None
            if not nuevo_nombre or not nuevo_dni.isdigit():
                messagebox.showerror(
                    "Error", "Nombre y DNI válidos requeridos.")
                return
            if controller.editar_cajero(
                id_cajero,
                nuevo_nombre,
                nuevo_dni,
                nuevo_legajo,
                nuevo_solutia,
                nueva_sucursal,
                nueva_fecha,
            ):
                self.actualizar_tabla()
                top.destroy()

        tk.Button(cont, text="Guardar cambios", command=guardar,
                  bg="blue", fg="white").pack(side="right", padx=(6, 0))
        tk.Button(cont, text="Cancelar",
                  command=top.destroy).pack(side="right")

        entry_legajo.bind("<Return>", lambda _e: guardar())
        entry_nombre.bind("<Return>", lambda _e: guardar())
        entry_solutia.bind("<Return>", lambda _e: guardar())
        entry_dni.bind("<Return>", lambda _e: guardar())
        entry_sucursal.bind("<Return>", lambda _e: guardar())
        entry_fecha.bind("<Return>", lambda _e: guardar())
        top.bind("<Escape>", lambda _e: top.destroy())
        entry_nombre.focus_set()

    def _abrir_carpeta_pdfs(self):
        controller.abrir_carpeta_pdfs()
