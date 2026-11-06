from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from aula.utils import paginar
from usuarios.auth import requiere_sesion, solo_admin

from .forms import ProveedorForm
from .models import Proveedor


@requiere_sesion
def proveedores(request):
    q = request.GET.get("q", "").strip()
    lista = Proveedor.objects.all()
    if q:
        lista = lista.filter(Q(nombre__icontains=q) | Q(nit__icontains=q) |
                             Q(telefono__icontains=q) | Q(correo__icontains=q))
    return render(request, "proveedores.html", {
        "activo": "proveedores", "q": q, "total": Proveedor.objects.count(),
        "page": paginar(request, list(lista)),
    })


def _formulario(request, obj=None):
    form = ProveedorForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        p = form.save()
        messages.success(request, f"Proveedor «{p.nombre}» guardado.")
        return redirect("proveedores")
    return render(request, "form_simple.html", {
        "activo": "proveedores", "form": form, "volver": "proveedores",
        "titulo": "Editar proveedor" if obj else "Nuevo proveedor",
        "sub": "Datos de contacto de quien abastece el inventario.",
    })


@solo_admin
def proveedor_nuevo(request):
    return _formulario(request)


@solo_admin
def proveedor_editar(request, pk):
    return _formulario(request, get_object_or_404(Proveedor, pk=pk))


@solo_admin
@require_POST
def proveedor_eliminar(request, pk):
    obj = get_object_or_404(Proveedor, pk=pk)
    if obj.movimiento_set.exists():
        messages.error(request, f"No se puede eliminar a «{obj.nombre}»: tiene entradas registradas.")
    else:
        obj.delete()          # los productos asociados quedan sin proveedor
        messages.success(request, f"Proveedor «{obj.nombre}» eliminado.")
    return redirect("proveedores")
