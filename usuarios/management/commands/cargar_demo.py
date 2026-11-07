"""Carga datos de ejemplo (los mismos de la base de datos MySQL). Uso: python manage.py cargar_demo"""
from datetime import date, timedelta

from django.utils import timezone

from django.core.management.base import BaseCommand
from django.db import transaction

from clientes.models import Cliente
from movimientos.models import Movimiento
from productos.models import Categoria, Producto
from proveedores.models import Proveedor
from reportes.models import Reporte
from usuarios.models import Usuario

USUARIOS = [
    ("Administrador MagnusSIG", "admin@magnussig.com", "demo-admin-2026", "ADMINISTRADOR"),
    ("Operador Bodega", "bodega@magnussig.com", "demo-bodega-2026", "OPERADOR"),
    ("Operador Ventas", "ventas@magnussig.com", "demo-ventas-2026", "OPERADOR"),
]
CATEGORIAS = [
    ("Extintores", "Extintores de distintos agentes y capacidades"),
    ("Botiquines", "Botiquines y reposición de insumos de primeros auxilios"),
    ("Elementos de protección personal", "Cascos, guantes, tapabocas y similares"),
    ("Camillas y transporte", "Camillas rígidas y accesorios de inmovilización"),
    ("Higiene y bioseguridad", "Gel antibacterial, alcohol y desinfectantes"),
]
PROVEEDORES = [
    ("9001234561", "Extintores del Sur S.A.S.", "3101234567", "ventas@extintoressur.com", "Cra. 5 # 12-30, Neiva"),
    ("9006543217", "Distribuidora Médica Huila", "3207654321", "pedidos@dmhuila.com", "Calle 8 # 4-15, Neiva"),
    ("8009876543", "Seguridad Industrial Andina", "3159876543", "contacto@sialandina.com", "Av. Circunvalar # 20-45, Bogotá"),
]
CLIENTES = [
    ("8911800012", "Constructora Surcolombiana Ltda.", "3001112233", "compras@surcolombiana.com"),
    ("9004567890", "Clínica Los Andes S.A.S.", "3012223344", "logistica@clinicalosandes.com"),
    ("9002223335", "Colegio San Agustín", "3023334455", "rectoria@colsanagustin.edu.co"),
]
# código, nombre, descripción, unidad, p.compra, p.venta, mínimo, lote, vence, recarga, categoría, proveedor
PRODUCTOS = [
    ("EXT-ABC-10", "Extintor ABC 10 lb", "Extintor multipropósito polvo químico seco", "unidad", 70000, 95000, 5, "L2026-01", date(2027, 6, 30), date(2027, 1, 15), 0, 0),
    ("EXT-CO2-10", "Extintor CO2 10 lb", "Extintor de dióxido de carbono", "unidad", 150000, 195000, 3, "L2026-02", date(2027, 9, 30), date(2027, 3, 10), 0, 0),
    ("BOT-TA-001", "Botiquín tipo A", "Botiquín para empresas hasta 10 personas", "unidad", 32000, 48000, 8, "L2026-03", date(2026, 12, 15), None, 1, 1),
    ("BOT-TB-001", "Botiquín tipo B", "Botiquín para empresas de 10 a 50 personas", "unidad", 78000, 110000, 4, "L2026-03", date(2027, 2, 28), None, 1, 1),
    ("EPP-CAS-01", "Casco de seguridad", "Casco dieléctrico con barboquejo", "unidad", 21000, 32000, 10, "", None, None, 2, 2),
    ("EPP-GUA-01", "Guantes de nitrilo", "Caja x 100 unidades", "caja", 30000, 48000, 6, "L2026-05", date(2028, 5, 31), None, 2, 2),
    ("EPP-TAP-95", "Tapabocas N95", "Caja x 20 unidades", "caja", 45000, 65000, 10, "L2026-06", date(2027, 11, 30), None, 2, 1),
    ("CAM-RIG-01", "Camilla rígida", "Camilla de polietileno con arnés", "unidad", 150000, 210000, 2, "", None, None, 3, 2),
    ("HIG-GEL-500", "Gel antibacterial 500 ml", "Frasco con dosificador", "frasco", 7000, 12000, 15, "L2026-07", date(2026, 12, 1), None, 4, 1),
]
# tipo, cantidad, fecha, motivo, factura, observación, producto, usuario, tercero
MOVIMIENTOS = [
    ("E", 20, date(2026, 10, 5), "Compra", "FC-1001", "Compra inicial de extintores", 0, 1, 0),
    ("E", 10, date(2026, 10, 5), "Compra", "FC-1001", "", 1, 1, 0),
    ("E", 15, date(2026, 10, 6), "Compra", "FC-1002", "Botiquines tipo A", 2, 1, 1),
    ("E", 8, date(2026, 10, 6), "Compra", "FC-1002", "Botiquines tipo B", 3, 1, 1),
    ("E", 30, date(2026, 10, 7), "Compra", "FC-1003", "Cascos", 4, 1, 2),
    ("E", 12, date(2026, 10, 7), "Compra", "FC-1003", "", 5, 1, 2),
    ("E", 25, date(2026, 10, 8), "Compra", "FC-1004", "", 6, 1, 1),
    ("E", 4, date(2026, 10, 8), "Compra", "FC-1005", "", 7, 1, 2),
    ("E", 40, date(2026, 10, 9), "Compra", "FC-1006", "", 8, 1, 1),
    ("S", 12, date(2026, 10, 12), "Venta", "FV-2001", "Dotación de obra", 0, 2, 0),
    ("S", 20, date(2026, 10, 12), "Venta", "FV-2001", "", 4, 2, 0),
    ("S", 9, date(2026, 10, 14), "Venta", "FV-2002", "Reposición de botiquines", 2, 2, 1),
    ("S", 10, date(2026, 10, 14), "Venta", "FV-2002", "", 6, 2, 1),
    ("S", 35, date(2026, 10, 20), "Venta", "FV-2003", "Campaña de higiene", 8, 2, 2),
]


