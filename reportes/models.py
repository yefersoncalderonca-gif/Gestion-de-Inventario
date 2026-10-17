from django.db import models


class Reporte(models.Model):
    """Reporte generado a partir de los datos del inventario."""
    tipo = models.CharField(max_length=50)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey("usuarios.Usuario", on_delete=models.SET_NULL, null=True, blank=True)

    def generar(self) -> None:
        pass

    def exportar_pdf(self) -> None:
        pass

    def exportar_excel(self) -> None:
        pass
