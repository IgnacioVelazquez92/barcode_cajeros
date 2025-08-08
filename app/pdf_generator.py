# app/pdf_generator.py
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.lib.pagesizes import A4
import os
from app import db

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PDF_DIR = os.path.join(BASE_DIR, "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

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


def generar_pdf(nombre, clave):
    """PDF A4 con UNA credencial centrada. Nombre ARRIBA y código ABAJO."""
    ruta = os.path.join(PDF_DIR, f"{nombre}.pdf")
    c = canvas.Canvas(ruta, pagesize=A4)

    page_w, page_h = A4
    x = (page_w - CRED_W) / 2
    y = (page_h - CRED_H) / 2

    # Marco (opcional)
    c.roundRect(x, y, CRED_W, CRED_H, 6)

    # --- Nombre (más cerca del código) ---
    c.setFont("Helvetica-Bold", 12)
    nombre_y = y + CRED_H - 0.5 * cm     # antes 0.8cm
    c.drawCentredString(x + CRED_W / 2, nombre_y, nombre)

    # --- Código de barras (más arriba) ---
    barcode = _barcode_ajustado(clave, BAR_MAX_W)
    bar_w = barcode.width
    bar_x = x + (CRED_W - bar_w) / 2
    bar_y = y + 1.2 * cm                 # antes 0.6cm

    # Si por altura choca con el nombre, lo ajustamos
    if bar_y + BAR_H > nombre_y - 0.4 * cm:
        bar_y = max(y + 0.3 * cm, nombre_y - 0.4 * cm - BAR_H)

    barcode.drawOn(c, bar_x, bar_y)

    c.showPage()
    c.save()
    return ruta


def generar_pdf_multiples(ids):
    """PDF A4 con múltiples credenciales por hoja, paginando automáticamente."""
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
            # dibujo desde arriba hacia abajo
            y = page_h - margin - (row + 1) * (CRED_H + gap_y) + gap_y

            _dibujar_credencial(c, x, y, caj[1], caj[3])

        if cajeros:
            c.showPage()
        c.save()
        return True
    except Exception as e:
        print(f"Error al generar PDF múltiple: {e}")
        return False


def _dibujar_credencial(c: canvas.Canvas, x: float, y: float, nombre: str, clave: str):
    """Dibuja una credencial (8.3x5.3 cm) con NOMBRE arriba y BARCODE debajo, más cercanos."""
    c.roundRect(x, y, CRED_W, CRED_H, 6)

    # Nombre (más cerca del código)
    c.setFont("Helvetica-Bold", 12)
    nombre_y = y + CRED_H - 0.5 * cm     # antes 0.8cm
    c.drawCentredString(x + CRED_W / 2, nombre_y, nombre)

    # Código de barras (más arriba)
    barcode = _barcode_ajustado(clave, BAR_MAX_W)
    bar_w = barcode.width
    bar_x = x + (CRED_W - bar_w) / 2
    bar_y = y + 1.2 * cm                 # antes 0.6cm

    if bar_y + BAR_H > nombre_y - 0.4 * cm:
        bar_y = max(y + 0.3 * cm, nombre_y - 0.4 * cm - BAR_H)

    barcode.drawOn(c, bar_x, bar_y)