# Movimientos recientes (días atrás desde hoy), para que el panel y el historial tengan datos vivos
RECIENTES = [
    ("E", 5, 5, "Compra", "FC-1010", "Reposición de tapabocas", 6, 1, 1),
    ("S", 1, 4, "Venta", "FV-2010", "Camilla para brigada", 7, 2, 1),
    ("E", 6, 3, "Compra", "FC-1011", "Extintores", 0, 1, 0),
    ("S", 2, 2, "Venta", "FV-2011", "", 0, 2, 2),
    ("S", 3, 1, "Venta", "FV-2012", "Botiquines tipo B", 3, 2, 0),
    ("E", 10, 1, "Compra", "FC-1012", "Gel antibacterial", 8, 1, 1),
    ("S", 4, 0, "Venta", "FV-2013", "", 6, 2, 2),
    ("E", 5, 0, "Compra", "FC-1013", "Cascos", 4, 1, 2),
]


class Command(BaseCommand):
    help = "Carga usuarios, catálogo, proveedores, clientes, productos y movimientos de ejemplo."

    @transaction.atomic
    def handle(self, *args, **opts):
        if Producto.objects.exists() or Usuario.objects.exists():
            self.stdout.write("Ya hay datos; no se cargó nada. (Borra db.sqlite3 para empezar de cero.)")
            return
        us = []
        for nombre, correo, clave, rol in USUARIOS:
            u = Usuario(nombre=nombre, correo=correo, rol=rol)
            u.establecer_contrasena(clave)
            u.save()
            us.append(u)
        cats = [Categoria.objects.create(nombre=n, descripcion=d) for n, d in CATEGORIAS]
        provs = [Proveedor.objects.create(nit=a, nombre=b, telefono=c, correo=d, direccion=e)
                 for a, b, c, d, e in PROVEEDORES]
        clis = [Cliente.objects.create(nit=a, nombre=b, telefono=c, correo=d) for a, b, c, d in CLIENTES]
        prods = [Producto.objects.create(
            codigo=c, nombre=n, descripcion=d, unidad_medida=u, precio_compra=pc, precio=pv,
            stock=0, stock_minimo=mn, lote=lo, fecha_vencimiento=ve, fecha_proxima_recarga=re,
            categoria=cats[ca], proveedor=provs[pr])
            for c, n, d, u, pc, pv, mn, lo, ve, re, ca, pr in PRODUCTOS]
        for tipo, cant, fecha, motivo, fac, obs, p, u, t in MOVIMIENTOS:
            Movimiento(tipo=tipo, cantidad=cant, fecha=fecha, motivo=motivo, factura=fac,
                       observaciones=obs, producto=prods[p], usuario=us[u],
                       proveedor=provs[t] if tipo == "E" else None,
                       cliente=clis[t] if tipo == "S" else None).registrar()
        hoy = timezone.localdate()
        for tipo, cant, atras, motivo, fac, obs, p, u, t in RECIENTES:
            Movimiento(tipo=tipo, cantidad=cant, fecha=hoy - timedelta(days=atras), motivo=motivo,
                       factura=fac, observaciones=obs, producto=prods[p], usuario=us[u],
                       proveedor=provs[t] if tipo == "E" else None,
                       cliente=clis[t] if tipo == "S" else None).registrar()
        Reporte.objects.create(tipo="Stock actual", usuario=us[0])
        self.stdout.write(self.style.SUCCESS(
            "Datos de ejemplo cargados. Entra con admin@magnussig.com / demo-admin-2026"))
