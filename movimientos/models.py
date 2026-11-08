from django.db import models, transaction
from django.utils import timezone

from productos.models import Producto

TIPO_ENTRADA = "E"
TIPO_SALIDA = "S"


class StockInsuficienteError(Exception):
    """Se intentó sacar más unidades de las que hay en el inventario."""

    def __init__(self, disponible: int):
        self.disponible = disponible
        super().__init__("Stock insuficiente: solo hay %d unidades." % disponible)


class Movimiento(models.Model):
    """Entrada (compra a proveedor) o salida (venta a cliente) de un producto."""
    TIPOS = [(TIPO_ENTRADA, "Entrada"), (TIPO_SALIDA, "Salida")]

    tipo = models.CharField(max_length=1, choices=TIPOS)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateField(default=timezone.localdate)
    motivo = models.CharField(max_length=100)
    factura = models.CharField(max_length=30)
    observaciones = models.CharField(max_length=255, blank=True)
    producto = models.ForeignKey("productos.Producto", on_delete=models.PROTECT)
    usuario = models.ForeignKey("usuarios.Usuario", on_delete=models.SET_NULL, null=True, blank=True)
    cliente = models.ForeignKey("clientes.Cliente", on_delete=models.PROTECT, null=True, blank=True)
    proveedor = models.ForeignKey("proveedores.Proveedor", on_delete=models.PROTECT, null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-id"]

    def __str__(self) -> str:
        return f"{self.get_tipo_display()} {self.cantidad} x {self.producto.nombre}"

    @property
    def tercero(self) -> str:
        t = self.proveedor if self.tipo == "E" else self.cliente
        return t.nombre if t else ""

    @property
    def firmada(self) -> str:
        return f"{'+' if self.tipo == 'E' else '−'}{self.cantidad}"

    def registrar(self) -> None:
        """Guarda el movimiento y actualiza el stock del producto.

        Todo ocurre en una transacción: si la salida pide más unidades de las
        que hay, lanza StockInsuficienteError y no se guarda nada. El producto
        se bloquea (select_for_update) para que dos salidas simultáneas no
        puedan dejar el stock en negativo.
        """
        with transaction.atomic():
            producto = Producto.objects.select_for_update().get(pk=self.producto_id)
            if self.tipo == TIPO_SALIDA and self.cantidad > producto.stock:
                raise StockInsuficienteError(producto.stock)
            self.save()
            variacion = self.cantidad if self.tipo == TIPO_ENTRADA else -self.cantidad
            producto.actualizar_stock(variacion)
            self.producto = producto

    @staticmethod
    def consultar_por_producto(producto_id: int):
        return Movimiento.objects.filter(producto_id=producto_id)
