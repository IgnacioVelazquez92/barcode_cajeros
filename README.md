# 🧾 Gestor de Credenciales de Cajeros

Aplicación de escritorio desarrollada en Python con `Tkinter`, `SQLite` y `ReportLab` para generar credenciales con código de barras.

---

## 🚀 Características

- Alta de cajeros con nombre y DNI.
- Generación de credenciales con código de barras (clave).
- Exportación a PDF tamaño A4.
- Reimpresión de credenciales.
- Búsqueda por nombre o DNI.
- Exportación múltiple seleccionando cajeros.
- Base de datos local SQLite.
- Interfaz con pestañas (formulario y listado).

---

## 🛠 Requisitos

- Python 3.11+
- Entorno virtual (recomendado)

### 🔧 Instalación

```bash
git clone https://github.com/tu_usuario/credenciales_app.git
cd credenciales_app
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python main.py
```

### 🗂 Estructura

```
credenciales_app/
├── app/
│   ├── controller.py
│   ├── db.py
│   ├── pdf_generator.py
│   ├── ui_form.py
│   ├── ui_table.py
│   ├── ui_exportador_multiple.py
│   ├── utils.py
├── main.py
├── data/
├── pdfs/
├── excel/
├── README.md
└── .gitignore
```
