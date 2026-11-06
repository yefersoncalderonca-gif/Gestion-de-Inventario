from django.db import models


class Movimiento(models.Model):
    """Entrada o salida de un producto."""
    TIPOS = [("ENTRADA", "Entrada"), ("SALIDA", "Salida")]

    tipo = models.CharField(max_length=10, choices=TIPOS)
    cantidad = models.IntegerField(default=0)
    fecha = models.DateTimeField(auto_now_add=True)
    observacion = models.CharField(max_length=255, blank=True)
    producto = models.ForeignKey("productos.Producto", on_delete=models.CASCADE)
    usuario = models.ForeignKey("usuarios.Usuario", on_delete=models.SET_NULL, null=True, blank=True)

    def registrar(self) -> None:
        pass

    def consultar_por_producto(self, producto_id: int) -> list:
        return []
