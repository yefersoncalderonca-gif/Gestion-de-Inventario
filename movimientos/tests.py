"""Pruebas del registro de movimientos y de la regla "el stock nunca es negativo"."""

from django.db import IntegrityError, transaction
from django.test import TestCase

from productos.models import Producto

from .models import TIPO_ENTRADA, TIPO_SALIDA, Movimiento, StockInsuficienteError, siguiente_factura

STOCK_INICIAL = 6


class RegistrarMovimientoTests(TestCase):
    """Comprueba que registrar() mantiene el stock correcto y consistente."""

    def setUp(self):
        """Crea un producto con stock inicial para cada prueba."""
        self.producto = Producto.objects.create(
            codigo="TEST-001", nombre="Botiquín de prueba", stock=STOCK_INICIAL
        )

    def _movimiento(self, tipo, cantidad):
        """Arma (sin guardar) un movimiento del producto de prueba."""
        return Movimiento(
            tipo=tipo, cantidad=cantidad, motivo="Prueba", factura="FT-0001", producto=self.producto
        )

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


class FacturaAutomaticaTests(TestCase):
    """El número de factura se asigna solo, por serie (FC compras, FV ventas)."""

    def setUp(self):
        """Crea un producto con stock inicial para cada prueba."""
        self.producto = Producto.objects.create(
            codigo="TEST-003", nombre="Casco de prueba", stock=STOCK_INICIAL
        )

    def _registrar(self, tipo, factura=""):
        """Registra un movimiento de una unidad y lo devuelve."""
        movimiento = Movimiento(
            tipo=tipo, cantidad=1, motivo="Prueba", factura=factura, producto=self.producto
        )
        movimiento.registrar()
        return movimiento

    def test_primera_entrada_y_primera_salida_inician_su_serie(self):
        self.assertEqual(self._registrar(TIPO_ENTRADA).factura, "FC-1001")
        self.assertEqual(self._registrar(TIPO_SALIDA).factura, "FV-2001")

    def test_numeracion_es_consecutiva(self):
        primera = self._registrar(TIPO_ENTRADA).factura
        segunda = self._registrar(TIPO_ENTRADA).factura
        self.assertEqual((primera, segunda), ("FC-1001", "FC-1002"))

    def test_continua_despues_del_numero_mas_alto_existente(self):
        self._registrar(TIPO_ENTRADA, factura="FC-1050")
        self.assertEqual(siguiente_factura(TIPO_ENTRADA), "FC-1051")

    def test_una_factura_escrita_a_mano_se_respeta(self):
        self.assertEqual(self._registrar(TIPO_SALIDA, "WEB-1").factura, "WEB-1")
