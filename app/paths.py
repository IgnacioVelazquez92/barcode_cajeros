# app/paths.py
import os
import sys


def base_dir() -> str:
    """
    Directorio base para datos en modo ejecutable (PyInstaller) o desarrollo.
    - Ejecutable: carpeta donde está el .exe
    - Dev: carpeta raíz del proyecto
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(__file__))


def ensure_dirs(*folders: str) -> None:
    for folder in folders:
        os.makedirs(os.path.join(base_dir(), folder), exist_ok=True)
