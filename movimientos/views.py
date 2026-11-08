from datetime import date

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from clientes.models import Cliente
from proveedores.models import Proveedor
from usuarios.auth import requiere_sesion

from .forms import MovimientoForm
from .models import Movimiento, StockInsuficienteError


def _terceros(tipo):
    modelo = Proveedor if tipo == "E" else Cliente
    return list(modelo.objects.values_list("nombre", flat=True))


@requiere_sesion
def movimientos(request):
    tipo = request.POST.get("tipo") if request.method == "POST" else request.GET.get("tipo")
    tipo = tipo if tipo in ("E", "S") else "E"
    form = MovimientoForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        producto = d["producto"]
        modelo = Proveedor if tipo == "E" else Cliente
        tercero = modelo.objects.filter(nombre__iexact=d["tercero"].strip()).first()
        if tercero is None:
            form.add_error("tercero", f"No existe ese {'proveedor' if tipo == 'E' else 'cliente'}. "
                                      "Escógelo de la lista o regístralo primero.")
        else:
            try:
                Movimiento(
                    tipo=tipo, cantidad=d["cantidad"], fecha=d["fecha"], motivo=d["motivo"],
                    factura=d["factura"], observaciones=d["observaciones"], producto=producto,
                    usuario=request.usuario,
                    proveedor=tercero if tipo == "E" else None,
                    cliente=tercero if tipo == "S" else None,
                ).registrar()
            except StockInsuficienteError as error:
                form.add_error("cantidad", str(error))
            else:
                messages.success(request, f"{'Entrada' if tipo == 'E' else 'Salida'} registrada: "
                                          f"{d['cantidad']} × {producto.nombre}.")
                return redirect("movimientos")

    try:
        fecha_hist = date.fromisoformat(request.GET.get("fecha", ""))
    except ValueError:
        fecha_hist = timezone.localdate()
    hist = list(Movimiento.objects.filter(fecha=fecha_hist)
                .select_related("producto", "cliente", "proveedor"))
    return render(request, "movimientos.html", {
        "activo": "movimientos", "form": form, "tipo_sel": tipo, "terceros": _terceros(tipo),
        "hist": hist, "fecha_hist": fecha_hist,
    })


@requiere_sesion
def terceros(request):
    """Lista de proveedores (entradas) o clientes (salidas) para el campo con sugerencias."""
    tipo = "S" if request.GET.get("tipo") == "S" else "E"
    return JsonResponse({"terceros": _terceros(tipo)})
