"""Formularios de cuentas: administración de usuarios y registro público de clientes."""

from django import forms

from .models import Usuario

CLAVE_MINIMA = 6  # largo mínimo de la contraseña


def _validar_clave(clave: str) -> str:
    """Verifica el largo mínimo de la contraseña y la devuelve."""
    if len(clave) < CLAVE_MINIMA:
        raise forms.ValidationError(f"La contraseña debe tener al menos {CLAVE_MINIMA} caracteres.")
    return clave


class UsuarioForm(forms.ModelForm):
    """Crea o edita una cuenta (administrador). Al editar, dejar la clave en blanco no la cambia."""

    contrasena_nueva = forms.CharField(
        label="Contraseña",
        required=False,
        widget=forms.PasswordInput(attrs={"class": "input"}, render_value=False),
    )

    class Meta:
        """Campos, etiquetas y controles HTML del formulario."""

        model = Usuario
        fields = ["nombre", "correo", "rol", "activo"]
        labels = {"nombre": "Nombre", "correo": "Correo", "rol": "Rol", "activo": "Cuenta activa"}
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "input"}),
            "correo": forms.EmailInput(attrs={"class": "input"}),
            "rol": forms.Select(attrs={"class": "input"}),
        }

    def __init__(self, *args, **kwargs):
        """La contraseña es obligatoria al crear y opcional al editar."""
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["contrasena_nueva"].required = True
        else:
            self.fields["contrasena_nueva"].label = "Contraseña nueva (opcional)"

    def clean_correo(self):
        """Pone el correo en minúsculas y verifica que no esté repetido."""
        correo = self.cleaned_data["correo"].strip().lower()
        if Usuario.objects.filter(correo__iexact=correo).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return correo

    def clean_contrasena_nueva(self):
        """Valida la contraseña nueva solo si se escribió."""
        clave = self.cleaned_data.get("contrasena_nueva", "")
        return _validar_clave(clave) if clave else clave

    def save(self, commit=True):
        """Guarda la cuenta; cifra la contraseña únicamente si se escribió una nueva."""
        usuario = super().save(commit=False)
        if self.cleaned_data.get("contrasena_nueva"):
            usuario.establecer_contrasena(self.cleaned_data["contrasena_nueva"])
        if commit:
            usuario.save()
        return usuario


class RegistroForm(forms.Form):
    """Autorregistro: solo crea cuentas de rol CLIENTE."""

    nombre = forms.CharField(
        label="Nombre completo",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "input", "autofocus": True}),
    )
    correo = forms.EmailField(label="Correo", widget=forms.EmailInput(attrs={"class": "input"}))
    clave = forms.CharField(
        label="Contraseña", widget=forms.PasswordInput(attrs={"class": "input"})
    )
    repetir = forms.CharField(
        label="Repite la contraseña", widget=forms.PasswordInput(attrs={"class": "input"})
    )

    def clean_correo(self):
        """Pone el correo en minúsculas y verifica que no esté registrado."""
        correo = self.cleaned_data["correo"].strip().lower()
        if Usuario.objects.filter(correo__iexact=correo).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return correo

    def clean_clave(self):
        """Verifica el largo mínimo de la contraseña."""
        return _validar_clave(self.cleaned_data["clave"])

    def clean(self):
        """Comprueba que las dos contraseñas coincidan."""
        datos = super().clean()
        if datos.get("clave") and datos.get("repetir") and datos["clave"] != datos["repetir"]:
            self.add_error("repetir", "Las contraseñas no coinciden.")
        return datos

    def crear(self) -> Usuario:
        """Crea y guarda la cuenta de cliente con la contraseña cifrada."""
        usuario = Usuario(
            nombre=self.cleaned_data["nombre"].strip(),
            correo=self.cleaned_data["correo"],
            rol="CLIENTE",
        )
        usuario.establecer_contrasena(self.cleaned_data["clave"])
        usuario.save()
        return usuario
