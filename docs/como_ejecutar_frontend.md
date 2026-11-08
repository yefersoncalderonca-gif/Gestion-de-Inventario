# Cómo ejecutar el frontend (Django)

Requisitos: Python 3.12 o superior.

```
pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_demo
python manage.py runserver
```

Abrir http://127.0.0.1:8000/ e iniciar sesión con uno de los usuarios de ejemplo:

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | admin@magnussig.com | admin2026 |
| Operador | bodega@magnussig.com | bodega2026 |
| Operador | ventas@magnussig.com | ventas2026 |
| Cliente (tienda) | cliente@magnussig.com | cliente2026 |

Notas:
- `cargar_demo` carga los datos de ejemplo solo si la base está vacía, pero **siempre** crea o restablece las cuentas de la tabla de arriba. Para empezar de cero, borrar `db.sqlite3` y repetir `migrate` y `cargar_demo`.
- El cliente entra a la tienda (`/tienda/`): ve los productos con existencias, compra y cada compra queda como una salida (factura `WEB-...`) que baja el stock. No accede a las pantallas internas.
- Los usuarios, productos, proveedores y clientes de ejemplo son los mismos de la base de datos MySQL (`inventario_magnus.sql`).
- El administrador puede usar «Ver como operador»; el operador no puede crear, editar ni eliminar.
- Los reportes se exportan a PDF y Excel (`reportlab` y `openpyxl`, ya incluidos en `requirements.txt`).
