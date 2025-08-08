from datetime import datetime


def generar_clave(dni: str) -> str:
    """DNI + fecha actual (DDMM)"""
    fecha = datetime.now().strftime("%d%m")
    return f"{dni}{fecha}"


def _k_semilla(fecha: datetime | None = None) -> int:
    """Semilla simple: (DD+MM) % 10"""
    dt = fecha or datetime.now()
    return (int(dt.strftime("%d")) + int(dt.strftime("%m"))) % 10


def ofuscar_clave(clave: str, k: int | None = None) -> str:
    """
    Reversible y simple:
    1) Invertir
    2) Desplazar cada dígito por k (mod 10)
    """
    if k is None:
        k = _k_semilla()
    rev = clave[::-1]
    out = []
    for ch in rev:
        if ch.isdigit():
            out.append(str((int(ch) + k) % 10))
        else:
            out.append(ch)  # por si algún día metés letras, se dejan igual
    return "".join(out)


def desofuscar_clave(ofuscada: str, k: int | None = None) -> str:
    """Reversa exacta de ofuscar_clave"""
    if k is None:
        k = _k_semilla()
    tmp = []
    for ch in ofuscada:
        if ch.isdigit():
            tmp.append(str((int(ch) - k) % 10))
        else:
            tmp.append(ch)
    return "".join(tmp)[::-1]
