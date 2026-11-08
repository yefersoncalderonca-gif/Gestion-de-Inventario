from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class Usuario(models.Model):
    """Persona que accede al sistema (Administrador, Operador o Cliente de la tienda)."""
    ROLES = [("ADMINISTRADOR", "Administrador"), ("OPERADOR", "Operador"), ("CLIENTE", "Cliente")]

    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=128)
    rol = models.CharField(max_length=20, choices=ROLES, default="OPERADOR")
    activo = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.nombre

    def establecer_contrasena(self, texto: str) -> None:
        """Guarda la contraseña cifrada (nunca en texto plano)."""
        self.contrasena = make_password(texto)

    def iniciar_sesion(self, correo: str, contrasena: str) -> bool:
        return (self.activo
                and correo.strip().lower() == self.correo.lower()
                and check_password(contrasena, self.contrasena))

    @property
    def iniciales(self) -> str:
        return "".join(p[0] for p in self.nombre.split()[:2]).upper()
