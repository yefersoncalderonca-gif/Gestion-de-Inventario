from django.db import models
from django.utils import timezone


class Movimiento(models.Model):
    """Entrada (compra a proveedor) o salida (venta a cliente) de un producto."""
    TIPOS = [("E", "Entrada"), ("S", "Salida")]

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
        """Guarda el movimiento y actualiza el stock del producto."""
        from django.db import transaction
        with transaction.atomic():
            self.save()
            self.producto.actualizar_stock(self.cantidad if self.tipo == "E" else -self.cantidad)

    @staticmethod
    def consultar_por_producto(producto_id: int):
        return Movimiento.objects.filter(producto_id=producto_id)
