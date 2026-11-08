from django.db import models

from aula.managers import ActivosManager


class Proveedor(models.Model):
    """Empresa o persona que suministra productos."""
    nit = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    activo = models.BooleanField(default=True)

    objects = ActivosManager()      # los archivados no aparecen
    todos = models.Manager()        # incluye archivados

    class Meta:
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre

    @property
    def siglas(self) -> str:
        palabras = [p for p in self.nombre.replace(".", " ").split() if p[0].isalpha()]
        return "".join(p[0] for p in palabras[:2]).upper()
