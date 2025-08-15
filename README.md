# 🧾 Gestor de Credenciales de Cajeros

Aplicación de escritorio en **Python** (Tkinter + SQLite + ReportLab) para **generar credenciales con código de barras**, administrar cajeros y exportar/importar datos de forma simple. Pensada para funcionar **como .exe portable** en Windows o desde código fuente.

---

## 🚀 Características principales

- **ABM de cajeros** con campos:
  - **ID** (auto)
  - **Legajo** *(opcional)*
  - **Nombre completo** *(requerido)*
  - **Nombre solutia** *(opcional; mostrado en credenciales y al copiar nombre+clave)*
  - **DNI** *(requerido y **único**)*
  - **Clave** (generada a partir de DNI+fecha y ofuscada, editable)
  - **Fecha de creación** *(editable; por defecto hoy; acepta `YYYY-MM-DD` o `DD/MM/YYYY`)*
  - **Sucursal** *(opcional)*
- **Interfaz con pestañas**: “Agregar Cajero” y “Ver Cajeros”.
- **Generación de credenciales PDF**:
  - Individual y Múltiple.
  - Muestra **Nombre solutia** (si no hay, usa Nombre completo).
  - Texto **cercano** al código de barras.
- **Exportación**:
  - **Backup Excel** (o **Plantilla** si no hay datos) con **apertura automática** de carpeta.
  - **Backup PDF de emergencia** si no hay `openpyxl`.
- **Importación desde Excel** con **el mismo formato** que el backup/plantilla.
- **Búsquedas** por nombre, DNI, legajo, solutia o sucursal.
- **Copiado rápido**: “**Copiar Nombre + Clave**” usa **Solutia + Clave** (o Nombre si falta Solutia).
- **Botón**: “**📂 Abrir carpeta PDFs**” abre en 1 clic la carpeta de credenciales.
- **Base local SQLite** en `data/` (portabilidad total).

---

## 🛠 Requisitos

- **Windows 10/11**.
- Para ejecutar desde fuentes: **Python 3.11** + `pip`.
- Dependencias principales:
  - `reportlab==4.4.3`
  - `openpyxl==3.1.5`

> **Nota**: el ejecutable `.exe` generado incluye todo lo necesario (no requiere Python instalado).

---

## 📦 Usar como **ejecutable (.exe)** en Windows

### Opción 1 — Usar el `.bat` de build (recomendado)
1. Asegurá que en la raíz del proyecto existan estos archivos:
   - `build_windows_exe.bat` (script de build)
   - *(opcional)* `icono.ico` (ícono para el .exe y el acceso directo)
2. Doble clic a **`build_windows_exe.bat`**. El script:
   - Crea/activa `.venv`
   - Instala dependencias + **PyInstaller**
   - Aplica **hook** para ReportLab (barcode)
   - Construye **`dist/GestorCredenciales.exe`**
   - Crea un **acceso directo en el Escritorio**
   - Abre la carpeta `dist/`
3. Ejecutá **`dist/GestorCredenciales.exe`**.

> La primera vez se crean, junto al `.exe`, las carpetas: `data/`, `pdfs/`, `excel/`.

### Opción 2 — PyInstaller manual (si preferís)
```bash
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --onefile --windowed --name "GestorCredenciales" main.py
```
> Con ReportLab puede requerir *hidden imports*; el `.bat` ya lo resuelve automáticamente.

---

## ▶️ Ejecutar **desde código fuente** (modo desarrollo)

