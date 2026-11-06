# Base de datos inventario_magnus (MySQL)

Entrega de la asignatura Introducción a la Base de Datos (Ing. Juan Sebastian Parra Sáenz).
Incluye el módulo de inventario y el módulo de servicios SG-SST de MagnusSIG SAS.

| Archivo | Contenido |
|---|---|
| `inventario_magnus.sql` | Script completo: 10 tablas, 2 disparadores, 5 vistas y datos de ejemplo |
| `consultas_inventario_magnus.sql` | 20 consultas de demostración |
| `der_inventario_magnus.png` | Diagrama entidad-relación (notación de Chen) |
| `Entrega_Base_de_Datos_inventario_magnus.pdf` | Documento con modelo relacional, diccionario de datos, normalización y pruebas |

## Cómo ejecutarla en MySQL Workbench
1. Abrir `inventario_magnus.sql` con File → Open SQL Script.
2. Ejecutar todo con Ctrl + Shift + Enter.
3. Abrir `consultas_inventario_magnus.sql` y ejecutar cada consulta con Ctrl + Enter.

Nota: la aplicación Django usa SQLite por ahora; este script es el diseño en MySQL del proyecto.
