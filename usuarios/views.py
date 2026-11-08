from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .auth import requiere_sesion, solo_admin
from .context import usuario_actual
from .forms import RegistroForm, UsuarioForm
from .models import Usuario


def _destino(usuario):
    """Pantalla de inicio según el rol: el cliente va a la tienda."""
    return "tienda" if usuario.rol == "CLIENTE" else "panel"


def login_view(request):
    actual = usuario_actual(request)
    if actual:
        return redirect(_destino(actual))
    ctx = {}
    if request.method == "POST":
        correo = request.POST.get("correo", "").strip()
        clave = request.POST.get("password", "")
        u = Usuario.objects.filter(correo__iexact=correo).first()
        if u and u.iniciar_sesion(correo, clave):
            request.session.flush()
            request.session["usuario_id"] = u.pk
            return redirect(_destino(u))
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


def registro(request):
    """Cualquier persona puede crear una cuenta de cliente para comprar en la tienda."""
    if usuario_actual(request):
        return redirect("login")
    form = RegistroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.crear()
        request.session.flush()
        request.session["usuario_id"] = usuario.pk
        return redirect("tienda")
    return render(request, "registro.html", {"form": form})


@solo_admin
def usuarios_lista(request):
    """Lista de cuentas con su rol y estado."""
    return render(request, "usuarios.html", {
        "activo": "usuarios", "cuentas": Usuario.objects.order_by("rol", "nombre")})


def _formulario_usuario(request, obj=None):
    form = UsuarioForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        propia = obj is not None and obj.pk == request.usuario.pk
        if propia and (form.cleaned_data["rol"] != "ADMINISTRADOR" or not form.cleaned_data["activo"]):
            form.add_error(None, "No puedes quitarte el rol de administrador ni desactivar tu propia cuenta.")
        else:
            cuenta = form.save()
            messages.success(request, f"Cuenta de «{cuenta.nombre}» guardada.")
            return redirect("usuarios")
    return render(request, "form_simple.html", {
        "activo": "usuarios", "form": form, "volver": "usuarios",
        "titulo": "Editar usuario" if obj else "Nuevo usuario",
        "sub": "Define el correo, la contraseña y el rol: cada rol entra a su propia interfaz."})


@solo_admin
def usuario_nuevo(request):
    return _formulario_usuario(request)


@solo_admin
def usuario_editar(request, pk):
    return _formulario_usuario(request, get_object_or_404(Usuario, pk=pk))
