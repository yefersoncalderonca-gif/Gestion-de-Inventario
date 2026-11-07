"""Validaciones compartidas de NIT y teléfono.
Si cambia el rango permitido, se modifica SOLO aquí."""
from django.core.exceptions import ValidationError

NIT_MIN = 9          # mínimo de dígitos del NIT
NIT_MAX = 10         # máximo de dígitos (9 + dígito de verificación)
TEL_FIJO = 7         # dígitos de un teléfono fijo
TEL_CELULAR = 10     # dígitos de un celular (empieza por 3)


def validar_nit(valor):
    """Devuelve el NIT limpio o lanza ValidationError."""
    nit = (valor or "").strip()
    if not (nit.isascii() and nit.isdigit()):
        raise ValidationError(
            "El NIT debe tener solo números, sin puntos, espacios ni guiones.")
    if not (NIT_MIN <= len(nit) <= NIT_MAX):
        raise ValidationError(
            "El NIT debe tener entre %d y %d dígitos (escribió %d)."
            % (NIT_MIN, NIT_MAX, len(nit)))
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
