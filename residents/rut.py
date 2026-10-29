"""Utilidades para normalizar y validar el RUT chileno."""

from __future__ import annotations


def clean_rut(value: str | None) -> str:
    """Devuelve el RUT en formato 12345678-9.

    Acepta puntos, espacios y guion. No valida el dígito verificador.
    """

    if not value:
        return ""
    compact = str(value).upper().replace(".", "").replace(" ", "").replace("-", "")
    if len(compact) < 2:
        return compact
    return f"{compact[:-1]}-{compact[-1]}"


def rut_display(value: str | None) -> str:
    """Formatea un RUT normalizado con puntos para mostrarlo."""

    cleaned = clean_rut(value)
    if "-" not in cleaned:
        return cleaned
    body, dv = cleaned.split("-", 1)
    if not body.isdigit():
        return cleaned
    return f"{int(body):,}".replace(",", ".") + f"-{dv}"


def calculate_dv(body: str) -> str:
    """Calcula el dígito verificador de un cuerpo numérico."""

    total = 0
    multiplier = 2
    for digit in reversed(body):
        total += int(digit) * multiplier
        multiplier = 2 if multiplier == 7 else multiplier + 1
    remainder = 11 - (total % 11)
    if remainder == 11:
        return "0"
    if remainder == 10:
        return "K"
    return str(remainder)


def validate_rut(value: str | None) -> bool:
    """Valida formato y dígito verificador."""

    cleaned = clean_rut(value)
    if "-" not in cleaned:
        return False
    body, dv = cleaned.split("-", 1)
    if not body.isdigit() or not dv or len(dv) != 1:
        return False
    if not 7 <= len(body) <= 8:
        return False
    return calculate_dv(body) == dv
