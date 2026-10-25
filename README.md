# Sistema de gestión de inventario

Aplicativo para el control de inventarios de una mypime del Huila, desarrollado como proyecto de aula para la empresa MagnusSIS SAS (Neiva, Huila).

## Integrantes

- Yeferson Calderón Camacho
- Carlos Andrés Portela Quesada
- Kevin Mauricio Hernandez Valenzuela
- Juan Sebastian Tobon Alvarez
- Juan José Roso Casanova
- Juan Jose Rodriguez Gomez
- Rafel Salazar Rodriguez
- Fredy Alejandro Olaya Alvarez
- Juan Sebastian Pérez Poveda
- Juan David Narváez Moquera

## Información académica

- Asignatura: Lenguaje de Programación 1 (2026-2)
- Docente: Ing. Juan José Ramos Díaz
- Docente: Ing. Juan Sebastian Parra Sáenz 

## Tecnologías

- Python
- Django
- MySQL

## Cómo ejecutarlo

1. Clonar el repositorio:
   `git clone https://github.com/yefersoncalderonca-gif/Gestion-de-Inventario.git`
2. Entrar a la carpeta del proyecto.
3. Instalar Django:
   `pip install django mysqlclient`
4. Crear la base de datos:
   `python manage.py migrate`
5. Iniciar el servidor:
   `python manage.py runserver`

## Estado del proyecto

En desarrollo (Entrega 3: versión de consola con persistencia).

## Versión de consola (Entregas 2 y 3)

Programa en Python que gestiona el inventario por la terminal, sin Django ni MySQL. Está en el archivo `inventario.py`.

### Cómo ejecutarlo

1. Tener Python 3 instalado.
2. Abrir una terminal en la carpeta del proyecto.
3. Ejecutar:
   `python inventario.py`

### Funciones

1. Agregar producto (nombre, cantidad, precio y fecha de vencimiento opcional)
2. Ver inventario
3. Buscar producto por nombre
4. Actualizar la cantidad de un producto
5. Eliminar producto (con confirmación)
6. Salir

### Persistencia de datos

- Los productos se guardan en el archivo `inventario.json`, en la misma carpeta del programa.
- Al iniciar, el programa busca el archivo. Si existe, carga los productos; si no existe, lo crea vacío sin mostrar errores.
- Cada vez que se agrega, actualiza o elimina un producto, el archivo se guarda automáticamente.
- Si el archivo está vacío o dañado, el programa avisa, guarda una copia como `inventario.json.corrupto` y arranca con un inventario vacío.
- El archivo `inventario.json` no se sube al repositorio (está en el `.gitignore`).

### Validaciones y manejo de errores

- La cantidad debe ser un número entero entre 0 y 1.000.000. No acepta letras, símbolos ni negativos.
- El precio debe ser un número mayor que cero.
- El nombre no puede estar vacío ni repetirse.
- La fecha de vencimiento es opcional y debe tener el formato dd/mm/aaaa con una fecha real.
- Ante un dato inválido, el programa muestra un mensaje de error y vuelve a pedir el dato, sin cerrarse.
- Si se interrumpe la entrada (Ctrl + C), el programa guarda los datos y se cierra sin errores técnicos.
