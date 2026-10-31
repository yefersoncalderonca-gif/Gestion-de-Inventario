# Guía de casos de prueba (Entrega 3)

Cómo hacer cada prueba: abrir la terminal en la carpeta del proyecto y ejecutar `python inventario.py`.
Cada integrante hace SUS casos, anota el resultado en `pruebas/CP-XX.md` (qué escribió, qué pasó, aprobado o falló) y sube una captura a la carpeta `pruebas/`.

| Integrante | Casos |
|---|---|
| Kevin Mauricio Hernández Valenzuela | CP-02, CP-11 |
| Jhon Sebastian Scarpeta Diaz | CP-03, CP-12 |
| Juan Sebastián Pérez Poveda | CP-04, CP-13 |
| Juan José Rodríguez Gómez | CP-05, CP-14 |
| Juan José Roso Casanova | CP-06, CP-15 |
| Juan Sebastián Tobon Álvarez | CP-07, CP-16 |
| Rafael Salazar Rodríguez | CP-08 |
| Carlos Andrés Portela Quesada | CP-09, CP-10 |
| Fredy Alejandro Olaya Alvarez | CP-01 |

## Casos

**CP-01 Camino normal.** Opción 1; nombre `Extintor ABC 10 lb`; cantidad `14`; precio `95000`; fecha `02/11/2026`; luego opción 2.
Esperado: dice "agregado y guardado correctamente" y el producto aparece en la lista.

**CP-02 Cantidad con letras o símbolos.** Opción 1; nombre `Botiquín tipo A`; cantidad `abc`, luego `1.5`, luego `@#`, luego `10`; precio `48000`; fecha vacía (Enter).
Esperado: error en cada dato inválido, vuelve a pedir la cantidad y acepta 10.

**CP-03 Cantidad negativa.** Opción 1; nombre `Casco de seguridad`; cantidad `-5`, luego `5`; precio `32000`; fecha vacía.
Esperado: error "no puede ser menor que 0" y acepta 5.

**CP-04 Precio inválido.** Opción 1; nombre `Guantes de nitrilo`; cantidad `8`; precio `$$`, `hola`, `0`, `-100`, luego `48000`.
Esperado: errores y acepta 48000.

**CP-05 Nombre vacío.** Opción 1; nombre vacío (Enter), luego solo espacios, luego `Tapabocas N95`; cantidad `60`; precio `65000`.
Esperado: error "no puede estar vacío" 2 veces y acepta el nombre válido.

**CP-06 Producto duplicado.** Agregar `Botiquín tipo A` (cantidad 25, precio 48000). Luego opción 1 otra vez con nombre `botiquín TIPO a`.
Esperado: error "ya existe un producto" y pide otro nombre; escribir `Gel antibacterial` y terminar el registro.

**CP-07 Fecha inválida.** Opción 1; nombre `Camilla rígida`; cantidad `6`; precio `210000`; fecha `31/02/2026`, `2026-11-02`, `abc`, luego `15/11/2026`.
Esperado: error en las 3 primeras y acepta la última.

**CP-08 Persistencia.** Agregar 2 productos y salir con la opción 6. Volver a ejecutar `python inventario.py` y elegir la opción 2.
Esperado: dice "Inventario cargado: 2 producto(s)" y aparecen los mismos 2.

**CP-09 Archivo inexistente.** Cerrar el programa, borrar el archivo con `Remove-Item inventario.json` y ejecutar el programa.
Esperado: dice "No se encontró 'inventario.json'. Se creó un inventario nuevo." y abre el menú sin error.

**CP-10 Archivo dañado.** Con el programa cerrado, ejecutar `Set-Content inventario.json "esto no es json {"` y luego el programa.
Esperado: avisa que el archivo está dañado, crea `inventario.json.corrupto` y abre con inventario vacío, sin cerrarse.

**CP-11 Archivo vacío.** Con el programa cerrado, ejecutar `New-Item inventario.json -ItemType File -Force` y luego el programa.
Esperado: dice que el archivo está vacío, inicia un inventario nuevo y abre normal.

**CP-12 Datos fuera de rango en el archivo.** Con el programa cerrado, ejecutar
`Set-Content inventario.json '[{"nombre": "Casco", "cantidad": -4, "precio": 32000, "vencimiento": ""}]'` y luego el programa.
Esperado: detecta datos inválidos, respalda el archivo y abre con inventario vacío.

**CP-13 Opciones de menú inválidas.** En el menú escribir `x`, Enter vacío, `9` y `1.5`.
Esperado: "Opción no válida" cada vez y el menú sigue funcionando.

**CP-14 Actualizar cantidad.** Tener el producto `Casco de seguridad`. Opción 4; nombre `Martillo` (no existe), luego `Casco de seguridad`; cantidad `-3`, `abc`, luego `20`.
Esperado: errores controlados; la cantidad queda en 20 y se guarda.

**CP-15 Eliminar con confirmación.** Tener un producto. Opción 5; nombre del producto; confirmar con `x` (inválido), luego `n`. Repetir y confirmar con `s`.
Esperado: `x` da error, `n` no borra, `s` elimina y el cambio se guarda.

**CP-16 Interrupción.** Estando en el menú, presionar `Ctrl + C`.
Esperado: dice "Entrada interrumpida. Guardando datos y saliendo..." sin mensajes técnicos (traceback).