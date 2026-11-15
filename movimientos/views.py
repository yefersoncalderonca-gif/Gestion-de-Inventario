"""Vistas de movimientos: registro de entradas y salidas, historial por fecha y sugerencias."""

from datetime import date

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from clientes.models import Cliente
from proveedores.models import Proveedor
from usuarios.auth import requiere_sesion

from .forms import MovimientoForm
from .models import Movimiento, StockInsuficienteError, siguiente_factura


def _terceros(tipo):
    """Nombres de proveedores (entradas) o clientes (salidas) para el campo con sugerencias."""
    modelo = Proveedor if tipo == "E" else Cliente
    return list(modelo.objects.values_list("nombre", flat=True))


@requiere_sesion
def movimientos(request):
    """Registra un movimiento (validando existencias) y muestra el historial de una fecha."""
    tipo = request.POST.get("tipo") if request.method == "POST" else request.GET.get("tipo")
    tipo = tipo if tipo in ("E", "S") else "E"
    form = MovimientoForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        producto = d["producto"]
        modelo = Proveedor if tipo == "E" else Cliente
        tercero = modelo.objects.filter(nombre__iexact=d["tercero"].strip()).first()
        if tercero is None:
            form.add_error(
                "tercero",
                f"No existe ese {'proveedor' if tipo == 'E' else 'cliente'}. "
                "Escógelo de la lista o regístralo primero.",
            )
        else:
            try:
                movimiento = Movimiento(
                    tipo=tipo,
                    cantidad=d["cantidad"],
                    fecha=d["fecha"],
                    motivo=d["motivo"],
                    observaciones=d["observaciones"],
                    producto=producto,
                    usuario=request.usuario,
                    proveedor=tercero if tipo == "E" else None,
                    cliente=tercero if tipo == "S" else None,
                )
                movimiento.registrar()
            except StockInsuficienteError as error:
                form.add_error("cantidad", str(error))
            else:
                messages.success(
                    request,
                    f"{'Entrada' if tipo == 'E' else 'Salida'} registrada: "
                    f"{d['cantidad']} × {producto.nombre}. Factura {movimiento.factura}.",
                )
                return redirect("movimientos")

    try:
        fecha_hist = date.fromisoformat(request.GET.get("fecha", ""))
    except ValueError:
        fecha_hist = timezone.localdate()
    hist = list(
        Movimiento.objects.filter(fecha=fecha_hist).select_related(
            "producto", "cliente", "proveedor"
        )
    )
    return render(
        request,
        "movimientos.html",
        {
            "activo": "movimientos",
            "form": form,
            "tipo_sel": tipo,
            "terceros": _terceros(tipo),
            "hist": hist,
            "fecha_hist": fecha_hist,
            "factura_sugerida": siguiente_factura(tipo),
        },
    )


@requiere_sesion
def terceros(request):
    """Lista de proveedores (entradas) o clientes (salidas) para el campo con sugerencias."""
    tipo = "S" if request.GET.get("tipo") == "S" else "E"
    return JsonResponse({"terceros": _terceros(tipo)})
