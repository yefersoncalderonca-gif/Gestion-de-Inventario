"""
Sistema de Gestión de Inventario por Consola - Entrega 3
Proyecto de aula: Sistema de gestión de inventario para mypime del Huila (MagnusSIG SAS)

Qué hace el programa:
  - Guarda los productos en una lista de diccionarios y en el archivo inventario.json,
    por lo que la información se conserva al cerrar y volver a abrir el programa.
  - Permite agregar, ver, buscar, actualizar la cantidad y eliminar productos.
  - Valida todo lo que escribe el usuario: si un dato es inválido, muestra un
    mensaje de error y lo vuelve a pedir, sin cerrar el programa.
"""

import json
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

ARCHIVO = "inventario.json"
CLAVES = ("nombre", "cantidad", "precio", "vencimiento")
CANTIDAD_MAXIMA = 1000000
PRECIO_MAXIMO = 100000000


# ---------------------------------------------------------------------------
# Persistencia: lectura y escritura del archivo JSON
# ---------------------------------------------------------------------------

def guardar_inventario(inventario):
    """Guarda la lista en el archivo JSON. Devuelve True si se pudo guardar."""
    temporal = ARCHIVO + ".tmp"
    try:
        # Se escribe primero en un archivo temporal y luego se reemplaza el
        # original, así un fallo a mitad de la escritura no daña los datos.
        with open(temporal, "w", encoding="utf-8") as archivo:
            json.dump(inventario, archivo, ensure_ascii=False, indent=2)
        os.replace(temporal, ARCHIVO)
        return True
    except OSError as error:
        print("Error: no se pudo guardar el inventario (" + str(error) + ").")
        return False


def registro_valido(registro):
    """Comprueba que un registro leído del archivo tenga la forma correcta."""
    if not isinstance(registro, dict):
        return False
    for clave in CLAVES:
        if clave not in registro:
            return False
    nombre = registro["nombre"]
    cantidad = registro["cantidad"]
    precio = registro["precio"]
    if not isinstance(nombre, str) or nombre.strip() == "":
        return False
    if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad < 0:
        return False
    if isinstance(precio, bool) or not isinstance(precio, (int, float)) or precio <= 0:
        return False
    if not isinstance(registro["vencimiento"], str):
        return False
    return True


def cargar_inventario():
    """Lee el archivo al iniciar. Si no existe lo crea; si está dañado, lo respalda."""
    if not os.path.exists(ARCHIVO):
        print("No se encontró '" + ARCHIVO + "'. Se creó un inventario nuevo.")
        guardar_inventario([])
        return []

    try:
        with open(ARCHIVO, "r", encoding="utf-8") as archivo:
            contenido = archivo.read()
    except (OSError, UnicodeDecodeError) as error:
        print("Error: no se pudo leer '" + ARCHIVO + "' (" + str(error) + ").")
        print("Se inicia con un inventario vacío.")
        return []

    if contenido.strip() == "":
        print("El archivo '" + ARCHIVO + "' está vacío. Se inicia un inventario nuevo.")
        return []

    try:
        datos = json.loads(contenido)
        if not isinstance(datos, list):
            raise ValueError("el archivo no contiene una lista")
        for registro in datos:
            if not registro_valido(registro):
                raise ValueError("hay un registro con datos inválidos")
    except ValueError:
        respaldo = ARCHIVO + ".corrupto"
        print("Error: el archivo '" + ARCHIVO + "' está dañado o tiene datos inválidos.")
        try:
            os.replace(ARCHIVO, respaldo)
            print("Se guardó una copia en '" + respaldo + "' y se inicia un inventario nuevo.")
        except OSError:
            print("No se pudo guardar la copia. Se inicia un inventario nuevo.")
        guardar_inventario([])
        return []

    print("Inventario cargado: " + str(len(datos)) + " producto(s).")
    return datos


# ---------------------------------------------------------------------------
# Validación de datos: cada función repite la pregunta hasta recibir un dato válido
# ---------------------------------------------------------------------------

def pedir_texto(mensaje):
    """Pide un texto que no esté vacío."""
    while True:
        texto = input(mensaje).strip()
        if texto == "":
            print("Error: este campo no puede estar vacío.")
        else:
            return texto


