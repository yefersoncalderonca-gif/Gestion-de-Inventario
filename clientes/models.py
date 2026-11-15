"""Modelo de clientes del sistema de inventario."""

from django.db import models

from aula.managers import ActivosManager
from aula.utils import LETRAS_INICIALES


class Cliente(models.Model):
    """Empresa o persona a la que se le venden insumos y se le prestan servicios."""

    nit = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    activo = models.BooleanField(default=True)

    objects = ActivosManager()  # los archivados no aparecen
    todos = models.Manager()  # incluye archivados

    class Meta:
        """Los clientes se listan por nombre."""

        ordering = ["nombre"]

    def __str__(self) -> str:
        """Representa al cliente con su nombre."""
        return self.nombre

    @property
    def siglas(self) -> str:
        """Iniciales de las dos primeras palabras del nombre, para el avatar de la lista."""
        palabras = [p for p in self.nombre.replace(".", " ").split() if p[0].isalpha()]
        return "".join(p[0] for p in palabras[:LETRAS_INICIALES]).upper()

    @property
    def detalle(self) -> str:
        """Texto secundario que muestra la lista de clientes: la dirección."""
        return self.direccion
