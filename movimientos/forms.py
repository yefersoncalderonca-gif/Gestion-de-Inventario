from django import forms
from django.utils import timezone

from productos.models import Producto


class MovimientoForm(forms.Form):
    producto = forms.ModelChoiceField(
        Producto.objects.all(), empty_label="Seleccione un producto...",
        widget=forms.Select(attrs={"class": "input"}))
    cantidad = forms.IntegerField(
        min_value=1, max_value=1_000_000,
        error_messages={"invalid": "Escribe un número entero.", "min_value": "Debe ser al menos 1.",
                        "max_value": "No puede ser mayor que 1000000."},
        widget=forms.NumberInput(attrs={"class": "input", "min": 1}))
    fecha = forms.DateField(widget=forms.DateInput(attrs={"class": "input", "type": "date"}, format="%Y-%m-%d"))
    motivo = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"class": "input", "placeholder": "Compra, venta, devolución..."}))
    tercero = forms.CharField(max_length=150)
    factura = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"class": "input", "placeholder": "FC-1010"}))
    observaciones = forms.CharField(
        required=False, max_length=255,
        widget=forms.Textarea(attrs={"class": "input", "rows": 3}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["producto"].queryset = Producto.objects.all()
        self.fields["producto"].label_from_instance = lambda p: f"{p.codigo} · {p.nombre} (stock {p.stock})"
        self.fields["fecha"].initial = timezone.localdate()

    def clean_fecha(self):
        f = self.cleaned_data["fecha"]
        if f > timezone.localdate():
            raise forms.ValidationError("La fecha no puede ser futura.")
        return f

    def clean_motivo(self):
        return self.cleaned_data["motivo"].strip()

    def clean_factura(self):
        return self.cleaned_data["factura"].strip().upper()
