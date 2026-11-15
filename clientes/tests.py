"""Pruebas de los formularios de clientes y proveedores (NIT y teléfono)."""

from django.test import SimpleTestCase, TestCase

from clientes.models import Cliente
from proveedores.models import Proveedor

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


class NombresRepetidosTests(TestCase):
    """No se permiten dos clientes ni dos proveedores con el mismo nombre."""

    def test_cliente_con_nombre_repetido_se_rechaza(self):
        Cliente.objects.create(nit="900123456-7", nombre="Colegio San Agustín")
        formulario = ClienteForm(data={"nombre": "  colegio SAN agustín ", "nit": "900765432-1"})
        self.assertFalse(formulario.is_valid())
        self.assertIn("nombre", formulario.errors)

    def test_cliente_puede_conservar_su_propio_nombre_al_editar(self):
        cliente = Cliente.objects.create(nit="900123456-7", nombre="Colegio San Agustín")
        formulario = ClienteForm(
            data={"nombre": "Colegio San Agustín", "nit": "900123456-7"}, instance=cliente
        )
        self.assertNotIn("nombre", formulario.errors)

    def test_proveedor_con_nombre_repetido_se_rechaza(self):
        Proveedor.objects.create(nit="900111222-3", nombre="Extintores del Sur")
        formulario = ProveedorForm(data={"nombre": "EXTINTORES DEL SUR"})
        self.assertFalse(formulario.is_valid())
        self.assertIn("nombre", formulario.errors)
