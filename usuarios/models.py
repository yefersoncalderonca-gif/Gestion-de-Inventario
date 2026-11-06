from django.db import models


class Usuario(models.Model):
    """Persona que accede al sistema (Administrador u Operador)."""
    ROLES = [("ADMINISTRADOR", "Administrador"), ("OPERADOR", "Operador")]

    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=128)
    rol = models.CharField(max_length=20, choices=ROLES, default="OPERADOR")

    def iniciar_sesion(self, correo: str, contrasena: str) -> bool:
        return False

    def cerrar_sesion(self) -> None:
        pass

    def tiene_permiso(self, accion: str) -> bool:
        return False
