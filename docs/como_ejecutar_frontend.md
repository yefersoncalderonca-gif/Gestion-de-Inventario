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
| Administrador | admin@magnussig.com | demo-admin-2026 |
| Operador | bodega@magnussig.com | demo-bodega-2026 |
| Operador | ventas@magnussig.com | demo-ventas-2026 |

Notas:
- `cargar_demo` solo carga datos si la base está vacía. Para empezar de cero, borrar `db.sqlite3` y repetir `migrate` y `cargar_demo`.
- Los usuarios, productos, proveedores y clientes de ejemplo son los mismos de la base de datos MySQL (`inventario_magnus.sql`).
- El administrador puede usar «Ver como operador»; el operador no puede crear, editar ni eliminar.
- Los reportes se exportan a PDF y Excel (`reportlab` y `openpyxl`, ya incluidos en `requirements.txt`).
