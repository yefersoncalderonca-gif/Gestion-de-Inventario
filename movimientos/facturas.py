"""Arma los datos de una factura a partir de los movimientos que comparten su número."""

from decimal import Decimal

from .models import TIPO_SALIDA, Movimiento


def armar_factura(numero: str, cliente=None):
    """Devuelve un diccionario con la factura `numero`, o None si no existe.

    Si se indica `cliente`, solo se consideran las salidas de ese cliente (así un
    comprador únicamente puede ver sus propias facturas). Cada línea trae el
    precio unitario guardado en el movimiento; en movimientos antiguos, que no lo
    guardaron, se usa el precio actual del producto.
    """
    movimientos = Movimiento.objects.filter(factura=numero).select_related(
        "producto", "cliente", "proveedor", "usuario"
    )
    if cliente is not None:
        movimientos = movimientos.filter(tipo=TIPO_SALIDA, cliente=cliente)
    movimientos = list(movimientos.order_by("id"))
    if not movimientos:
        return None
    primero = movimientos[0]
    es_venta = primero.tipo == TIPO_SALIDA
    lineas = []
    total = Decimal(0)
    for mov in movimientos:
        precio = mov.precio_unitario
        if precio is None:
            precio = mov.producto.precio if es_venta else mov.producto.precio_compra
        subtotal = precio * mov.cantidad
        total += subtotal
        lineas.append(
            {
                "producto": mov.producto,
                "cantidad": mov.cantidad,
                "precio": precio,
                "subtotal": subtotal,
            }
        )
    return {
        "numero": numero,
        "es_venta": es_venta,
        "fecha": primero.fecha,
        "tercero": primero.cliente if es_venta else primero.proveedor,
        "atendido_por": primero.usuario,
        "motivo": primero.motivo,
        "lineas": lineas,
        "total": total,
    }
