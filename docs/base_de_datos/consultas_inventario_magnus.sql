-- =====================================================================
-- Consultas de demostración - base de datos inventario_magnus
-- Ejecutar DESPUÉS de inventario_magnus.sql
-- =====================================================================
USE inventario_magnus;

-- 1. Inventario actual con su categoría y proveedor
SELECT p.codigo, p.nombre, c.nombre AS categoria, pr.nombre AS proveedor,
       p.stock, p.stock_minimo, p.precio
FROM producto p
LEFT JOIN categoria c  ON c.id_categoria = p.id_categoria
LEFT JOIN proveedor pr ON pr.id_proveedor = p.id_proveedor
ORDER BY c.nombre, p.nombre;

-- 2. Productos con stock bajo (usa la vista)
SELECT * FROM v_stock_bajo;

-- 3. Productos por vencer en los próximos 60 días (usa la vista)
SELECT * FROM v_productos_por_vencer ORDER BY fecha_vencimiento;

-- 3b. Pantalla "Stock y vencimientos" de Figma 2.0 (fecha clave, días y estado)
SELECT codigo, nombre, lote, stock, stock_minimo, fecha_clave, dias_restantes, estado
FROM v_stock_vencimientos
ORDER BY dias_restantes IS NULL, dias_restantes;

-- 4. Valor del inventario por categoría (a precio de compra y de venta)
SELECT c.nombre AS categoria,
       SUM(p.stock)                  AS unidades,
       SUM(p.stock * p.precio_compra) AS valor_compra,
       SUM(p.stock * p.precio)        AS valor_venta
FROM producto p
JOIN categoria c ON c.id_categoria = p.id_categoria
GROUP BY c.nombre
ORDER BY valor_venta DESC;

-- 5. Movimientos de un producto (ejemplo: Extintor ABC 10 lb)
SELECT m.fecha, m.tipo, m.cantidad, m.motivo, m.numero_factura, u.nombre AS registrado_por
FROM movimiento m
JOIN producto p     ON p.id_producto = m.id_producto
LEFT JOIN usuario u ON u.id_usuario = m.id_usuario
WHERE p.codigo = 'EXT-ABC-10'
ORDER BY m.fecha;

-- 6. Ventas por cliente (salidas)
SELECT cl.nombre AS cliente, COUNT(*) AS movimientos, SUM(m.cantidad) AS unidades,
       SUM(m.cantidad * p.precio) AS total_vendido
FROM movimiento m
JOIN cliente cl ON cl.id_cliente = m.id_cliente
JOIN producto p ON p.id_producto = m.id_producto
WHERE m.tipo = 'SALIDA'
GROUP BY cl.nombre
ORDER BY total_vendido DESC;

-- 6b. Compras por proveedor (entradas)
SELECT pv.nombre AS proveedor, COUNT(*) AS movimientos, SUM(m.cantidad) AS unidades,
       SUM(m.cantidad * p.precio_compra) AS total_comprado
FROM movimiento m
JOIN proveedor pv ON pv.id_proveedor = m.id_proveedor
JOIN producto p   ON p.id_producto = m.id_producto
WHERE m.tipo = 'ENTRADA'
GROUP BY pv.nombre
ORDER BY total_comprado DESC;

-- 7. Entradas y salidas por mes
SELECT DATE_FORMAT(fecha, '%Y-%m') AS mes,
       SUM(CASE WHEN tipo = 'ENTRADA' THEN cantidad ELSE 0 END) AS entradas,
       SUM(CASE WHEN tipo = 'SALIDA'  THEN cantidad ELSE 0 END) AS salidas
FROM movimiento
GROUP BY DATE_FORMAT(fecha, '%Y-%m')
ORDER BY mes;

-- 8. Los 3 productos más vendidos
SELECT p.nombre, SUM(m.cantidad) AS unidades_vendidas
FROM movimiento m
JOIN producto p ON p.id_producto = m.id_producto
WHERE m.tipo = 'SALIDA'
GROUP BY p.id_producto, p.nombre
ORDER BY unidades_vendidas DESC
LIMIT 3;

-- 9. Productos que nunca han tenido una salida
SELECT p.codigo, p.nombre
FROM producto p
WHERE NOT EXISTS (SELECT 1 FROM movimiento m
                  WHERE m.id_producto = p.id_producto AND m.tipo = 'SALIDA');

