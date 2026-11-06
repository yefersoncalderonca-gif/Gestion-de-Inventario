from django.db import models


class Reporte(models.Model):
    """Registro de cada reporte que se genera o se exporta."""
    tipo = models.CharField(max_length=50)
    fecha_desde = models.DateField(null=True, blank=True)
    fecha_hasta = models.DateField(null=True, blank=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey("usuarios.Usuario", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-fecha_generacion"]

    def __str__(self) -> str:
        return f"{self.tipo} ({self.fecha_generacion:%d/%m/%Y})"
