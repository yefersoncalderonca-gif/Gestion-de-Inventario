"""Filtros y etiquetas propios de las plantillas (`{% load inv %}`)."""
from decimal import Decimal

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

# Íconos de línea (viewBox 24x24). Se dibujan con trazo, sin relleno.
ICONOS = {
    "box": '<path d="M21 8l-9-5-9 5v8l9 5 9-5V8z"/><path d="M3.3 7.5L12 12.5l8.7-5M12 22V12.5"/>',
    "panel": '<rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>',
    "layers": '<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 13l9 5 9-5"/>',
    "swap": '<path d="M7 4L3 8l4 4M3 8h14M17 20l4-4-4-4M21 16H7"/>',
    "truck": '<path d="M2 6h11v10H2zM13 9h5l3 3v4h-8"/><circle cx="6.5" cy="17.5" r="1.8"/><circle cx="17.5" cy="17.5" r="1.8"/>',
    "users": '<circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><path d="M16 5.2a3.2 3.2 0 010 5.6M18 14.3c1.8.7 3 2.4 3 4.7"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "pin": '<path d="M12 21s7-6.2 7-11.5A7 7 0 005 9.5C5 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "logout": '<path d="M9 4H5a2 2 0 00-2 2v12a2 2 0 002 2h4M16 8l4 4-4 4M20 12H9"/>',
    "user": '<circle cx="12" cy="8" r="3.5"/><path d="M5 20c0-3.9 3.1-7 7-7s7 3.1 7 7"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "alert": '<path d="M12 3L2 20h20L12 3z"/><path d="M12 10v4M12 17.2v.1"/>',
    "arrow-right": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "arrow-left": '<path d="M19 12H5M11 6l-6 6 6 6"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/>',
    "edit": '<path d="M4 20h4L19 9l-4-4L4 16v4z"/><path d="M13.5 6.5l4 4"/>',
    "trash": '<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v6M14 11v6"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 7.8v.1"/>',
    "in": '<path d="M12 4v12M6 11l6 6 6-6M5 20h14"/>',
    "out": '<path d="M12 20V8M6 13l6-6 6 6M5 4h14"/>',
    "bell": '<path d="M6 16V11a6 6 0 0112 0v5l2 2H4l2-2z"/><path d="M10 20a2 2 0 004 0"/>',
    "file": '<path d="M6 3h8l5 5v13H6z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
    "lock": '<rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10V7a4 4 0 018 0v3"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "eye": '<path d="M2 12s3.7-7 10-7 10 7 10 7-3.7 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "shield": '<path d="M12 3l8 3v6c0 4.5-3.2 7.8-8 9-4.8-1.2-8-4.5-8-9V6l8-3z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "user-plus": '<circle cx="10" cy="8" r="3.5"/><path d="M3 20c0-3.9 3.1-7 7-7 1.4 0 2.7.4 3.8 1.1M18 14v6M15 17h6"/>',
    "download": '<path d="M12 4v11M7 11l5 5 5-5M5 20h14"/>',
    "filter": '<path d="M3 5h18l-7 8v6l-4-2v-4L3 5z"/>',
}


@register.simple_tag
def icon(nombre, tam=16):
    """Dibuja un ícono SVG: {% icon 'box' 18 %}."""
    trazos = ICONOS.get(nombre, ICONOS["info"])
    return format_html(
        '<svg class="ic" width="{0}" height="{0}" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true">{1}</svg>',
        tam, mark_safe(trazos),
    )


@register.filter
def cop(valor):
    """Pesos colombianos sin decimales: 95000 -> $95.000"""
    try:
        n = int(Decimal(valor).quantize(Decimal("1")))
    except (TypeError, ValueError, ArithmeticError):
        return "—"
    return "$" + f"{n:,}".replace(",", ".")


@register.filter
def pct(valor):
    """Altura de barra: número entre 0 y 100 (entero)."""
    try:
        return max(0, min(100, int(round(float(valor)))))
    except (TypeError, ValueError):
        return 0
