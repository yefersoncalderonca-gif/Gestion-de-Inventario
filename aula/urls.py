"""Rutas de MagnusSIG. Cada nombre coincide con los `{% url '...' %}` de las plantillas."""
from django.contrib import admin
from django.urls import path

from clientes import views as clientes
from movimientos import views as movimientos
from productos import views as productos
from proveedores import views as proveedores
from reportes import views as reportes
from usuarios import views as usuarios

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', usuarios.login_view, name='login'),
    path('salir/', usuarios.logout_view, name='logout'),
    path('modo-operador/', usuarios.modo_operador, name='modo_operador'),
    path('panel/', views.panel, name='panel'),

    path('productos/', productos.productos, name='productos'),
    path('productos/nuevo/', productos.producto_nuevo, name='producto_nuevo'),
    path('productos/<int:pk>/editar/', productos.producto_editar, name='producto_editar'),
    path('productos/<int:pk>/eliminar/', productos.producto_eliminar, name='producto_eliminar'),
    path('stock/', productos.stock, name='stock'),

    path('movimientos/', movimientos.movimientos, name='movimientos'),
    path('movimientos/terceros/', movimientos.terceros, name='movimientos_terceros'),

    path('proveedores/', proveedores.proveedores, name='proveedores'),
    path('proveedores/nuevo/', proveedores.proveedor_nuevo, name='proveedor_nuevo'),
    path('proveedores/<int:pk>/editar/', proveedores.proveedor_editar, name='proveedor_editar'),
    path('proveedores/<int:pk>/eliminar/', proveedores.proveedor_eliminar, name='proveedor_eliminar'),

    path('clientes/', clientes.clientes, name='clientes'),
    path('clientes/nuevo/', clientes.cliente_nuevo, name='cliente_nuevo'),
    path('clientes/<int:pk>/editar/', clientes.cliente_editar, name='cliente_editar'),

    path('reportes/', reportes.reportes, name='reportes'),
]
