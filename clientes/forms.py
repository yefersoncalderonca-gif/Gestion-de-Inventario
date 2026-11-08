from django import forms

from validaciones import validar_nit, validar_telefono
from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "nit", "telefono", "correo", "direccion"]
        labels = {"nombre": "Nombre o razón social", "nit": "NIT", "telefono": "Teléfono",
                  "correo": "Correo", "direccion": "Dirección"}
        widgets = {f: forms.TextInput(attrs={"class": "input"}) for f in
                   ("nombre", "nit", "telefono", "direccion")}
        widgets["correo"] = forms.EmailInput(attrs={"class": "input"})

    def clean_nit(self):
        nit = validar_nit(self.cleaned_data.get("nit"))
        if Cliente.todos.filter(nit=nit).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un cliente con este NIT (puede estar archivado).")
        return nit

    def clean_telefono(self):
        tel = (self.cleaned_data.get("telefono") or "").strip()
        if not tel:  # el telefono es opcional
            return tel
        return validar_telefono(tel)
