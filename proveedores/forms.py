from django import forms

from validaciones import validar_nit, validar_telefono
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
        nit = (self.cleaned_data.get("nit") or "").strip()
        if not nit:  # en proveedores el NIT es opcional
            return None
        return validar_nit(nit)

    def clean_telefono(self):
        tel = (self.cleaned_data.get("telefono") or "").strip()
        if not tel:  # el telefono es opcional
            return tel
        return validar_telefono(tel)
