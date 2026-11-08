"""Tienda para clientes: catálogo, carrito y compra. Cada compra queda como salidas de inventario."""
from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from clientes.models import Cliente
from movimientos.models import Movimiento
from productos.models import Categoria, Producto
from usuarios.auth import requiere_cliente

CANTIDAD_MAXIMA = 1_000_000          # mismo tope que el formulario de movimientos
NIT_BASE_WEB = 9_000_000_000         # NIT provisional de clientes creados desde la tienda
COMPRAS_RECIENTES = 10               # filas que se muestran en "Mis compras"
CLAVE_CARRITO = "carrito"            # en la sesión: {id_producto: cantidad}


def _cliente_de(usuario) -> Cliente:
    """Cliente comercial del usuario (se busca por correo; si no existe, se crea)."""
    cliente = Cliente.objects.filter(correo__iexact=usuario.correo).first()
    if cliente is None:
        cliente = Cliente.objects.create(
            nit=str(NIT_BASE_WEB + usuario.pk), nombre=usuario.nombre, correo=usuario.correo)
    return cliente


def _leer_cantidad(valor):
    """Convierte a entero entre 1 y CANTIDAD_MAXIMA; devuelve None si no es válida."""
    try:
        cantidad = int(valor)
    except (TypeError, ValueError):
        return None
    return cantidad if 1 <= cantidad <= CANTIDAD_MAXIMA else None


def _carrito(request) -> dict:
    return request.session.setdefault(CLAVE_CARRITO, {})


def _lineas(request):
    """Líneas del carrito con producto, cantidad y subtotal; descarta productos que ya no existen."""
    carrito = _carrito(request)
    productos = Producto.objects.in_bulk([int(pk) for pk in carrito])
    lineas = []
    for pk, cantidad in list(carrito.items()):
        producto = productos.get(int(pk))
        if producto is None:
            carrito.pop(pk)
            request.session.modified = True
            continue
        lineas.append({"producto": producto, "cantidad": cantidad,
                       "subtotal": producto.precio * cantidad, "excede": cantidad > producto.stock})
    return lineas


def _contexto_base(request):
    return {"items_carrito": sum(_carrito(request).values())}


@requiere_cliente
def tienda(request):
    """Catálogo con productos disponibles y compras recientes del cliente."""
    texto = request.GET.get("q", "").strip()
    categoria = request.GET.get("categoria", "")
    productos = Producto.objects.filter(stock__gt=0).select_related("categoria")
    if texto:
        productos = productos.filter(nombre__icontains=texto) | productos.filter(codigo__icontains=texto)
    if categoria.isdigit():
        productos = productos.filter(categoria_id=int(categoria))
    compras = (Movimiento.objects.filter(tipo="S", cliente=_cliente_de(request.usuario),
                                         factura__startswith="WEB-").select_related("producto")[:COMPRAS_RECIENTES])
    return render(request, "tienda.html", {
        **_contexto_base(request), "productos": productos.order_by("nombre"),
        "categorias": Categoria.objects.all(), "q": texto, "categoria": categoria, "compras": compras,
    })


@requiere_cliente
@require_POST
def agregar(request):
    """Suma la cantidad pedida al carrito sin pasar del stock disponible."""
    cantidad = _leer_cantidad(request.POST.get("cantidad"))
    pk = request.POST.get("producto", "")
    producto = Producto.objects.filter(pk=int(pk)).first() if pk.isdigit() else None
    if cantidad is None:
        messages.error(request, "Escribe una cantidad válida (número entero, mínimo 1).")
    elif producto is None:
        messages.error(request, "Ese producto ya no está disponible.")
    else:
        carrito = _carrito(request)
        nueva = carrito.get(str(producto.pk), 0) + cantidad
        if nueva > producto.stock:
            messages.error(request, f"Stock insuficiente: solo hay {producto.stock} unidades de {producto.nombre}.")
        else:
            carrito[str(producto.pk)] = nueva
            request.session.modified = True
            messages.success(request, f"Agregado al carrito: {cantidad} × {producto.nombre}.")
    return redirect(request.POST.get("volver") or "tienda")


@requiere_cliente
def carrito(request):
    """Muestra las líneas del carrito y el total a pagar."""
    lineas = _lineas(request)
    total = sum((l["subtotal"] for l in lineas), Decimal(0))
    return render(request, "carrito.html", {
        **_contexto_base(request), "lineas": lineas, "total": total,
        "hay_exceso": any(l["excede"] for l in lineas)})


@requiere_cliente
@require_POST
def quitar(request):
    """Elimina un producto del carrito."""
    _carrito(request).pop(request.POST.get("producto", ""), None)
    request.session.modified = True
    return redirect("carrito")


@requiere_cliente
@require_POST
def actualizar(request):
    """Cambia la cantidad de una línea del carrito."""
    cantidad = _leer_cantidad(request.POST.get("cantidad"))
    pk = request.POST.get("producto", "")
    producto = Producto.objects.filter(pk=int(pk)).first() if pk.isdigit() else None
    if cantidad is None or producto is None:
        messages.error(request, "Cantidad no válida.")
    elif cantidad > producto.stock:
        messages.error(request, f"Stock insuficiente: solo hay {producto.stock} unidades de {producto.nombre}.")
    else:
        _carrito(request)[str(producto.pk)] = cantidad
        request.session.modified = True
    return redirect("carrito")


@requiere_cliente
@require_POST
def confirmar(request):
    """Registra una salida por cada línea; todo o nada. El stock baja con `registrar()`."""
    lineas = _lineas(request)
    if not lineas:
        messages.error(request, "Tu carrito está vacío.")
        return redirect("tienda")
    ahora = timezone.localtime()
    factura = f"WEB-{ahora:%Y%m%d%H%M%S}"
    cliente = _cliente_de(request.usuario)
    with transaction.atomic():
        total = Decimal(0)
        for linea in lineas:
            producto = Producto.objects.select_for_update().get(pk=linea["producto"].pk)
            if linea["cantidad"] > producto.stock:
                messages.error(request, f"Stock insuficiente: solo hay {producto.stock} unidades de "
                                        f"{producto.nombre}. Ajusta tu carrito.")
                return redirect("carrito")
            Movimiento(tipo="S", cantidad=linea["cantidad"], fecha=ahora.date(), motivo="Venta en tienda",
                       factura=factura, producto=producto, usuario=request.usuario, cliente=cliente).registrar()
            total += producto.precio * linea["cantidad"]
    request.session[CLAVE_CARRITO] = {}
    messages.success(request, f"Compra realizada (factura {factura}). Total pagado: ${total:,.0f}".replace(",", "."))
    return redirect("tienda")
