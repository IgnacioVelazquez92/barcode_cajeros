from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.lib.pagesizes import A4
import os
from app import db

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Carpeta donde se guardarán los PDFs
PDF_DIR = os.path.join(BASE_DIR, "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)


def generar_pdf(nombre, clave):
    """Genera un PDF A4 con una credencial tamaño 8.3 x 5.3 cm"""
    archivo_pdf = os.path.join(PDF_DIR, f"{nombre}.pdf")
    c = canvas.Canvas(archivo_pdf, pagesize=A4)

    ancho_credencial = 8.3 * cm
    alto_credencial = 5.3 * cm
    margen_x = (A4[0] - ancho_credencial) / 2
    margen_y = (A4[1] - alto_credencial) / 2

    # Dibujar borde (opcional)
    c.roundRect(margen_x, margen_y, ancho_credencial, alto_credencial, 5)

    # Nombre y código de barras uno al lado del otro
    c.setFont("Helvetica-Bold", 12)
    texto_x = margen_x + 0.5 * cm
    texto_y = margen_y + (alto_credencial / 2) - 6
    c.drawString(texto_x, texto_y, nombre)

    # Código de barras (3cm alto, hasta 5cm ancho)
    barcode = code128.Code128(clave, barHeight=3 * cm)
    barcode_x = texto_x + 4.5 * cm  # Ubicación a la derecha del nombre
    barcode_y = margen_y + (alto_credencial - 3 * cm) / 2
    barcode.drawOn(c, barcode_x, barcode_y)

    c.showPage()
    c.save()
    return archivo_pdf


def generar_pdf_multiples(ids):
    """Genera un PDF A4 con múltiples credenciales por hoja."""
    try:
        archivo_pdf = os.path.join(PDF_DIR, "credenciales_multiples.pdf")
        c = canvas.Canvas(archivo_pdf, pagesize=A4)

        ancho_pagina, alto_pagina = A4
        margen = 1 * cm

        ancho_credencial = 8.3 * cm
        alto_credencial = 5.3 * cm

        espacio_x = 1 * cm
        espacio_y = 1 * cm

        columnas = int((ancho_pagina - 2 * margen + espacio_x) //
                       (ancho_credencial + espacio_x))
        filas = int((alto_pagina - 2 * margen + espacio_y) //
                    (alto_credencial + espacio_y))

        cajeros = [db.obtener_por_id(
            id_) for id_ in ids if db.obtener_por_id(id_) is not None]

        col = 0
        fil = 0

        for cajero in cajeros:
            id_, nombre, dni, clave, fecha = cajero

            x = margen + col * (ancho_credencial + espacio_x)
            y = alto_pagina - margen - \
                (fil + 1) * (alto_credencial + espacio_y)

            c.roundRect(x, y, ancho_credencial, alto_credencial, 5)

            # Nombre
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x + 0.5 * cm, y + alto_credencial / 2 - 6, nombre)

            # Código de barras
            barcode = code128.Code128(clave, barHeight=3 * cm)
            barcode_x = x + 4.5 * cm
            barcode_y = y + (alto_credencial - 3 * cm) / 2
            barcode.drawOn(c, barcode_x, barcode_y)

            col += 1
            if col >= columnas:
                col = 0
                fil += 1
            if fil >= filas:
                c.showPage()
                col = 0
                fil = 0

        c.showPage()
        c.save()
        return True
    except Exception as e:
        print(f"Error al generar PDF múltiple: {e}")
        return False
