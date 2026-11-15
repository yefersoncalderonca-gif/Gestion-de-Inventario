"""Modelo de movimientos de inventario y numeración automática de facturas."""

import re

from django.db import models, transaction
from django.utils import timezone

from productos.models import Producto

TIPO_ENTRADA = "E"
TIPO_SALIDA = "S"

# Numeración automática de facturas: FC-1001 para compras, FV-2001 para ventas.
PREFIJO_FACTURA = {TIPO_ENTRADA: "FC", TIPO_SALIDA: "FV"}
PRIMERA_FACTURA = {TIPO_ENTRADA: 1001, TIPO_SALIDA: 2001}


class StockInsuficienteError(Exception):
    """Se intentó sacar más unidades de las que hay en el inventario."""

    def __init__(self, disponible: int):
        """Guarda las unidades disponibles y arma el mensaje de error."""
        self.disponible = disponible
        super().__init__("Stock insuficiente: solo hay %d unidades." % disponible)


def siguiente_factura(tipo: str) -> str:
    """Devuelve el próximo número de factura libre para el tipo de movimiento.

    Busca el número más alto ya usado con el prefijo del tipo (FC o FV) y le
    suma uno. Si todavía no hay ninguno, parte del primer número de la serie.
    """
    prefijo = PREFIJO_FACTURA[tipo]
    patron = re.compile(rf"^{prefijo}-(\d+)$")
    usadas = Movimiento.objects.filter(factura__startswith=f"{prefijo}-").values_list(
        "factura", flat=True
    )
    numeros = [int(m.group(1)) for m in map(patron.match, usadas) if m]
    ultimo = max(numeros, default=PRIMERA_FACTURA[tipo] - 1)
    return f"{prefijo}-{ultimo + 1}"


class Movimiento(models.Model):
    """Entrada (compra a proveedor) o salida (venta a cliente) de un producto."""

    TIPOS = [(TIPO_ENTRADA, "Entrada"), (TIPO_SALIDA, "Salida")]

    tipo = models.CharField(max_length=1, choices=TIPOS)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateField(default=timezone.localdate)
    motivo = models.CharField(max_length=100)
    factura = models.CharField(max_length=30, blank=True)
    observaciones = models.CharField(max_length=255, blank=True)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    producto = models.ForeignKey("productos.Producto", on_delete=models.PROTECT)
    usuario = models.ForeignKey(
        "usuarios.Usuario", on_delete=models.SET_NULL, null=True, blank=True
    )
    cliente = models.ForeignKey("clientes.Cliente", on_delete=models.PROTECT, null=True, blank=True)
    proveedor = models.ForeignKey(
        "proveedores.Proveedor", on_delete=models.PROTECT, null=True, blank=True
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Los movimientos se listan del más reciente al más antiguo."""

        ordering = ["-fecha", "-id"]

    def __str__(self) -> str:
        """Resume el movimiento: tipo, cantidad y producto."""
        return f"{self.get_tipo_display()} {self.cantidad} x {self.producto.nombre}"

    @property
    def tercero(self) -> str:
        """Nombre del proveedor (entradas) o del cliente (salidas)."""
        t = self.proveedor if self.tipo == "E" else self.cliente
        return t.nombre if t else ""

    @property
    def firmada(self) -> str:
        """Cantidad con signo: «+» para entradas y «−» para salidas."""
        return f"{'+' if self.tipo == 'E' else '−'}{self.cantidad}"

    def registrar(self) -> None:
        """Guarda el movimiento y actualiza el stock del producto.

        Todo ocurre en una transacción: si la salida pide más unidades de las
        que hay, lanza StockInsuficienteError y no se guarda nada. El producto
        se bloquea (select_for_update) para que dos salidas simultáneas no
        puedan dejar el stock en negativo. Si el movimiento no trae número de
        factura, se le asigna el siguiente de su serie (siguiente_factura), y se guarda
        el precio unitario del momento para poder mostrar la factura.
        """
        with transaction.atomic():
            producto = Producto.objects.select_for_update().get(pk=self.producto_id)
            if self.tipo == TIPO_SALIDA and self.cantidad > producto.stock:
                raise StockInsuficienteError(producto.stock)
            if not self.factura:
                self.factura = siguiente_factura(self.tipo)
            if self.precio_unitario is None:  # se guarda el precio del momento para la factura
                self.precio_unitario = (
                    producto.precio if self.tipo == TIPO_SALIDA else producto.precio_compra
                )
            self.save()
            variacion = self.cantidad if self.tipo == TIPO_ENTRADA else -self.cantidad
            producto.actualizar_stock(variacion)
            self.producto = producto
