"""Formulario de proveedores con validación de NIT y teléfono."""

from django import forms

from validaciones import NIT_MAX_CARACTERES, TEL_CELULAR, validar_nit, validar_telefono
from .models import Proveedor


class ProveedorForm(forms.ModelForm):
    """Crea o edita un proveedor; NIT y teléfono son opcionales, pero si se escriben se validan."""

    class Meta:
        """Campos, etiquetas y controles HTML del formulario."""

        model = Proveedor
        fields = ["nombre", "nit", "telefono", "correo", "direccion"]
        labels = {
            "nombre": "Nombre",
            "nit": "NIT",
            "telefono": "Teléfono",
            "correo": "Correo",
            "direccion": "Dirección",
        }
        widgets = {f: forms.TextInput(attrs={"class": "input"}) for f in ("nombre", "direccion")}
        widgets["nit"] = forms.TextInput(
            attrs={"class": "input", "inputmode": "numeric", "data-solo": "nit"}
        )
        widgets["telefono"] = forms.TextInput(
            attrs={"class": "input", "inputmode": "numeric", "data-solo": "digitos"}
        )
        widgets["correo"] = forms.EmailInput(attrs={"class": "input"})

    def __init__(self, *args, **kwargs):
        """Limita lo que se puede escribir en NIT y teléfono.

        Django copia el max_length del modelo al campo y pisaría estos
        límites si se pusieran en Meta.widgets, por eso se fijan aquí.
        """
        super().__init__(*args, **kwargs)
        self.fields["nit"].widget.attrs["maxlength"] = NIT_MAX_CARACTERES
        self.fields["telefono"].widget.attrs["maxlength"] = TEL_CELULAR

    def clean_nit(self):
        """Valida el formato del NIT y que ningún otro proveedor (ni archivado) lo use."""
        nit = (self.cleaned_data.get("nit") or "").strip()
        if not nit:  # en proveedores el NIT es opcional
            return None
        nit = validar_nit(nit)
        if Proveedor.todos.filter(nit=nit).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "Ya existe un proveedor con este NIT (puede estar archivado)."
            )
        return nit

    def clean_telefono(self):
        """Valida el teléfono si se escribió; es un dato opcional."""
        tel = (self.cleaned_data.get("telefono") or "").strip()
        if not tel:  # el telefono es opcional
            return tel
        return validar_telefono(tel)

    def clean_nombre(self) -> str:
        """Evita dos proveedors con el mismo nombre (sin importar mayúsculas).

        Los movimientos buscan al proveedor por su nombre, así que un nombre
        repetido podría asignar una entrada al proveedor equivocado.
        """
        nombre = " ".join((self.cleaned_data.get("nombre") or "").split())
        repetidos = Proveedor.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            repetidos = repetidos.exclude(pk=self.instance.pk)
        if repetidos.exists():
            raise forms.ValidationError(
                f"Ya existe un proveedor llamado «{nombre}». Use otro nombre."
            )
        return nombre
