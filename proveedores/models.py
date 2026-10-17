from django.db import models


class Proveedor(models.Model):
    """Empresa o persona que suministra productos."""
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=255, blank=True)

    def agregar(self) -> None:
        pass

    def actualizar(self) -> None:
        pass

    def eliminar(self) -> None:
        pass
