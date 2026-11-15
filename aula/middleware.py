"""Evita que el navegador muestre páginas viejas: tras agregar o borrar, se ve el dato actual."""


class SinCacheMiddleware:
    """Añade `Cache-Control: no-store` a las páginas HTML (no a los archivos estáticos)."""

    def __init__(self, get_response):
        """Guarda la siguiente función de la cadena de middleware de Django."""
        self.get_response = get_response

    def __call__(self, request):
        """Atiende la petición y, si la respuesta es HTML, desactiva el caché del navegador."""
        respuesta = self.get_response(request)
        if "text/html" in respuesta.get("Content-Type", ""):
            respuesta["Cache-Control"] = "no-store"
        return respuesta