def pedir_entero(mensaje, minimo, maximo):
    """Pide un número entero entre minimo y maximo."""
    while True:
        texto = input(mensaje).strip()
        digitos = texto.lstrip("-")
        if not (digitos.isascii() and digitos.isdigit()):
            print("Error: escriba solo números enteros, sin letras ni símbolos (ejemplo: 10).")
            continue
        try:
            valor = int(texto)
        except ValueError:
            print("Error: escriba solo números enteros (ejemplo: 10).")
            continue
        if valor < minimo:
            print("Error: el valor no puede ser menor que " + str(minimo) + ".")
        elif valor > maximo:
            print("Error: el valor no puede ser mayor que " + str(maximo) + ".")
        else:
            return valor


def pedir_precio(mensaje):
    """Pide un precio mayor que cero. Acepta punto o coma como separador decimal."""
    while True:
        texto = input(mensaje).strip().replace(",", ".")
        permitido = True
        for letra in texto:
            if letra not in "0123456789.-":
                permitido = False
        if texto == "" or not permitido:
            print("Error: escriba solo números, sin letras ni símbolos (ejemplo: 25000).")
            continue
        try:
            valor = float(texto)
        except ValueError:
            print("Error: el precio no es un número válido (ejemplo: 25000).")
            continue
        if valor <= 0:
            print("Error: el precio debe ser mayor que cero.")
        elif valor > PRECIO_MAXIMO:
            print("Error: el precio no puede ser mayor que " + str(PRECIO_MAXIMO) + ".")
        else:
            return valor


def pedir_fecha_opcional(mensaje):
    """Pide una fecha dd/mm/aaaa. Si el usuario solo presiona Enter, no hay fecha."""
    while True:
        texto = input(mensaje).strip()
        if texto == "":
            return ""
        try:
            fecha = datetime.strptime(texto, "%d/%m/%Y")
            return fecha.strftime("%d/%m/%Y")
        except ValueError:
            print("Error: fecha inválida. Use el formato dd/mm/aaaa con una fecha real (ejemplo: 15/11/2026).")


def pedir_si_no(mensaje):
    """Pide una confirmación s/n y devuelve True si el usuario escribe s."""
    while True:
        texto = input(mensaje).strip().lower()
        if texto == "s":
            return True
        if texto == "n":
            return False
        print("Error: escriba s para sí o n para no.")


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def buscar_indice(inventario, nombre):
    """Devuelve la posición del producto con ese nombre, o -1 si no existe."""
    for posicion in range(len(inventario)):
        if inventario[posicion]["nombre"].lower() == nombre.lower():
            return posicion
    return -1


def formato_precio(valor):
    """Devuelve el precio con separador de miles, por ejemplo $25.000."""
    if float(valor).is_integer():
        return "$" + "{:,}".format(int(valor)).replace(",", ".")
    texto = "{:,.2f}".format(valor)
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return "$" + texto


def mostrar_producto(producto):
    """Imprime los datos de un producto."""
    print("  Nombre:      " + producto["nombre"])
    print("  Cantidad:    " + str(producto["cantidad"]))
    print("  Precio:      " + formato_precio(producto["precio"]))
    if producto["vencimiento"] != "":
        print("  Vencimiento: " + producto["vencimiento"])


# ---------------------------------------------------------------------------
# Funciones del sistema
# ---------------------------------------------------------------------------

def agregar_producto(inventario):
    """Pide los datos de un producto, los valida y lo agrega al inventario."""
    print("\n--- AGREGAR PRODUCTO ---")

    # Se repite hasta que el nombre no esté vacío y no exista ya en el inventario
    while True:
        nombre = pedir_texto("Nombre del producto: ")
        if buscar_indice(inventario, nombre) == -1:
            break
        print("Error: ya existe un producto llamado '" + nombre + "'. Escriba otro nombre.")

    cantidad = pedir_entero("Cantidad en stock: ", 0, CANTIDAD_MAXIMA)
    precio = pedir_precio("Precio unitario: ")
    vencimiento = pedir_fecha_opcional("Fecha de vencimiento (dd/mm/aaaa, Enter si no aplica): ")

    inventario.append({
        "nombre": nombre,
        "cantidad": cantidad,
        "precio": precio,
        "vencimiento": vencimiento,
    })
    if guardar_inventario(inventario):
        print("Producto '" + nombre + "' agregado y guardado correctamente.")
    else:
        print("Producto '" + nombre + "' agregado, pero no se pudo guardar en el archivo.")


