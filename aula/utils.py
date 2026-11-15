"""Utilidades compartidas por los listados: paginación con filtros conservados."""

from urllib.parse import urlencode

from django.core.paginator import Paginator

LETRAS_INICIALES = 2  # letras de las siglas y avatares (iniciales de las dos primeras palabras)
POR_PAGINA = 15  # filas visibles por página en los listados


def paginar(request, items, por_pagina=POR_PAGINA):
    """Pagina una lista y deja en `page.qs` los filtros actuales (sin `page`)."""
    page = Paginator(items, por_pagina).get_page(request.GET.get("page"))
    page.qs = urlencode(
        [(k, v) for k, v in request.GET.items() if k not in ("page", "export") and v]
    )
    return page
