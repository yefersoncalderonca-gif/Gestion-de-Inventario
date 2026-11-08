"""Pruebas del registro de movimientos y de la regla "el stock nunca es negativo"."""
from django.db import IntegrityError, transaction
from django.test import TestCase

from productos.models import Producto

from .models import (TIPO_ENTRADA, TIPO_SALIDA, Movimiento,
                     StockInsuficienteError)

STOCK_INICIAL = 6


class RegistrarMovimientoTests(TestCase):
    """Comprueba que registrar() mantiene el stock correcto y consistente."""

    def setUp(self):
        self.producto = Producto.objects.create(
            codigo="TEST-001", nombre="Botiquín de prueba", stock=STOCK_INICIAL)

    def _movimiento(self, tipo, cantidad):
        return Movimiento(tipo=tipo, cantidad=cantidad, motivo="Prueba",
                          factura="FT-0001", producto=self.producto)

    def test_entrada_suma_al_stock(self):
        self._movimiento(TIPO_ENTRADA, 4).registrar()
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, STOCK_INICIAL + 4)

    def test_salida_resta_al_stock(self):
        self._movimiento(TIPO_SALIDA, 2).registrar()
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, STOCK_INICIAL - 2)

    def test_salida_igual_al_stock_deja_cero(self):
        self._movimiento(TIPO_SALIDA, STOCK_INICIAL).registrar()
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 0)

    def test_salida_mayor_al_stock_se_rechaza(self):
        with self.assertRaises(StockInsuficienteError) as contexto:
            self._movimiento(TIPO_SALIDA, STOCK_INICIAL + 1).registrar()
        self.assertEqual(contexto.exception.disponible, STOCK_INICIAL)

    def test_salida_rechazada_no_guarda_nada(self):
        with self.assertRaises(StockInsuficienteError):
            self._movimiento(TIPO_SALIDA, STOCK_INICIAL + 500).registrar()
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, STOCK_INICIAL)
        self.assertEqual(Movimiento.objects.count(), 0)


class RestriccionStockTests(TestCase):
    """La base de datos rechaza un stock negativo aunque se salte registrar()."""

    def test_no_se_puede_guardar_stock_negativo(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Producto.objects.create(codigo="TEST-002", nombre="Negativo", stock=-1)