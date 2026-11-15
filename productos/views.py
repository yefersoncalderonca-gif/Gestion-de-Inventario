"""Vistas de productos: catálogo, alta, edición, archivado y control de stock."""

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from aula.utils import paginar
from usuarios.auth import requiere_sesion, solo_admin

from .forms import ProductoForm
from .models import DIAS_ALERTA, Categoria, Producto

ESTADOS = [
    (e, e)
    for e in ("Vencido", "Urgente", "Por vencer", "Bajo mínimo", "Vigente", "Sin vencimiento")
]


@requiere_sesion
def productos(request):
    """Lista el catálogo (el más reciente primero) con búsqueda y filtro por categoría."""
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("cat", "")
    todos = list(Producto.objects.select_related("categoria"))
    lista = Producto.objects.select_related("categoria").order_by("-id")  # el más reciente primero
    if q:
        lista = lista.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q))
    if cat.isdigit():
        lista = lista.filter(categoria_id=int(cat))
    lista = list(lista)
    return render(
        request,
        "productos.html",
        {
            "activo": "productos",
            "q": q,
            "cat": cat,
            "total": len(todos),
            "unidades": sum(p.stock for p in todos),
            "bajo": [p for p in todos if p.bajo_minimo],
            "n_cat": Categoria.objects.count(),
            "categorias": [(str(c.pk), c.nombre) for c in Categoria.objects.all()],
            "n_filtrados": len(lista),
            "page": paginar(request, lista),
        },
    )


@solo_admin
def producto_nuevo(request):
    """Formulario para crear un producto (solo administrador)."""
    form = ProductoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        p = form.save()
        messages.success(request, f"Producto «{p.nombre}» creado.")
        return redirect("productos")
    return render(request, "producto_form.html", {"activo": "productos", "form": form})


@solo_admin
def producto_editar(request, pk):
    """Formulario para modificar un producto; el stock solo cambia con movimientos."""
    obj = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, instance=obj, editando=True)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Producto «{obj.nombre}» actualizado.")
        return redirect("productos")
    return render(request, "producto_form.html", {"activo": "productos", "form": form, "obj": obj})


@solo_admin
@require_POST
def producto_eliminar(request, pk):
    """Borra el producto, o lo archiva si ya tiene movimientos, para conservar el historial."""
    obj = get_object_or_404(Producto, pk=pk)
    if obj.movimiento_set.exists():
        # Tiene historial: se archiva para no perder los movimientos ni los reportes.
        obj.activo = False
        obj.save(update_fields=["activo"])
        messages.success(
            request,
            f"Producto «{obj.nombre}» eliminado del catálogo. "
            "Su historial de movimientos se conserva.",
        )
    else:
        obj.delete()
        messages.success(request, f"Producto «{obj.nombre}» eliminado.")
    return redirect("productos")


@requiere_sesion
def stock(request):
    """Muestra existencias con alertas de vencimiento, recarga y bajo mínimo, por urgencia."""
    q = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "")
    todos = list(Producto.objects.all())
    vencen = sorted(
        (p for p in todos if p.fecha_vencimiento and p.dias_vencimiento <= DIAS_ALERTA),
        key=lambda p: p.fecha_vencimiento,
    )
    recargas = sorted(
        (p for p in todos if p.fecha_proxima_recarga and p.dias_recarga <= DIAS_ALERTA),
        key=lambda p: p.fecha_proxima_recarga,
    )
    bajo = [p for p in todos if p.bajo_minimo]

    lista = todos
    if q:
        lista = [p for p in lista if q.lower() in p.nombre.lower() or q.lower() in p.codigo.lower()]
    if estado:
        lista = [p for p in lista if p.estado == estado]
    # primero lo más urgente: los que tienen fecha, por días restantes
    lista = sorted(lista, key=lambda p: (p.dias_restantes is None, p.dias_restantes or 0, p.nombre))

    avisos = [
        f"{p.nombre}: {p.estado.lower()}"
        + (f" ({p.dias_restantes} días)." if p.dias_restantes is not None else ".")
        for p in todos
        if p.estado in ("Vencido", "Urgente")
    ]
    return render(
        request,
        "stock.html",
        {
            "activo": "stock",
            "q": q,
            "estado": estado,
            "estados": ESTADOS,
            "total": len(todos),
            "vencen": vencen,
            "recargas": recargas,
            "bajo": bajo,
            "n_filtrados": len(lista),
            "page": paginar(request, lista),
            "avisos": avisos,
        },
    )