```bat
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

También podés usar `run_dev.bat` (si está incluido).

---

## 🗂 Estructura del proyecto

```
credenciales_app/
├── app/
│   ├── controller.py
│   ├── db.py
│   ├── pdf_generator.py
│   ├── paths.py
│   ├── ui_form.py
│   ├── ui_table.py
│   ├── ui_exportador_multiple.py
│   └── utils.py
├── main.py
├── data/     (SQLite, se crea en runtime)
├── pdfs/     (PDFs generados)
├── excel/    (backups/plantillas/logs)
├── build_windows_exe.bat   (script de empaquetado)
├── run_dev.bat             (script dev; opcional)
├── requirements.txt
├── README.md
└── .gitignore
```

**Rutas portables**: `app/paths.py` detecta si se ejecuta como `.exe` (PyInstaller) o desde fuentes y dirige todo a las carpetas locales junto al `.exe` o al proyecto.

---

## 🧭 Uso de la aplicación

### Pestaña **Agregar Cajero**
- Completar **Nombre completo** y **DNI** (numérico).
- Opcionales en el alta: **Nombre solutia**, **Legajo**, **Sucursal**, **Fecha de creación**.
- La **Clave** se genera automáticamente (DNI+fecha → ofuscada); luego puede cambiarse manualmente (con o sin ofuscación).

**Atajos**: `Enter` para aceptar; `Esc` para limpiar.

### Pestaña **Ver Cajeros**
- Buscar por **nombre**, **dni**, **legajo**, **solutia** o **sucursal**.
- **Ordenar** por `ID`, `Nombre completo` o `Fecha de creación` haciendo clic en el encabezado.
- **Editar**: abre modal con todos los campos, incluida **Fecha de creación**.
- **Cambiar clave**: ofuscada o **en texto plano** si se decide así.
- **Eliminar**, **Exportar PDF individual**, **Copiar Nombre + Clave** (Solutia + Clave).

### Exportar **varios PDFs**
- Botón “**Exportar varios**” → seleccionar filas → genera `pdfs/credenciales_multiples.pdf`.

### **Abrir carpeta PDFs**
- Botón “**📂 Abrir carpeta PDFs**” abre en el explorador la carpeta `pdfs/`.

---

## 📑 Exportar **Backup Excel** / **Plantilla**

- Botón **“Backup Excel”**:
  - Si hay registros: crea `excel/backup_YYYYMMDD_HHMM.xlsx` con **todos los datos**.
  - Si **no** hay registros: crea **PLANTILLA** con **solo encabezados** (útil para cargar datos y luego **importarlos**).
  - Abre la carpeta **`excel/`** automáticamente.
  - Si falta `openpyxl`, se genera **PDF de respaldo** (encabezados + datos).

**Encabezados del Excel (orden exacto):**  
`ID | Legajo | Nombre completo | Nombre solutia | DNI | Clave | Fecha creación | Sucursal`

- **ID** puede quedar vacío para importar; la app lo genera automáticamente.
- **Clave**: si se deja vacía en el Excel de importación, la app la **genera y ofusca**; si trae valor, se respeta **tal cual**.

---

## 📥 Importar **desde Excel** (mismo formato que el backup)

- Botón **“📥 Importar Excel”** (en “Ver Cajeros”).
- Acepta `.xlsx` con los **mismos encabezados** que genera el backup/plantilla.  
- Reglas:
  - **Nombre completo** y **DNI** obligatorios; **DNI** debe ser numérico y **único**.
  - **Fecha de creación** acepta `YYYY-MM-DD` o `DD/MM/YYYY` (si Excel trae fecha nativa, también se toma).
  - **Clave**: si está vacía → se genera (ofuscada). Si tiene valor → se guarda **sin ofuscar**.
- Resultado:
  - Informe “Insertados” y “Saltados” (duplicados, fechas inválidas, etc.).
  - Se escribe un **log** en `excel/import_log_YYYYMMDD_HHMM.txt`.
  - Se refresca la tabla.

---

## 🧾 Credenciales PDF (diseño)

- **Tamaño** de credencial: `8.3 × 5.3 cm` con bordes redondeados.
- **Código de barras**: `Code128`, alto fijo ~ `3.0 cm`, ancho adaptativo (módulo mínimo 0.25 mm).
- **Texto**: se muestra **Nombre solutia** (o Nombre completo) **justo encima del código de barras** para máxima legibilidad.

---

## 🔐 Reglas clave de datos

- **DNI único** (validación y constraint SQL).
- **Fecha de creación** **editable** (útil al migrar desde Excel).
- **Clave**:
  - Generación: `dni + fecha(DDMM)` → **ofuscación reversible** por desplazamiento y reversa.
  - Desde UI: se puede **forzar texto plano** (ej.: `"pepe"`) si así se desea.

---

## 🧩 Requisitos y `requirements.txt`

Mínimo recomendado:
```
reportlab==4.4.3
openpyxl==3.1.5
```
> Si usás el `pip freeze` original, puede incluir paquetes no esenciales. Para un `.exe` más liviano, mantené solo los necesarios.

---

## 🧰 Scripts incluidos

- **`build_windows_exe.bat`**: empaqueta el proyecto, resuelve los *hidden imports* de ReportLab, **crea acceso directo** en el Escritorio y abre `dist/`.
- **`run_dev.bat`**: instala dependencias y ejecuta `main.py` desde fuentes.

Colocá un ícono **`icono.ico`** en la raíz para que el `.bat` lo use en el `.exe` y el acceso directo.

---

## 🆘 Solución de problemas

- **SmartScreen/Antivirus**: “Más información” → “Ejecutar de todas formas” o añadí `dist/` a exclusiones.
- **DLLs faltantes**: instalá **Microsoft Visual C++ Redistributable 2015–2022 (x64)**.
- **ReportLab/Barcode en PyInstaller**: ya resuelto con **hook** y `--collect-submodules` en el `.bat`.
- **Base vieja**: si cambiaste el esquema, borrá `data/credenciales.db` para regenerar tablas.
- **No tengo Excel**: la app genera **Plantilla** y el **Importador** funciona con `.xlsx`.

---

## 📣 Autoría

- Desarrollo: **Ignacio Velázquez** (“IV”).
- Icono por defecto: **código de barras + "IV"** (incluido en este repositorio como `icono.ico` si se desea).

---

## 📄 Licencia

Este proyecto se distribuye con una licencia permisiva. Ajustá a tu preferencia (**MIT** recomendado) o mantenelo privado.
