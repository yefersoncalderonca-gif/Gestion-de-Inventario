"""Administradores de modelos compartidos."""
from django.db import models


class ActivosManager(models.Manager):
    """Administrador por defecto: oculta los registros archivados (activo=False)."""

    def get_queryset(self):
        return super().get_queryset().filter(activo=True)
