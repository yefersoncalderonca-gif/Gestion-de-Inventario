from django.db import models


class Cliente(models.Model):
    """Empresa o persona a la que se le venden insumos y se le prestan servicios."""
    nit = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre

    @property
    def siglas(self) -> str:
        palabras = [p for p in self.nombre.replace(".", " ").split() if p[0].isalpha()]
        return "".join(p[0] for p in palabras[:2]).upper()

    @property
    def detalle(self) -> str:
        return self.direccion
