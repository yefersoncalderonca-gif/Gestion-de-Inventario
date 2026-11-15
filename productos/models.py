"""Modelos de categorías y productos, con cálculo de estado por fechas y stock."""

from django.db import models

from aula.managers import ActivosManager
from django.db.models import F, Q
from django.utils import timezone


class Categoria(models.Model):
    """Agrupa los productos por tipo."""

    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True)

    class Meta:
        """Las categorías se listan por nombre."""

        ordering = ["nombre"]

    def __str__(self) -> str:
        """Representa la categoría con su nombre."""
        return self.nombre


# Días que faltan para la fecha clave a partir de los cuales el producto se marca en alerta.
DIAS_URGENTE = 10
DIAS_ALERTA = 30

UNIDADES_DE_MEDIDA = [
    ("unidad", "Unidad (und)"),
    ("par", "Par"),
    ("kit", "Kit"),
    ("caja", "Caja"),
    ("paquete", "Paquete"),
    ("bolsa", "Bolsa"),
    ("rollo", "Rollo"),
    ("frasco", "Frasco"),
    ("botella", "Botella"),
    ("galon", "Galón (gal)"),
    ("litro", "Litro (L)"),
    ("mililitro", "Mililitro (ml)"),
    ("kilogramo", "Kilogramo (kg)"),
    ("gramo", "Gramo (g)"),
    ("metro", "Metro (m)"),
    ("centimetro", "Centímetro (cm)"),
    ("milimetro", "Milímetro (mm)"),
]


class Producto(models.Model):
    """Artículo del inventario. Si ya tiene movimientos no se borra: se archiva."""

    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True)
    unidad_medida = models.CharField(max_length=20, choices=UNIDADES_DE_MEDIDA, default="unidad")
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    precio = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=0)
    lote = models.CharField(max_length=30, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    fecha_proxima_recarga = models.DateField(null=True, blank=True)
    categoria = models.ForeignKey(
        "productos.Categoria", on_delete=models.SET_NULL, null=True, blank=True
    )
    proveedor = models.ForeignKey(
        "proveedores.Proveedor", on_delete=models.SET_NULL, null=True, blank=True
    )
    activo = models.BooleanField(default=True)

    objects = ActivosManager()  # catálogo visible
    todos = models.Manager()  # incluye archivados

    class Meta:
        """Orden por nombre y restricción de stock no negativo en la base de datos."""

        ordering = ["nombre"]
        constraints = [
            # La base de datos rechaza cualquier stock negativo, venga de donde venga.
            models.CheckConstraint(condition=Q(stock__gte=0), name="stock_no_negativo"),
        ]

    def __str__(self) -> str:
        """Representa el producto con su código y nombre."""
        return f"{self.codigo} · {self.nombre}"

    # Nombres que usan las plantillas del frontend
    @property
    def cantidad(self) -> int:
        """Alias de «stock» para las plantillas."""
        return self.stock

    @property
    def unidad(self) -> str:
        """Alias de «unidad_medida» para las plantillas."""
        return self.unidad_medida

    @property
    def precio_venta(self):
        """Alias de «precio» para las plantillas."""
        return self.precio

    @property
    def proxima_recarga(self):
        """Alias de «fecha_proxima_recarga» para las plantillas."""
        return self.fecha_proxima_recarga

    @property
    def valor_compra(self):
        """Valor del stock a precio de compra."""
        return self.stock * self.precio_compra

    def esta_bajo_minimo(self) -> bool:
        """Indica si el stock llegó al mínimo o quedó por debajo."""
        return self.stock <= self.stock_minimo

    @property
    def bajo_minimo(self) -> bool:
        """Propiedad equivalente a esta_bajo_minimo() para las plantillas."""
        return self.esta_bajo_minimo()

    @property
    def fecha_clave(self):
        """La fecha más cercana entre el vencimiento y la próxima recarga."""
        fechas = [f for f in (self.fecha_vencimiento, self.fecha_proxima_recarga) if f]
        return min(fechas) if fechas else None

    @property
    def dias_restantes(self):
        """Días que faltan para la fecha clave (negativo si ya pasó); None si no tiene fecha."""
        f = self.fecha_clave
        return (f - timezone.localdate()).days if f else None

    @property
    def dias_vencimiento(self):
        """Días que faltan para el vencimiento; None si no vence."""
        f = self.fecha_vencimiento
        return (f - timezone.localdate()).days if f else None

    @property
    def dias_recarga(self):
        """Días que faltan para la próxima recarga; None si no aplica."""
        f = self.fecha_proxima_recarga
        return (f - timezone.localdate()).days if f else None

    @property
    def fecha_texto(self) -> str:
        """Fecha clave en formato dd/mm/aaaa, o «Sin fecha»."""
        f = self.fecha_clave
        return f.strftime("%d/%m/%Y") if f else "Sin fecha"

    @property
    def estado(self) -> str:
        """Clasifica: Vencido, Urgente, Por vencer, Bajo mínimo, Vigente o Sin vencimiento."""
        d = self.dias_restantes
        if d is not None and d < 0:
            return "Vencido"
        if d is not None and d <= DIAS_URGENTE:
            return "Urgente"
        if d is not None and d <= DIAS_ALERTA:
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
