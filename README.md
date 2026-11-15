# Sistema de gestión de inventario para mypimes del Huila

Aplicación web para controlar el inventario de una mypime del Huila: productos, existencias, entradas y salidas de mercancía, proveedores, clientes, tienda en línea y reportes. Se desarrolló como proyecto de aula de **Lenguaje de Programación 1 (2026-2)** en la Fundación Escuela Tecnológica de Neiva (FET), para la empresa MagnusSIG SAS (Neiva, Huila). **Versión 1.0.**

## Integrantes

- Yeferson Calderón Camacho
- Carlos Andrés Portela Quesada
- Kevin Mauricio Hernandez Valenzuela
- Juan Sebastian Tobon Alvarez
- Juan José Roso Casanova
- Juan Jose Rodriguez Gomez
- Rafael Salazar Rodriguez
- Juan Sebastian Pérez Poveda
- Jhon Sebastian Scarpeta Diaz
- Fredy Alejandro Olaya Alvarez

Docentes: Ing. Juan José Ramos Díaz e Ing. Juan Sebastian Parra Sáenz.

## Funciones principales

- Inicio de sesión y registro con tres roles: **Administrador**, **Operador** y **Cliente**.
- Productos y categorías (crear, editar y eliminar con borrado lógico).
- Stock con alertas de existencias bajas y productos próximos a vencer.
- Movimientos de entrada y salida con número de factura automático (`FC` para entradas, `FV` para salidas).
- Proveedores y clientes con validación de NIT y teléfono.
- Tienda en línea con carrito de compras para el rol Cliente.
- Reportes en pantalla, con exportación a PDF y Excel.

## Requisitos previos

- Python 3.13 (con `pip`). Se verificó en Windows 11.
- Git, para clonar el repositorio.
- MySQL 8.0 con MySQL Workbench. **Es opcional:** si no se configura, el sistema usa SQLite y funciona igual.

## Dependencias

Todas están en `requirements.txt`:

| Paquete | Uso |
|---|---|
| Django 6.1.1 | Framework web |
| PyMySQL 1.1.1 | Conexión con MySQL |
| cryptography 50.0.2 | Autenticación de MySQL 8 |
| openpyxl 3.1.5 | Reportes en Excel |
| reportlab 5.0.1 | Reportes en PDF |

## Cómo ejecutarlo (con SQLite, sin instalar MySQL)

1. Clonar el repositorio y entrar a la carpeta:
   ```
   git clone https://github.com/yefersoncalderonca-gif/Gestion-de-Inventario.git
   cd Gestion-de-Inventario
   ```
2. Crear y activar el entorno virtual (en Windows):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
   En Linux o macOS, el segundo comando es `source venv/bin/activate`.
3. Instalar las dependencias:
   ```
   python -m pip install -r requirements.txt
   ```
4. Crear las tablas de la base de datos:
   ```
   python manage.py migrate
   ```
5. Cargar los datos de ejemplo (usuarios, productos, proveedores y clientes):
   ```
   python manage.py cargar_demo
   ```
6. Iniciar el servidor:
   ```
   python manage.py runserver
   ```
7. Abrir <http://127.0.0.1:8000> en el navegador.

## Usuarios de demostración

Se crean con `python manage.py cargar_demo`.

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | admin@magnussig.com | admin2026 |
| Operador (bodega) | bodega@magnussig.com | bodega2026 |
| Operador (ventas) | ventas@magnussig.com | ventas2026 |
| Cliente | cliente@magnussig.com | cliente2026 |

## Usar MySQL (opcional)

1. Crear la base de datos en MySQL Workbench:
   ```sql
   CREATE DATABASE inventario_web CHARACTER SET utf8mb4;
   ```
2. En la raíz del proyecto, crear un archivo llamado `.env` con estos datos (ajustar usuario y clave):
   ```
   DB_MOTOR=mysql
   DB_NOMBRE=inventario_web
   DB_USUARIO=root
   DB_CLAVE=su_clave
   DB_HOST=127.0.0.1
   DB_PUERTO=3306
   ```
3. Ejecutar de nuevo los pasos 4, 5 y 6 de la sección anterior. El archivo `.env` no se sube al repositorio.

## Pruebas

```
python manage.py test
```

Ejecuta 38 pruebas automáticas y debe terminar con `OK`. Los casos de prueba manuales están en la carpeta `pruebas/`.

## Estructura del proyecto

| Carpeta o archivo | Contenido |
|---|---|
| `aula/` | Configuración de Django, rutas, panel, tienda y utilidades |
| `usuarios/` | Login, registro, roles y comando `cargar_demo` |
| `productos/` | Productos, categorías y stock |
| `movimientos/` | Entradas, salidas y numeración de facturas |
| `proveedores/`, `clientes/` | Gestión de terceros |
| `reportes/` | Reportes con exportación a PDF y Excel |
| `templates/`, `static/` | Pantallas HTML, estilos, scripts e imágenes |
| `validaciones.py` | Validaciones compartidas (NIT, teléfono) |
| `docs/` | Diagramas, base de datos y prototipos |
| `pruebas/` | Casos de prueba |
| `consola_v0/` | Versión de consola de las Entregas 2 y 3 (histórica) |

## Versión de consola (histórica)

Antes de la versión web se entregó un programa de consola, sin Django ni base de datos. Está en `consola_v0/inventario.py` y se ejecuta con `python consola_v0/inventario.py`. Guarda los datos en `inventario.json`, archivo que no se sube al repositorio.