def mostrar_inventario(inventario):
    """Recorre el inventario con un ciclo for y muestra todos los productos."""
    print("\n--- INVENTARIO ACTUAL ---")

    if len(inventario) == 0:
        print("El inventario está vacío. Agregue productos primero.")
    else:
        numero = 1
        for producto in inventario:
            linea = (str(numero) + ". " + producto["nombre"]
                     + " | Cantidad: " + str(producto["cantidad"])
                     + " | Precio: " + formato_precio(producto["precio"]))
            if producto["vencimiento"] != "":
                linea = linea + " | Vence: " + producto["vencimiento"]
            print(linea)
            numero = numero + 1
        print("Total de productos registrados: " + str(len(inventario)))


def buscar_producto(inventario):
    """Busca productos cuyo nombre contenga el texto escrito."""
    print("\n--- BUSCAR PRODUCTO ---")

    if len(inventario) == 0:
        print("El inventario está vacío. No hay nada que buscar.")
        return

    texto = pedir_texto("Nombre del producto a buscar: ")
    encontrados = 0
    for producto in inventario:
        if texto.lower() in producto["nombre"].lower():
            if encontrados == 0:
                print("Producto(s) encontrado(s):")
            mostrar_producto(producto)
            encontrados = encontrados + 1

    if encontrados == 0:
        print("No se encontró ningún producto que contenga '" + texto + "'.")


def actualizar_cantidad(inventario):
    """Cambia la cantidad en stock de un producto existente."""
    print("\n--- ACTUALIZAR CANTIDAD ---")

    if len(inventario) == 0:
        print("El inventario está vacío. No hay productos para actualizar.")
        return

    # Se repite hasta que el producto exista; el usuario puede escribir "cancelar"
    while True:
        nombre = pedir_texto("Nombre del producto (o 'cancelar'): ")
        if nombre.lower() == "cancelar":
            print("Operación cancelada.")
            return
        posicion = buscar_indice(inventario, nombre)
        if posicion != -1:
            break
        print("Error: no existe un producto llamado '" + nombre + "'.")

    producto = inventario[posicion]
    print("Cantidad actual de '" + producto["nombre"] + "': " + str(producto["cantidad"]))
    producto["cantidad"] = pedir_entero("Nueva cantidad: ", 0, CANTIDAD_MAXIMA)
    if guardar_inventario(inventario):
        print("Cantidad actualizada y guardada correctamente.")


def eliminar_producto(inventario):
    """Elimina un producto después de pedir confirmación."""
    print("\n--- ELIMINAR PRODUCTO ---")

    if len(inventario) == 0:
        print("El inventario está vacío. No hay productos para eliminar.")
        return

    while True:
        nombre = pedir_texto("Nombre del producto (o 'cancelar'): ")
        if nombre.lower() == "cancelar":
            print("Operación cancelada.")
            return
        posicion = buscar_indice(inventario, nombre)
        if posicion != -1:
            break
        print("Error: no existe un producto llamado '" + nombre + "'.")

    producto = inventario[posicion]
    if pedir_si_no("¿Eliminar '" + producto["nombre"] + "'? (s/n): "):
        inventario.pop(posicion)
        if guardar_inventario(inventario):
            print("Producto eliminado y cambio guardado correctamente.")
    else:
        print("Operación cancelada. No se eliminó nada.")


def mostrar_menu():
    """Imprime las opciones del menú principal."""
    print("\n========== SISTEMA DE INVENTARIO ==========")
    print("1. Agregar producto")
    print("2. Ver inventario")
    print("3. Buscar producto")
    print("4. Actualizar cantidad")
    print("5. Eliminar producto")
    print("6. Salir")


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

def main():
    inventario = cargar_inventario()
    opcion = ""

    while opcion != "6":
        mostrar_menu()
        try:
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                agregar_producto(inventario)
            elif opcion == "2":
                mostrar_inventario(inventario)
            elif opcion == "3":
                buscar_producto(inventario)
            elif opcion == "4":
                actualizar_cantidad(inventario)
            elif opcion == "5":
                eliminar_producto(inventario)
            elif opcion == "6":
                print("\nSaliendo del sistema. Los datos quedaron guardados. ¡Hasta pronto!")
            else:
                print("Opción no válida. Escriba un número del 1 al 6.")
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C o cierre de la entrada: se guarda y se sale sin errores
            print("\nEntrada interrumpida. Guardando datos y saliendo...")
            guardar_inventario(inventario)
            break
        except Exception as error:
            # Último recurso: un error inesperado no debe cerrar el programa
            print("Ocurrió un error inesperado (" + str(error) + "). El programa continúa.")


# El programa arranca aquí
if __name__ == "__main__":
    main()
    