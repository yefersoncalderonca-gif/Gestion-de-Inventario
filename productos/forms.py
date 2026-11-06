from django import forms

from .models import Producto


def _input(**extra):
    return {"class": "input", **extra}


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["codigo", "nombre", "categoria", "proveedor", "unidad_medida", "precio_compra",
                  "precio", "stock", "stock_minimo", "lote", "fecha_vencimiento",
                  "fecha_proxima_recarga", "descripcion"]
        labels = {
            "codigo": "Código", "nombre": "Nombre", "categoria": "Categoría",
            "proveedor": "Proveedor", "unidad_medida": "Unidad de medida",
            "precio_compra": "Precio de compra (COP)", "precio": "Precio de venta (COP)",
            "stock": "Stock inicial", "stock_minimo": "Stock mínimo", "lote": "Lote",
            "fecha_vencimiento": "Fecha de vencimiento",
            "fecha_proxima_recarga": "Próxima recarga", "descripcion": "Descripción",
        }
        help_texts = {
            "codigo": "Único por producto. Ej.: EXT-ABC-10",
            "stock": "Después solo cambia con entradas y salidas.",
            "stock_minimo": "Debajo de este valor se activa la alerta.",
            "fecha_vencimiento": "Déjala vacía si no vence.",
            "fecha_proxima_recarga": "Solo para extintores y similares.",
        }
        widgets = {
            "codigo": forms.TextInput(attrs=_input()),
            "nombre": forms.TextInput(attrs=_input()),
            "categoria": forms.Select(attrs=_input()),
            "proveedor": forms.Select(attrs=_input()),
            "unidad_medida": forms.TextInput(attrs=_input(placeholder="unidad, caja, frasco...")),
            "precio_compra": forms.NumberInput(attrs=_input(min=0, step="1")),
            "precio": forms.NumberInput(attrs=_input(min=0, step="1")),
            "stock": forms.NumberInput(attrs=_input(min=0)),
            "stock_minimo": forms.NumberInput(attrs=_input(min=0)),
            "lote": forms.TextInput(attrs=_input()),
            "fecha_vencimiento": forms.DateInput(attrs=_input(type="date"), format="%Y-%m-%d"),
            "fecha_proxima_recarga": forms.DateInput(attrs=_input(type="date"), format="%Y-%m-%d"),
            "descripcion": forms.TextInput(attrs=_input()),
        }

    # Campos que aparecen por primera vez en la versión 2.0 (etiqueta «Nuevo 2.0»)
    NUEVOS = ("unidad_medida", "precio_compra", "lote", "fecha_vencimiento", "fecha_proxima_recarga")

    def __init__(self, *args, editando=False, **kwargs):
        super().__init__(*args, **kwargs)
        for nombre in self.NUEVOS:
            self.fields[nombre].nuevo = True
        self.fields["categoria"].empty_label = "Seleccione..."
        self.fields["proveedor"].empty_label = "Seleccione..."
        if editando:
            del self.fields["stock"]       # el stock lo cambian los movimientos

    def clean_codigo(self):
        return self.cleaned_data["codigo"].strip().upper()

    def clean(self):
        datos = super().clean()
        for campo in ("precio_compra", "precio", "stock", "stock_minimo"):
            v = datos.get(campo)
            if v is not None and v < 0:
                self.add_error(campo, "No puede ser negativo.")
        return datos
