from django.shortcuts import redirect, render

from .auth import requiere_sesion
from .context import usuario_actual
from .models import Usuario


def login_view(request):
    if usuario_actual(request):
        return redirect("panel")
    ctx = {}
    if request.method == "POST":
        correo = request.POST.get("correo", "").strip()
        clave = request.POST.get("password", "")
        u = Usuario.objects.filter(correo__iexact=correo).first()
        if u and u.iniciar_sesion(correo, clave):
            request.session.flush()
            request.session["usuario_id"] = u.pk
            return redirect("panel")
        # El mismo mensaje para correo y clave: no revela cuál falló.
        ctx = {"error": "Correo o contraseña incorrectos.", "correo": correo}
    return render(request, "login.html", ctx)


def logout_view(request):
    request.session.flush()
    return redirect("login")


@requiere_sesion
def modo_operador(request):
    """El administrador alterna entre su vista y la del operador."""
    if request.usuario.rol == "ADMINISTRADOR":
        request.session["operador"] = not request.session.get("operador", False)
    return redirect("panel")
