"""
Sistema de Gestión de Inventario por Consola (MVP)
Proyecto de aula: Sistema de gestión de inventario para mypime del Huila (MagnusSIS SAS)

Qué hace el programa:
  - Guarda los productos en memoria (una lista de diccionarios).
  - Permite agregar un producto, ver todo el inventario y buscar un producto por nombre.
  - Muestra un menú que se repite hasta que el usuario elige "Salir".

Nota: es un MVP. No guarda datos en archivos ni en una base de datos.
Solo valida que la cantidad y el precio sean números.
"""


# ---------------------------------------------------------------------------
# Funciones del sistema
# ---------------------------------------------------------------------------

def agregar_producto(inventario):
    """Pide los datos de un producto y lo agrega al inventario (lista en memoria)."""
    print("\n--- AGREGAR PRODUCTO ---")
    nombre = input("Nombre del producto: ")

    # Ciclo while: repite la pregunta hasta que el usuario escriba un número entero
    cantidad = None
    while cantidad is None:
        try:
            cantidad = int(input("Cantidad en stock: "))
        except ValueError:
            print("Error: escriba solo números enteros (ejemplo: 10).")

    # Lo mismo para el precio, que puede tener decimales
    precio = None
    while precio is None:
        try:
            precio = float(input("Precio unitario: "))
        except ValueError:
            print("Error: escriba solo números (ejemplo: 25000).")

    # Cada producto es un diccionario con tres propiedades
    producto = {
        "nombre": nombre,
        "cantidad": cantidad,
        "precio": precio,
    }
    inventario.append(producto)
    print("Producto '" + nombre + "' agregado correctamente.")


def mostrar_inventario(inventario):
    """Recorre el inventario con un ciclo for y muestra todos los productos."""
    print("\n--- INVENTARIO ACTUAL ---")

    # Condicional: si la lista está vacía se muestra un mensaje especial
    if len(inventario) == 0:
        print("El inventario está vacío. Agregue productos primero.")
    else:
        numero = 1
        for producto in inventario:
            print(str(numero) + ". " + producto["nombre"]
                  + " | Cantidad: " + str(producto["cantidad"])
                  + " | Precio: $" + str(producto["precio"]))
            numero = numero + 1
        print("Total de productos registrados: " + str(len(inventario)))


def buscar_producto(inventario):
    """Busca un producto por su nombre y muestra el resultado."""
    print("\n--- BUSCAR PRODUCTO ---")

    if len(inventario) == 0:
        print("El inventario está vacío. No hay nada que buscar.")
        return

    nombre_buscado = input("Nombre del producto a buscar: ")
    encontrado = False

    # Ciclo for para recorrer el inventario y comparar nombres
    for producto in inventario:
        if producto["nombre"].lower() == nombre_buscado.lower():
            print("Producto encontrado:")
            print("  Nombre:   " + producto["nombre"])
            print("  Cantidad: " + str(producto["cantidad"]))
            print("  Precio:   $" + str(producto["precio"]))
            encontrado = True

    # Condicional: se evalúa el resultado de la búsqueda
    if not encontrado:
        print("No se encontró ningún producto llamado '" + nombre_buscado + "'.")


def mostrar_menu():
    """Imprime las opciones del menú principal."""
    print("\n========== SISTEMA DE INVENTARIO ==========")
    print("1. Agregar producto")
    print("2. Ver inventario")
    print("3. Buscar producto")
    print("4. Salir")


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

def main():
    inventario = []   # estructura de datos en memoria (RAM): lista de diccionarios
    opcion = ""

    # Ciclo while: el menú se repite hasta que el usuario elija "4. Salir"
    while opcion != "4":
        mostrar_menu()
        opcion = input("Seleccione una opción: ")

        # Condicionales: controlan la navegación del menú
        if opcion == "1":
            agregar_producto(inventario)
        elif opcion == "2":
            mostrar_inventario(inventario)
        elif opcion == "3":
            buscar_producto(inventario)
        elif opcion == "4":
            print("\nSaliendo del sistema. ¡Hasta pronto!")
        else:
            print("Opción no válida. Intente de nuevo.")


# El programa arranca aquí
if __name__ == "__main__":
    main()