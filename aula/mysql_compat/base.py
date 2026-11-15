"""Backend de MySQL que acepta servidores 8.0.

Django 6.1 exige MySQL 8.4 o superior, pero este proyecto solo usa
funciones básicas que existen igual en MySQL 8.0 (el de MySQL Workbench
del equipo). Por eso se omite únicamente la verificación de versión.
"""

from django.db.backends.mysql.base import DatabaseWrapper as MySQLWrapper


class DatabaseWrapper(MySQLWrapper):
    """Igual al backend oficial, sin exigir la versión mínima del servidor."""

    def check_database_version_supported(self):
        """No se valida la versión mínima del servidor MySQL."""
