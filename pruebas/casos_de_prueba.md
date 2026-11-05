# Guía de casos de prueba (Entrega 3)

Cómo hacer cada prueba: abrir la terminal en la carpeta del proyecto y ejecutar `python inventario.py`.
Cada integrante hace SUS casos, anota el resultado en `pruebas/CP-XX.md` (qué escribió, qué pasó, aprobado o falló) y sube una captura a la carpeta `pruebas/`.

| Integrante | Casos ejecutados |
|---|---|
| Kevin Mauricio Hernández Valenzuela | CP-02, CP-11 |
| Jhon Sebastian Scarpeta Diaz | CP-03, CP-12 |
| Juan José Rodríguez Gómez | CP-14 |
| Carlos Andrés Portela Quesada | CP-09, CP-10 |
| Fredy Alejandro Olaya Alvarez | Prototipos Figma 2.0 (subió los archivos a la rama diseno), CP-21 |
| Juan José Roso Casanova | Diseño de los prototipos Figma 2.0 (colaboró con Fredy), CP-20 |
| Juan Sebastian Pérez Poveda | CP-17 |
| Juan Sebastian Tobon Alvarez | CP-18 |
| Rafael Salazar Rodriguez | CP-19 |
| Yeferson Calderón Camacho (líder) | CP-01, CP-04, CP-05, CP-06, CP-07, CP-08, CP-13, CP-15, CP-16 |

Los casos CP-01, CP-04, CP-05, CP-06, CP-07, CP-08, CP-13, CP-15 y CP-16 los ejecutó el líder del equipo.

CP-05 lo subió primero Juan José Rodríguez Gómez, pero la captura no correspondía al caso. El líder lo volvió a ejecutar y reemplazó la captura y el resultado.

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

**CP-17 Buscar producto.** Tener el producto `Casco de seguridad`. Opción 3; escribir `casco DE seguridad`, luego `Martillo` y luego Enter vacío.
Esperado: encuentra el casco sin distinguir mayúsculas; con `Martillo` avisa que no encontró ningún producto; con el campo vacío muestra "no puede estar vacío".

**CP-18 Límites máximos.** Opción 1; nombre `Tornillo`; cantidad `1000001`, luego `1000000`; precio `100000001`, luego `100000000`; fecha vacía.
Esperado: error "no puede ser mayor que 1000000" y "no puede ser mayor que 100000000"; acepta los valores máximos y guarda el producto.

**CP-19 Inventario vacío.** Con el archivo `inventario.json` borrado, ejecutar el programa y entrar a las opciones 2, 3, 4 y 5.
Esperado: cada opción avisa que el inventario está vacío, sin errores técnicos, y el menú sigue funcionando.

**CP-20 Eliminar producto inexistente y cancelar.** Tener el producto `Guantes`. Opción 5; escribir `Martillo` (no existe) y luego `cancelar`. Después opción 2.
Esperado: con `Martillo` dice "no existe un producto llamado 'Martillo'" y vuelve a pedir el nombre; con `cancelar` dice "Operación cancelada"; `Guantes` sigue en el inventario.

**CP-21 Actualizar cantidad por encima del límite.** Tener el producto `Guantes` con cantidad 10. Opción 4; nombre `Guantes`; nueva cantidad `1000001`, luego `20`. Después opción 2.
Esperado: error "no puede ser mayor que 1000000" y vuelve a pedir la cantidad; con `20` dice "Cantidad actualizada y guardada correctamente" y el inventario muestra 20.