"""Formulario para registrar entradas y salidas de inventario."""

from django import forms
from django.utils import timezone

from productos.models import Producto

CANTIDAD_MAXIMA = 1_000_000  # unidades máximas por movimiento


class MovimientoForm(forms.Form):
    """Datos de un movimiento: producto, cantidad, fecha, motivo, tercero y observaciones."""

    producto = forms.ModelChoiceField(
        Producto.objects.all(),
        empty_label="Seleccione un producto...",
        widget=forms.Select(attrs={"class": "input"}),
    )
    cantidad = forms.IntegerField(
        min_value=1,
        max_value=CANTIDAD_MAXIMA,
        error_messages={
            "invalid": "Escribe un número entero.",
            "min_value": "Debe ser al menos 1.",
            "max_value": f"No puede ser mayor que {CANTIDAD_MAXIMA}.",
        },
        widget=forms.NumberInput(attrs={"class": "input", "min": 1}),
    )
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={"class": "input", "type": "date"}, format="%Y-%m-%d")
    )
    motivo = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "input", "placeholder": "Compra, venta, devolución..."}
        ),
    )
    tercero = forms.CharField(max_length=150)
    observaciones = forms.CharField(
        required=False, max_length=255, widget=forms.Textarea(attrs={"class": "input", "rows": 3})
    )

    def __init__(self, *args, **kwargs):
        """Carga los productos activos, el texto de cada opción y la fecha de hoy por defecto."""
        super().__init__(*args, **kwargs)
        self.fields["producto"].queryset = Producto.objects.all()
        self.fields["producto"].label_from_instance = (
            lambda p: f"{p.codigo} · {p.nombre} (stock {p.stock} {p.get_unidad_medida_display()})"
        )
        self.fields["fecha"].initial = timezone.localdate()

    def clean_fecha(self):
        """Rechaza fechas futuras."""
        f = self.cleaned_data["fecha"]
        if f > timezone.localdate():
            raise forms.ValidationError("La fecha no puede ser futura.")
        return f

    def clean_motivo(self):
        """Quita espacios sobrantes del motivo."""
        return self.cleaned_data["motivo"].strip()
