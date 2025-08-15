# app/pdf_generator.py
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.lib.pagesizes import A4
import os
from app import db
from app.paths import base_dir, ensure_dirs

BASE_DIR = base_dir()
PDF_DIR = os.path.join(BASE_DIR, "pdfs")
ensure_dirs("pdfs")


# Medidas de la credencial
CRED_W = 8.3 * cm   # ancho
CRED_H = 5.3 * cm   # alto

# Medidas del código de barras
BAR_H = 3.0 * cm                 # alto fijo
BAR_MAX_W = 5.0 * cm             # ancho máximo permitido
MIN_MODULE_W = 0.25 * (cm / 10)  # 0.25 mm mínimo p/ evitar barras “hilo”


def _barcode_ajustado(clave: str, max_width: float):
    """
    Crea un Code128 de alto BAR_H y ajusta el barWidth para que el ancho total
    no supere max_width y nunca sea demasiado fino.
    """
    ref = code128.Code128(clave, barHeight=BAR_H,
                          barWidth=1.0)  # módulo 1pt (referencia)
    scale = max_width / ref.width
    bar_width = max(MIN_MODULE_W, scale)  # evita barras ultra finas
    return code128.Code128(clave, barHeight=BAR_H, barWidth=bar_width)


def generar_pdf(nombre_mostrar, clave):
    """PDF A4 con UNA credencial centrada.
    Muestra 'nombre_mostrar' (idealmente 'nombre_sistema') pegado al código de barras.
    """
    ruta = os.path.join(PDF_DIR, f"{nombre_mostrar}.pdf")
    c = canvas.Canvas(ruta, pagesize=A4)

    page_w, page_h = A4
    x = (page_w - CRED_W) / 2
    y = (page_h - CRED_H) / 2

    # Marco (opcional)
    c.roundRect(x, y, CRED_W, CRED_H, 6)

    # --- Código de barras (primero) ---
    barcode = _barcode_ajustado(clave, BAR_MAX_W)
    bar_w = barcode.width
    bar_x = x + (CRED_W - bar_w) / 2
    bar_y = y + 0.9 * cm  # un poco más arriba del borde inferior

    barcode.drawOn(c, bar_x, bar_y)

    # --- Nombre (justo por encima del código) ---
    c.setFont("Helvetica-Bold", 12)
    nombre_y = bar_y + BAR_H + 0.2 * cm  # “más cerca” del código
    # Tope superior de seguridad
    nombre_y = min(nombre_y, y + CRED_H - 0.3 * cm)
    c.drawCentredString(x + CRED_W / 2, nombre_y, nombre_mostrar)

    c.showPage()
    c.save()
    return ruta


def generar_pdf_multiples(ids):
    """PDF A4 con múltiples credenciales por hoja, paginando automáticamente.
    Muestra 'nombre_sistema' si existe; caso contrario, 'nombre'."""
    try:
        ruta = os.path.join(PDF_DIR, "credenciales_multiples.pdf")
        c = canvas.Canvas(ruta, pagesize=A4)

        page_w, page_h = A4
        margin = 1.0 * cm
        gap_x = 0.6 * cm
        gap_y = 0.6 * cm

        cols = int((page_w - 2 * margin + gap_x) // (CRED_W + gap_x))
        rows = int((page_h - 2 * margin + gap_y) // (CRED_H + gap_y))
        cols = max(1, cols)
        rows = max(1, rows)
        per_page = cols * rows

        cajeros = [db.obtener_por_id(i) for i in ids]
        cajeros = [caj for caj in cajeros if caj]

        for idx, caj in enumerate(cajeros):
            if idx > 0 and idx % per_page == 0:
                c.showPage()

            slot = idx % per_page
            col = slot % cols
            row = slot // cols

            x = margin + col * (CRED_W + gap_x)
            # desde arriba hacia abajo
            y = page_h - margin - (row + 1) * (CRED_H + gap_y) + gap_y

            # Dataset: (id, legajo, nombre, nombre_sistema, dni, clave, fecha, sucursal)
            nombre_completo = caj[2] or ""
            nombre_sistema = caj[3] or ""
            nombre_mostrar = (nombre_sistema.strip()
                              or nombre_completo.strip())
            clave = caj[5]

            _dibujar_credencial(c, x, y, nombre_mostrar, clave)

        if cajeros:
            c.showPage()
        c.save()
        return True
    except Exception as e:
        print(f"Error al generar PDF múltiple: {e}")
        return False


def _dibujar_credencial(c: canvas.Canvas, x: float, y: float, nombre_mostrar: str, clave: str):
    """Dibuja una credencial (8.3x5.3 cm) con el NOMBRE pegado al código de barras."""
    c.roundRect(x, y, CRED_W, CRED_H, 6)

    # Código de barras (primero)
    barcode = _barcode_ajustado(clave, BAR_MAX_W)
    bar_w = barcode.width
    bar_x = x + (CRED_W - bar_w) / 2
    bar_y = y + 0.9 * cm

    barcode.drawOn(c, bar_x, bar_y)

    # Nombre (justo por encima)
    c.setFont("Helvetica-Bold", 12)
    nombre_y = bar_y + BAR_H + 0.2 * cm
    nombre_y = min(nombre_y, y + CRED_H - 0.3 * cm)
    c.drawCentredString(x + CRED_W / 2, nombre_y, nombre_mostrar)
