"""Administradores de modelos compartidos."""

from django.db import models


class ActivosManager(models.Manager):
    """Administrador por defecto: oculta los registros archivados (activo=False)."""

    def get_queryset(self):
        """Devuelve solo los registros activos (no archivados)."""
        return super().get_queryset().filter(activo=True)
