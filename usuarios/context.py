from django.utils import timezone

from .models import Usuario


def usuario_actual(request):
    uid = request.session.get("usuario_id")
    return Usuario.objects.filter(pk=uid, activo=True).first() if uid else None


def es_operador(request, usuario=None) -> bool:
    """Operador real, o administrador que activó «Ver como operador»."""
    usuario = usuario or usuario_actual(request)
    return bool(usuario and usuario.rol == "OPERADOR") or bool(request.session.get("operador"))


def sesion(request):
    """Datos que necesita la plantilla base en todas las páginas."""
    u = usuario_actual(request)
    return {
        "hoy": timezone.localdate(),
        "nombre_usuario": u.nombre if u else "",
        "iniciales": u.iniciales if u else "",
        "primer_nombre": u.nombre.split()[0] if u else "",
        "rol": u.get_rol_display() if u else "",
        "operador": es_operador(request, u),
    }
