"""Vistas de proveedores: listado con búsqueda, alta, edición y eliminación."""

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
    """Lista los proveedores; la búsqueda mira nombre, NIT, teléfono y correo."""
    q = request.GET.get("q", "").strip()
    lista = Proveedor.objects.all()
    if q:
        lista = lista.filter(
            Q(nombre__icontains=q)
            | Q(nit__icontains=q)
            | Q(telefono__icontains=q)
            | Q(correo__icontains=q)
        )
    return render(
        request,
        "proveedores.html",
        {
            "activo": "proveedores",
            "q": q,
            "total": Proveedor.objects.count(),
            "page": paginar(request, list(lista)),
        },
    )


def _formulario(request, obj=None):
    """Muestra el formulario de proveedor y lo guarda cuando es válido (alta o edición)."""
    form = ProveedorForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        p = form.save()
        messages.success(request, f"Proveedor «{p.nombre}» guardado.")
        return redirect("proveedores")
    return render(
        request,
        "form_simple.html",
        {
            "activo": "proveedores",
            "form": form,
            "volver": "proveedores",
            "titulo": "Editar proveedor" if obj else "Nuevo proveedor",
            "sub": "Datos de contacto de quien abastece el inventario.",
        },
    )


@solo_admin
def proveedor_nuevo(request):
    """Formulario para registrar un proveedor (solo administrador)."""
    return _formulario(request)


@solo_admin
def proveedor_editar(request, pk):
    """Formulario para modificar un proveedor existente (solo administrador)."""
    return _formulario(request, get_object_or_404(Proveedor, pk=pk))


@solo_admin
@require_POST
def proveedor_eliminar(request, pk):
    """Borra el proveedor, o lo archiva si ya tiene entradas, para conservar el historial."""
    obj = get_object_or_404(Proveedor, pk=pk)
    if obj.movimiento_set.exists():
        obj.activo = False  # tiene historial: se archiva y se conservan sus entradas
        obj.save(update_fields=["activo"])
        messages.success(
            request, f"Proveedor «{obj.nombre}» eliminado. Su historial de entradas se conserva."
        )
    else:
        obj.delete()  # los productos asociados quedan sin proveedor
        messages.success(request, f"Proveedor «{obj.nombre}» eliminado.")
    return redirect("proveedores")
