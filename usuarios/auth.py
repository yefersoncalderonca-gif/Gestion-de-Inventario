from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .context import es_operador, usuario_actual


def requiere_sesion(vista):
    """Solo entra quien inició sesión."""
    @wraps(vista)
    def envuelta(request, *a, **k):
        u = usuario_actual(request)
        if not u:
            request.session.flush()
            return redirect("login")
        request.usuario = u
        return vista(request, *a, **k)
    return envuelta


def solo_admin(vista):
    """Crear, editar y eliminar son solo para el administrador (no en modo operador)."""
    @wraps(vista)
    @requiere_sesion
    def envuelta(request, *a, **k):
        if es_operador(request, request.usuario):
            messages.error(request, "Tu rol de operador no permite esta acción.")
            return redirect("panel")
        return vista(request, *a, **k)
    return envuelta
