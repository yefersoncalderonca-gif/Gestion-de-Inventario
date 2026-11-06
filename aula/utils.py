from urllib.parse import urlencode

from django.core.paginator import Paginator


def paginar(request, items, por_pagina=8):
    """Pagina una lista y deja en `page.qs` los filtros actuales (sin `page`)."""
    page = Paginator(items, por_pagina).get_page(request.GET.get("page"))
    page.qs = urlencode([(k, v) for k, v in request.GET.items() if k not in ("page", "export") and v])
    return page
