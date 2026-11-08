"""Pruebas de acceso por rol y de la tienda del cliente."""
from django.core.management import call_command
from django.test import TestCase

from movimientos.models import Movimiento
from productos.models import Producto

CLAVES = {
    "admin@magnussig.com": ("admin2026", "panel"),
    "bodega@magnussig.com": ("bodega2026", "panel"),
    "cliente@magnussig.com": ("cliente2026", "tienda"),
}


class AccesoPorRolTests(TestCase):
    def setUp(self):
        call_command("cargar_demo", verbosity=0)

    def test_cada_cuenta_entra_a_su_pantalla(self):
        for correo, (clave, destino) in CLAVES.items():
            r = self.client.post("/", {"correo": correo, "password": clave})
            self.assertRedirects(r, f"/{destino}/", fetch_redirect_response=False)
            self.client.get("/salir/")

    def test_cargar_demo_restablece_claves_si_ya_hay_datos(self):
        from usuarios.models import Usuario
        u = Usuario.objects.get(correo="admin@magnussig.com")
        u.establecer_contrasena("otra-clave")
        u.save()
        call_command("cargar_demo", verbosity=0)
        r = self.client.post("/", {"correo": "admin@magnussig.com", "password": "admin2026"})
        self.assertRedirects(r, "/panel/", fetch_redirect_response=False)

    def test_cliente_no_entra_al_sistema_interno(self):
        self.client.post("/", {"correo": "cliente@magnussig.com", "password": "cliente2026"})
        for ruta in ("/panel/", "/productos/", "/movimientos/", "/reportes/"):
            self.assertRedirects(self.client.get(ruta), "/tienda/", fetch_redirect_response=False)

    def test_staff_no_entra_a_la_tienda(self):
        self.client.post("/", {"correo": "admin@magnussig.com", "password": "admin2026"})
        self.assertRedirects(self.client.get("/tienda/"), "/panel/", fetch_redirect_response=False)


class TiendaTests(TestCase):
    def setUp(self):
        call_command("cargar_demo", verbosity=0)
        self.client.post("/", {"correo": "cliente@magnussig.com", "password": "cliente2026"})
        self.producto = Producto.objects.filter(stock__gt=3).first()

    def agregar(self, cantidad):
        return self.client.post("/tienda/agregar/", {"producto": self.producto.pk, "cantidad": cantidad})

    def test_agregar_no_baja_stock_hasta_confirmar(self):
        antes = self.producto.stock
        self.agregar(2)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, antes)
        self.assertContains(self.client.get("/tienda/carrito/"), "Total a pagar")

    def test_confirmar_baja_stock_y_registra_salida(self):
        antes = self.producto.stock
        self.agregar(2)
        self.client.post("/tienda/carrito/confirmar/")
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, antes - 2)
        self.assertTrue(Movimiento.objects.filter(tipo="S", factura__startswith="WEB-", cantidad=2).exists())
        self.assertNotContains(self.client.get("/tienda/carrito/"), "Confirmar compra")

    def test_rechaza_mas_que_el_stock_o_cantidad_invalida(self):
        for malo in (self.producto.stock + 1, "0", "-3", "abc", ""):
            self.agregar(malo)
        self.assertNotContains(self.client.get("/tienda/carrito/"), "Total a pagar")


class ProductoArchivadoTests(TestCase):
    def setUp(self):
        call_command("cargar_demo", verbosity=0)
        self.client.post("/", {"correo": "admin@magnussig.com", "password": "admin2026"})

    def test_eliminar_producto_con_movimientos_lo_archiva(self):
        p = Producto.objects.first()
        self.client.post(f"/productos/{p.pk}/eliminar/")
        self.assertFalse(Producto.objects.filter(pk=p.pk).exists())
        self.assertTrue(Producto.todos.filter(pk=p.pk, activo=False).exists())
        self.assertTrue(Movimiento.objects.filter(producto_id=p.pk).exists())
        self.assertNotContains(self.client.get("/productos/"), p.codigo)

    def test_no_permite_reusar_codigo_archivado(self):
        p = Producto.objects.first()
        self.client.post(f"/productos/{p.pk}/eliminar/")
        r = self.client.post("/productos/nuevo/", {"codigo": p.codigo, "nombre": "Otro"})
        self.assertContains(r, "Ya existe un producto con este código")


