from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Categoria(models.Model):
    """Agrupa los productos por tipo."""
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


class Producto(models.Model):
    """Artículo del inventario."""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True)
    unidad_medida = models.CharField(max_length=20, default="unidad")
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    precio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=0)
    lote = models.CharField(max_length=30, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    fecha_proxima_recarga = models.DateField(null=True, blank=True)
    categoria = models.ForeignKey("productos.Categoria", on_delete=models.SET_NULL, null=True, blank=True)
    proveedor = models.ForeignKey("proveedores.Proveedor", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["nombre"]
        constraints = [
            # La base de datos rechaza cualquier stock negativo, venga de donde venga.
            models.CheckConstraint(condition=Q(stock__gte=0), name="stock_no_negativo"),
        ]

    def __str__(self) -> str:
        return f"{self.codigo} · {self.nombre}"

    # Nombres que usan las plantillas del frontend
    @property
    def cantidad(self) -> int:
        return self.stock

    @property
    def unidad(self) -> str:
        return self.unidad_medida

    @property
    def precio_venta(self):
        return self.precio

    @property
    def proxima_recarga(self):
        return self.fecha_proxima_recarga

    @property
    def valor_compra(self):
        return self.stock * self.precio_compra

    def esta_bajo_minimo(self) -> bool:
        return self.stock <= self.stock_minimo

    @property
    def bajo_minimo(self) -> bool:
        return self.esta_bajo_minimo()

    @property
    def fecha_clave(self):
        """La fecha más cercana entre el vencimiento y la próxima recarga."""
        fechas = [f for f in (self.fecha_vencimiento, self.fecha_proxima_recarga) if f]
        return min(fechas) if fechas else None

    @property
    def dias_restantes(self):
        f = self.fecha_clave
        return (f - timezone.localdate()).days if f else None

    @property
    def dias_vencimiento(self):
        f = self.fecha_vencimiento
        return (f - timezone.localdate()).days if f else None

    @property
    def dias_recarga(self):
        f = self.fecha_proxima_recarga
        return (f - timezone.localdate()).days if f else None

    @property
    def fecha_texto(self) -> str:
        f = self.fecha_clave
        return f.strftime("%d/%m/%Y") if f else "Sin fecha"

    @property
    def estado(self) -> str:
        d = self.dias_restantes
        if d is not None and d < 0:
            return "Vencido"
        if d is not None and d <= 10:
            return "Urgente"
        if d is not None and d <= 30:
            return "Por vencer"
        if self.bajo_minimo:
            return "Bajo mínimo"
        if d is None:
            return "Sin vencimiento"
        return "Vigente"

    def actualizar_stock(self, cantidad: int) -> None:
        """Suma (o resta, si es negativa) unidades al stock y guarda.

        Usa una expresión F() para que la suma la haga la base de datos:
        así dos operaciones simultáneas no se pisan entre sí.
        """
        Producto.objects.filter(pk=self.pk).update(stock=F("stock") + cantidad)
        self.refresh_from_db(fields=["stock"])
