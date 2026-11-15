"""Vista del panel principal: indicadores, alertas y gráfico de movimientos recientes."""

from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone

from movimientos.models import Movimiento
from productos.models import DIAS_ALERTA, Producto
from usuarios.auth import requiere_sesion

DIAS_GRAFICO = 7  # días que muestra el gráfico de movimientos
PORCENTAJE_TOTAL = 100  # altura máxima de una barra del gráfico, en %


@requiere_sesion
def panel(request):
    """Muestra el panel con vencimientos, recargas, bajo stock y movimientos de la última semana."""
    hoy = timezone.localdate()
    prods = list(Producto.objects.select_related("categoria"))
    vencen = sorted(
        (p for p in prods if p.fecha_vencimiento and p.dias_vencimiento <= DIAS_ALERTA),
        key=lambda p: p.fecha_vencimiento,
    )
    recargas = sorted(
        (p for p in prods if p.fecha_proxima_recarga and p.dias_recarga <= DIAS_ALERTA),
        key=lambda p: p.fecha_proxima_recarga,
    )
    bajo = [p for p in prods if p.bajo_minimo]
    atencion = [
        p for p in prods if p.bajo_minimo or p.estado in ("Vencido", "Urgente", "Por vencer")
    ]

    # Movimientos de los últimos DIAS_GRAFICO días (hoy incluido)
    desde = hoy - timedelta(days=DIAS_GRAFICO - 1)
    por_dia = {desde + timedelta(days=i): [0, 0] for i in range(DIAS_GRAFICO)}
    for m in Movimiento.objects.filter(fecha__gte=desde, fecha__lte=hoy):
        por_dia[m.fecha][0 if m.tipo == "E" else 1] += m.cantidad
    mayor = max([max(v) for v in por_dia.values()] + [1])
    tope = mayor + (mayor % 2)  # par, para que la mitad sea entera
    dias = [
        {
            "fecha": f,
            "e": e,
            "s": s,
            "eh": e * PORCENTAJE_TOTAL / tope,
            "sh": s * PORCENTAJE_TOTAL / tope,
        }
        for f, (e, s) in por_dia.items()
    ]

    return render(
        request,
        "panel.html",
        {
            "activo": "panel",
            "prods": prods,
            "total_unidades": sum(p.stock for p in prods),
            "vencen": vencen,
            "recargas": recargas,
            "bajo": bajo,
            "atencion": atencion,
            "desde": desde,
            "hasta": hoy,
            "tope": tope,
            "tope_mid": tope // 2,
            "dias": dias,
        },
    )
