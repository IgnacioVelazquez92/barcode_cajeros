# app/utils.py
from datetime import datetime


def generar_clave(dni: str) -> str:
    """Genera la clave en formato DNI + fecha actual (DDMM)."""
    fecha = datetime.now().strftime("%d%m")
    return f"{dni}{fecha}"
