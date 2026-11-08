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
        return validar_nit(self.cleaned_data.get("nit"))

    def clean_telefono(self):
        tel = (self.cleaned_data.get("telefono") or "").strip()
        if not tel:  # el telefono es opcional
            return tel
        return validar_telefono(tel)

    def clean_nombre(self):
        """Evita dos clientes con el mismo nombre (sin importar mayúsculas).

        Los movimientos buscan al cliente por su nombre, así que un nombre
        repetido podría asignar una salida al cliente equivocado.
        """
        nombre = " ".join((self.cleaned_data.get("nombre") or "").split())
        repetidos = Cliente.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            repetidos = repetidos.exclude(pk=self.instance.pk)
        if repetidos.exists():
            raise forms.ValidationError(
                "Ya existe un cliente llamado «%s». Use otro nombre." % nombre)
        return nombre
