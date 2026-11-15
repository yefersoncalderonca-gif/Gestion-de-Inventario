"""Modelo de usuarios con roles y contraseñas cifradas."""

from django.contrib.auth.hashers import check_password, make_password
from django.db import models

from aula.utils import LETRAS_INICIALES


class Usuario(models.Model):
    """Persona que accede al sistema (Administrador, Operador o Cliente de la tienda)."""

    ROLES = [("ADMINISTRADOR", "Administrador"), ("OPERADOR", "Operador"), ("CLIENTE", "Cliente")]

    AREAS = [
        ("TODAS", "Todas (entradas y salidas)"),
        ("VENTAS", "Ventas (solo salidas)"),
        ("BODEGA", "Bodega (solo entradas)"),
    ]

    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=128)
    rol = models.CharField(max_length=20, choices=ROLES, default="OPERADOR")
    area = models.CharField(max_length=10, choices=AREAS, default="TODAS")
    activo = models.BooleanField(default=True)

    def __str__(self) -> str:
        """Representa al usuario con su nombre."""
        return self.nombre

    def establecer_contrasena(self, texto: str) -> None:
        """Guarda la contraseña cifrada (nunca en texto plano)."""
        self.contrasena = make_password(texto)

    def iniciar_sesion(self, correo: str, contrasena: str) -> bool:
        """Indica si la cuenta está activa y el correo y la contraseña son correctos."""
        return (
            self.activo
            and correo.strip().lower() == self.correo.lower()
            and check_password(contrasena, self.contrasena)
        )

    @property
    def tipos_movimiento(self) -> str:
        """Tipos de movimiento que puede ver y registrar: «E», «S» o «ES».

        Solo el operador de Ventas (salidas) o de Bodega (entradas) queda limitado.
        """
        if self.rol == "OPERADOR" and self.area == "VENTAS":
            return "S"
        if self.rol == "OPERADOR" and self.area == "BODEGA":
            return "E"
        return "ES"

    @property
    def iniciales(self) -> str:
        """Iniciales de las dos primeras palabras del nombre, para el avatar."""
        return "".join(p[0] for p in self.nombre.split()[:LETRAS_INICIALES]).upper()