-- 10. Actividad por usuario
SELECT u.nombre, u.rol, COUNT(m.id_movimiento) AS movimientos_registrados
FROM usuario u
LEFT JOIN movimiento m ON m.id_usuario = u.id_usuario
GROUP BY u.id_usuario, u.nombre, u.rol
ORDER BY movimientos_registrados DESC;

-- 11. Reportes generados y quién los pidió
SELECT r.tipo, r.fecha_generacion, u.nombre AS generado_por
FROM reporte r
LEFT JOIN usuario u ON u.id_usuario = r.id_usuario
ORDER BY r.fecha_generacion;

-- 12. Comprobación: el stock guardado coincide con entradas menos salidas
SELECT p.codigo, p.stock AS stock_guardado,
       COALESCE(SUM(CASE WHEN m.tipo='ENTRADA' THEN m.cantidad ELSE -m.cantidad END), 0) AS stock_calculado
FROM producto p
LEFT JOIN movimiento m ON m.id_producto = p.id_producto
GROUP BY p.id_producto, p.codigo, p.stock
HAVING stock_guardado <> stock_calculado;   -- debe devolver 0 filas

-- 13. Prueba de las reglas del negocio (estas dos instrucciones deben FALLAR)
-- INSERT INTO movimiento (tipo, cantidad, id_producto) VALUES ('SALIDA', 9999, 1);   -- stock insuficiente
-- INSERT INTO producto (codigo, nombre, precio) VALUES ('X-1', 'Prueba', -10);        -- precio negativo
-- INSERT INTO movimiento (tipo, cantidad, id_producto, id_cliente) VALUES ('ENTRADA', 1, 1, 1);  -- una entrada no lleva cliente

-- =====================================================================
-- MÓDULO DE SERVICIOS (SG-SST)
-- =====================================================================

-- 14. Catálogo de servicios por categoría
SELECT cs.nombre AS categoria, sv.codigo, sv.nombre AS servicio, sv.precio_base
FROM servicio sv
JOIN categoria_servicio cs ON cs.id_categoria_servicio = sv.id_categoria_servicio
ORDER BY cs.nombre, sv.nombre;

-- 15. Servicios prestados o programados (usa la vista)
SELECT id_prestacion, fecha_inicio, estado, categoria, servicio, cliente, valor
FROM v_servicios_detalle
ORDER BY fecha_inicio;

-- 16. Servicios en ejecución o programados (pendientes)
SELECT fecha_inicio, estado, servicio, cliente, responsable
FROM v_servicios_detalle
WHERE estado IN ('EN_EJECUCION','PROGRAMADO')
ORDER BY fecha_inicio;

-- 17. Ingresos por servicios finalizados, por categoría
SELECT categoria, COUNT(*) AS servicios, SUM(valor) AS total_facturado
FROM v_servicios_detalle
WHERE estado = 'FINALIZADO'
GROUP BY categoria
ORDER BY total_facturado DESC;

-- 18. Servicios contratados por cada cliente
SELECT cl.nombre AS cliente, COUNT(ps.id_prestacion) AS servicios,
       COALESCE(SUM(CASE WHEN ps.estado <> 'CANCELADO' THEN ps.valor END), 0) AS valor_contratado
FROM cliente cl
LEFT JOIN prestacion_servicio ps ON ps.id_cliente = cl.id_cliente
GROUP BY cl.id_cliente, cl.nombre
ORDER BY valor_contratado DESC;

-- 19. Vista completa del cliente: compras de insumos + servicios
SELECT cl.nombre AS cliente,
       COALESCE((SELECT SUM(m.cantidad * p.precio)
                 FROM movimiento m JOIN producto p ON p.id_producto = m.id_producto
                 WHERE m.id_cliente = cl.id_cliente AND m.tipo = 'SALIDA'), 0) AS compras_insumos,
       COALESCE((SELECT SUM(ps.valor) FROM prestacion_servicio ps
                 WHERE ps.id_cliente = cl.id_cliente AND ps.estado = 'FINALIZADO'), 0) AS servicios_finalizados
FROM cliente cl
ORDER BY cl.nombre;

-- 20. Servicios del catálogo que aún no se han prestado
SELECT sv.codigo, sv.nombre
FROM servicio sv
WHERE NOT EXISTS (SELECT 1 FROM prestacion_servicio ps WHERE ps.id_servicio = sv.id_servicio);
