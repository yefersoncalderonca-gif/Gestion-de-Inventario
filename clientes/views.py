from django.contrib import messages
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render

from aula.utils import paginar
from usuarios.auth import requiere_sesion, solo_admin

from .forms import ClienteForm
from .models import Cliente


@requiere_sesion
def clientes(request):
    q = request.GET.get("q", "").strip()
    f = request.GET.get("f", "")
    lista = Cliente.objects.annotate(
        salidas=Count("movimiento", filter=Q(movimiento__tipo="S")),
        ultima=Max("movimiento__fecha", filter=Q(movimiento__tipo="S")),
    )
    if q:
        lista = lista.filter(Q(nombre__icontains=q) | Q(nit__icontains=q))
    if f == "con":
        lista = lista.filter(salidas__gt=0)
    elif f == "sin":
        lista = lista.filter(salidas=0)
    filas = [{"c": c, "salidas": c.salidas, "ultima": c.ultima} for c in lista]
    return render(request, "clientes.html", {
        "activo": "clientes", "q": q, "f": f, "total": Cliente.objects.count(),
        "page": paginar(request, filas),
    })


def _formulario(request, obj=None):
    form = ClienteForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        c = form.save()
        messages.success(request, f"Cliente «{c.nombre}» guardado.")
        return redirect("clientes")
    return render(request, "form_simple.html", {
        "activo": "clientes", "form": form, "volver": "clientes",
        "titulo": "Editar cliente" if obj else "Nuevo cliente",
        "sub": "Datos de quien compra insumos o contrata servicios.",
    })


@solo_admin
def cliente_nuevo(request):
    return _formulario(request)


@solo_admin
def cliente_editar(request, pk):
    return _formulario(request, get_object_or_404(Cliente, pk=pk))
