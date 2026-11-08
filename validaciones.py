"""Validaciones compartidas de NIT y teléfono.
Si cambia el rango permitido, se modifica SOLO aquí."""
import re

from django.core.exceptions import ValidationError

NIT_DIGITOS_BASE = 9     # dígitos del NIT sin dígito de verificación
TEL_FIJO = 7             # dígitos de un teléfono fijo
TEL_CELULAR = 10         # dígitos de un celular (empieza por 3)
# 9 dígitos + dígito de verificación opcional, con o sin guion
NIT_PATRON = re.compile(r"\d{%d}(-?\d)?" % NIT_DIGITOS_BASE, re.ASCII)


def validar_nit(valor):
    """Devuelve el NIT limpio o lanza ValidationError."""
    nit = (valor or "").strip()
    if not NIT_PATRON.fullmatch(nit):
        raise ValidationError(
            "El NIT debe tener %d dígitos y, opcionalmente, el dígito de "
            "verificación (ejemplo: 900123456-1)." % NIT_DIGITOS_BASE)
    return nit


def validar_telefono(valor):
    """Devuelve el teléfono limpio o lanza ValidationError."""
    tel = (valor or "").strip()
    if not (tel.isascii() and tel.isdigit()):
        raise ValidationError("El teléfono debe tener solo números.")
    es_celular = len(tel) == TEL_CELULAR and tel.startswith("3")
    es_fijo = len(tel) == TEL_FIJO
    if not (es_celular or es_fijo):
        raise ValidationError(
            "Escriba un celular de %d dígitos que empiece por 3 "
            "(ejemplo: 3101234567) o un fijo de %d dígitos."
            % (TEL_CELULAR, TEL_FIJO))
    return tel