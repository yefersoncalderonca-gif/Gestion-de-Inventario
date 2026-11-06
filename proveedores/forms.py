from django import forms

from .models import Proveedor


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ["nombre", "nit", "telefono", "correo", "direccion"]
        labels = {"nombre": "Nombre", "nit": "NIT", "telefono": "Teléfono",
                  "correo": "Correo", "direccion": "Dirección"}
        widgets = {f: forms.TextInput(attrs={"class": "input"}) for f in
                   ("nombre", "nit", "telefono", "direccion")}
        widgets["correo"] = forms.EmailInput(attrs={"class": "input"})

    def clean_nit(self):
        return (self.cleaned_data.get("nit") or "").strip() or None
