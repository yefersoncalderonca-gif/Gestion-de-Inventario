"""Pruebas de los formularios de clientes y proveedores (NIT y teléfono)."""

from django.test import SimpleTestCase

from clientes.forms import ClienteForm
from proveedores.forms import ProveedorForm
from validaciones import NIT_MAX_CARACTERES, TEL_CELULAR


class LimitesDeEscrituraTests(SimpleTestCase):
    """Los campos de NIT y teléfono limitan lo que el usuario puede escribir."""

    def test_telefono_admite_maximo_diez_caracteres(self):
        for formulario in (ClienteForm(), ProveedorForm()):
            atributos = formulario.fields["telefono"].widget.attrs
            self.assertEqual(atributos["maxlength"], TEL_CELULAR)
            self.assertEqual(atributos["data-solo"], "digitos")

    def test_nit_admite_nueve_digitos_guion_y_verificacion(self):
        for formulario in (ClienteForm(), ProveedorForm()):
            atributos = formulario.fields["nit"].widget.attrs
            self.assertEqual(atributos["maxlength"], NIT_MAX_CARACTERES)
            self.assertEqual(atributos["data-solo"], "nit")
