from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone

from movimientos.models import Movimiento
from productos.models import Producto
from usuarios.auth import requiere_sesion


@requiere_sesion
def panel(request):
    hoy = timezone.localdate()
    prods = list(Producto.objects.select_related("categoria"))
    vencen = sorted((p for p in prods if p.fecha_vencimiento and p.dias_vencimiento <= 30),
                    key=lambda p: p.fecha_vencimiento)
    recargas = sorted((p for p in prods if p.fecha_proxima_recarga and p.dias_recarga <= 30),
                      key=lambda p: p.fecha_proxima_recarga)
    bajo = [p for p in prods if p.bajo_minimo]
    atencion = [p for p in prods if p.bajo_minimo or p.estado in ("Vencido", "Urgente", "Por vencer")]

    # Movimientos de los últimos 7 días (hoy incluido)
    desde = hoy - timedelta(days=6)
    por_dia = {desde + timedelta(days=i): [0, 0] for i in range(7)}
    for m in Movimiento.objects.filter(fecha__gte=desde, fecha__lte=hoy):
        por_dia[m.fecha][0 if m.tipo == "E" else 1] += m.cantidad
    mayor = max([max(v) for v in por_dia.values()] + [1])
    tope = mayor + (mayor % 2)          # par, para que la mitad sea entera
    dias = [{"fecha": f, "e": e, "s": s, "eh": e * 100 / tope, "sh": s * 100 / tope}
            for f, (e, s) in por_dia.items()]

    return render(request, "panel.html", {
        "activo": "panel", "prods": prods, "total_unidades": sum(p.stock for p in prods),
        "vencen": vencen, "recargas": recargas, "bajo": bajo, "atencion": atencion,
        "desde": desde, "hasta": hoy, "tope": tope, "tope_mid": tope // 2, "dias": dias,
    })
