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


class FacturaDetalleTests(TestCase):
    """La factura muestra al tercero y los productos, y el comprador solo ve las suyas."""

    def setUp(self):
        """Crea un producto, dos clientes y una venta de la tienda."""
        from clientes.models import Cliente
        from productos.models import Producto
        from usuarios.models import Usuario

        self.producto = Producto.objects.create(
            codigo="EXT-01", nombre="Extintor ABC", precio=95000, precio_compra=60000, stock=10
        )
        self.cliente = Cliente.objects.create(nit="900111222-3", nombre="Colegio San Agustín")
        self.otro = Cliente.objects.create(nit="900333444-5", nombre="Otro Cliente")
        self.usuario = Usuario(nombre="Admin", correo="a@x.co", rol="ADMINISTRADOR")
        self.usuario.establecer_contrasena("clave12345")
        self.usuario.save()
        Movimiento(
            tipo="S",
            cantidad=2,
            motivo="Venta",
            factura="WEB-1",
            producto=self.producto,
            cliente=self.cliente,
            usuario=self.usuario,
        ).registrar()

    def test_registrar_guarda_el_precio_del_momento(self):
        movimiento = Movimiento.objects.get(factura="WEB-1")
        self.assertEqual(movimiento.precio_unitario, 95000)
        self.producto.precio = 120000
        self.producto.save()
        movimiento.refresh_from_db()
        self.assertEqual(movimiento.precio_unitario, 95000)

    def test_armar_factura_calcula_el_total(self):
        from movimientos.facturas import armar_factura

        factura = armar_factura("WEB-1")
        self.assertEqual(factura["total"], 190000)
        self.assertEqual(factura["tercero"], self.cliente)
        self.assertEqual(len(factura["lineas"]), 1)

    def test_un_comprador_no_ve_la_factura_de_otro(self):
        from movimientos.facturas import armar_factura

        self.assertIsNotNone(armar_factura("WEB-1", cliente=self.cliente))
        self.assertIsNone(armar_factura("WEB-1", cliente=self.otro))


class AreaOperadorTests(TestCase):
    """Ventas solo trabaja con salidas y Bodega solo con entradas."""

    def setUp(self):
        """Crea un operador de cada área, un administrador y un producto con stock."""
        from usuarios.models import Usuario

        def crear(nombre, correo, rol, area):
            usuario = Usuario(nombre=nombre, correo=correo, rol=rol, area=area)
            usuario.establecer_contrasena("clave12345")
            usuario.save()
            return usuario

        self.ventas = crear("Ventas", "v@x.co", "OPERADOR", "VENTAS")
        self.bodega = crear("Bodega", "b@x.co", "OPERADOR", "BODEGA")
        self.admin = crear("Admin", "a@x.co", "ADMINISTRADOR", "VENTAS")
        self.producto = Producto.objects.create(codigo="P-1", nombre="Casco", stock=10)
        for tipo in (TIPO_ENTRADA, TIPO_SALIDA):
            Movimiento(
                tipo=tipo, cantidad=1, motivo="Prueba", producto=self.producto, usuario=self.admin
            ).registrar()

    def _entrar(self, usuario):
        """Inicia sesión como el usuario dado."""
        sesion = self.client.session
        sesion["usuario_id"] = usuario.pk
        sesion.save()

    def test_tipos_permitidos_por_area(self):
        self.assertEqual(self.ventas.tipos_movimiento, "S")
        self.assertEqual(self.bodega.tipos_movimiento, "E")
        self.assertEqual(self.admin.tipos_movimiento, "ES")  # el área no limita al administrador

    def test_historial_de_ventas_solo_muestra_salidas(self):
        self._entrar(self.ventas)
        hist = self.client.get("/movimientos/").context["hist"]
        self.assertTrue(hist)
        self.assertTrue(all(m.tipo == TIPO_SALIDA for m in hist))

    def test_historial_de_bodega_solo_muestra_entradas(self):
        self._entrar(self.bodega)
        hist = self.client.get("/movimientos/").context["hist"]
        self.assertTrue(hist)
        self.assertTrue(all(m.tipo == TIPO_ENTRADA for m in hist))

    def test_ventas_no_puede_registrar_entradas(self):
        self._entrar(self.ventas)
        antes = Movimiento.objects.count()
        self.client.post("/movimientos/", {"tipo": "E", "producto": self.producto.pk})
        self.assertEqual(Movimiento.objects.count(), antes)

    def test_ventas_no_abre_facturas_de_compra(self):
        self._entrar(self.ventas)
        compra = Movimiento.objects.get(tipo=TIPO_ENTRADA).factura
        venta = Movimiento.objects.get(tipo=TIPO_SALIDA).factura
        self.assertEqual(self.client.get(f"/facturas/{compra}/").status_code, 404)
        self.assertEqual(self.client.get(f"/facturas/{venta}/").status_code, 200)
