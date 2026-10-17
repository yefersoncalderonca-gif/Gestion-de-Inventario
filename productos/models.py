from django.db import models


class Categoria(models.Model):
    """Agrupa los productos por tipo."""
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True)

    def agregar(self) -> None:
        pass

    def actualizar(self) -> None:
        pass

    def eliminar(self) -> None:
        pass


class Producto(models.Model):
    """Artículo del inventario."""
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=0)
    categoria = models.ForeignKey("productos.Categoria", on_delete=models.SET_NULL, null=True, blank=True)
    proveedor = models.ForeignKey("proveedores.Proveedor", on_delete=models.SET_NULL, null=True, blank=True)

    def agregar(self) -> None:
        pass

    def actualizar(self) -> None:
        pass

    def eliminar(self) -> None:
        pass

    def actualizar_stock(self, cantidad: int) -> None:
        pass

    def esta_bajo_minimo(self) -> bool:
        return False
