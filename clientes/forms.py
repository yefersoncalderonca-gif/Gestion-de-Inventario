from django import forms

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