class GestionDeUsuariosTests(TestCase):
    def setUp(self):
        call_command("cargar_demo", verbosity=0)

    def entrar(self, correo, clave):
        self.client.post("/", {"correo": correo, "password": clave})

    def test_registro_crea_cliente_y_entra_a_la_tienda(self):
        r = self.client.post("/registro/", {"nombre": "Ana Pérez", "correo": "ana@correo.com",
                                            "clave": "secreta1", "repetir": "secreta1"})
        self.assertRedirects(r, "/tienda/", fetch_redirect_response=False)
        from usuarios.models import Usuario
        self.assertEqual(Usuario.objects.get(correo="ana@correo.com").rol, "CLIENTE")

    def test_registro_rechaza_claves_distintas_o_cortas_y_correo_repetido(self):
        for datos in ({"clave": "abc12345", "repetir": "otra"}, {"clave": "ab", "repetir": "ab"},
                      {"clave": "secreta1", "repetir": "secreta1", "correo": "admin@magnussig.com"}):
            base = {"nombre": "X", "correo": "x@correo.com"}
            r = self.client.post("/registro/", {**base, **datos})
            self.assertEqual(r.status_code, 200)

    def test_admin_crea_operador_que_entra_al_panel(self):
        self.entrar("admin@magnussig.com", "admin2026")
        self.client.post("/usuarios/nuevo/", {"nombre": "Op Nuevo", "correo": "nuevo@magnussig.com",
                                              "rol": "OPERADOR", "activo": "on", "contrasena_nueva": "nuevo123"})
        self.client.get("/salir/")
        r = self.client.post("/", {"correo": "nuevo@magnussig.com", "password": "nuevo123"})
        self.assertRedirects(r, "/panel/", fetch_redirect_response=False)

    def test_solo_el_admin_ve_usuarios(self):
        self.entrar("bodega@magnussig.com", "bodega2026")
        self.assertRedirects(self.client.get("/usuarios/"), "/panel/", fetch_redirect_response=False)

    def test_admin_no_puede_desactivarse_a_si_mismo(self):
        self.entrar("admin@magnussig.com", "admin2026")
        from usuarios.models import Usuario
        yo = Usuario.objects.get(correo="admin@magnussig.com")
        r = self.client.post(f"/usuarios/{yo.pk}/editar/", {"nombre": yo.nombre, "correo": yo.correo, "rol": "ADMINISTRADOR"})
        self.assertContains(r, "No puedes quitarte")
        yo.refresh_from_db()
        self.assertTrue(yo.activo)


class ArchivarTercerosTests(TestCase):
    def setUp(self):
        call_command("cargar_demo", verbosity=0)
        self.client.post("/", {"correo": "admin@magnussig.com", "password": "admin2026"})

    def test_cliente_con_movimientos_se_archiva_y_desaparece_de_la_lista(self):
        from clientes.models import Cliente
        c = Cliente.objects.filter(movimiento__isnull=False).first()
        self.client.post(f"/clientes/{c.pk}/eliminar/")
        self.assertFalse(Cliente.objects.filter(pk=c.pk).exists())
        self.assertTrue(Cliente.todos.filter(pk=c.pk, activo=False).exists())
        self.assertTrue(Movimiento.objects.filter(cliente_id=c.pk).exists())

    def test_proveedor_con_entradas_se_archiva(self):
        from proveedores.models import Proveedor
        p = Proveedor.objects.filter(movimiento__isnull=False).first()
        self.client.post(f"/proveedores/{p.pk}/eliminar/")
        self.assertFalse(Proveedor.objects.filter(pk=p.pk).exists())
        self.assertTrue(Movimiento.objects.filter(proveedor_id=p.pk).exists())


class PanelPorRolTests(TestCase):
    def setUp(self):
        call_command("cargar_demo", verbosity=0)

    def test_operador_no_ve_el_boton_de_cambiar_a_administrador(self):
        self.client.post("/", {"correo": "bodega@magnussig.com", "password": "bodega2026"})
        self.assertNotContains(self.client.get("/panel/"), "Volver a administrador")
        self.assertNotContains(self.client.get("/panel/"), "Ver como operador")

    def test_administrador_si_puede_ver_como_operador(self):
        self.client.post("/", {"correo": "admin@magnussig.com", "password": "admin2026"})
        self.assertContains(self.client.get("/panel/"), "Ver como operador")
