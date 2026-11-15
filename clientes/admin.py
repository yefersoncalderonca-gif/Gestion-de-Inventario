"""Registro del modelo Cliente en el sitio de administración de Django."""

from django.contrib import admin

from .models import Cliente

admin.site.register(Cliente)
