-- =====================================================================
-- Base de datos: inventario_magnus
-- Proyecto de aula: Sistema de gestión de inventario para mypime del Huila
-- Cliente: MagnusSIG SAS (SG-SST e insumos de emergencia), Neiva, Huila
-- Asignatura: Introducción a la Base de Datos (Ing. Juan Sebastian Parra Sáenz)
-- Motor: MySQL 8.0 (Workbench) / compatible con MariaDB 10.5+
-- Basado en el diagrama entidad-relación versión 2 del proyecto y en los
-- prototipos de Figma 2.0 (productos, stock y vencimientos, movimientos,
-- proveedores, clientes y reportes).
--
-- Contenido:
--   1. Creación de la base de datos
--   2. Tablas (llaves primarias, foráneas, restricciones e índices)
--      - Inventario de insumos: usuario, categoria, proveedor, cliente,
--        producto, movimiento, reporte
--      - Servicios de SST: categoria_servicio, servicio, prestacion_servicio
--   3. Disparadores (actualizan el stock al registrar un movimiento)
--   4. Vistas (stock bajo, productos por vencer, detalle de movimientos
--      y de servicios)
--   5. Datos de ejemplo
-- Las consultas de demostración están en consultas_inventario_magnus.sql
-- =====================================================================

DROP DATABASE IF EXISTS inventario_magnus;
CREATE DATABASE inventario_magnus
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE inventario_magnus;

-- ---------------------------------------------------------------------
-- 2. TABLAS
-- ---------------------------------------------------------------------

-- Personas que acceden al sistema (Administrador u Operador)
CREATE TABLE usuario (
    id_usuario   INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    nombre       VARCHAR(100)  NOT NULL,
    correo       VARCHAR(120)  NOT NULL,
    contrasena   VARCHAR(255)  NOT NULL COMMENT 'Se guarda el hash, nunca la clave en texto',
    rol          ENUM('ADMINISTRADOR','OPERADOR') NOT NULL DEFAULT 'OPERADOR',
    activo       TINYINT(1)    NOT NULL DEFAULT 1,
    PRIMARY KEY (id_usuario),
    UNIQUE KEY uq_usuario_correo (correo),
    CONSTRAINT ck_usuario_correo CHECK (correo LIKE '%_@_%._%')
) ENGINE=InnoDB;

-- Agrupa los productos por tipo (extintores, botiquines, EPP, etc.)
CREATE TABLE categoria (
    id_categoria INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    nombre       VARCHAR(100)  NOT NULL,
    descripcion  VARCHAR(255)  NULL,
    PRIMARY KEY (id_categoria),
    UNIQUE KEY uq_categoria_nombre (nombre)
) ENGINE=InnoDB;

-- Empresa o persona que suministra productos
CREATE TABLE proveedor (
    id_proveedor INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    nit          VARCHAR(20)   NOT NULL,
    nombre       VARCHAR(100)  NOT NULL,
    telefono     VARCHAR(20)   NULL,
    correo       VARCHAR(120)  NULL,
    direccion    VARCHAR(255)  NULL,
    PRIMARY KEY (id_proveedor),
    UNIQUE KEY uq_proveedor_nit (nit)
) ENGINE=InnoDB;

-- Empresa o persona que compra a MagnusSIG
CREATE TABLE cliente (
    id_cliente   INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    nit          VARCHAR(20)   NOT NULL,
    nombre       VARCHAR(100)  NOT NULL,
    telefono     VARCHAR(20)   NULL,
    correo       VARCHAR(120)  NULL,
    PRIMARY KEY (id_cliente),
    UNIQUE KEY uq_cliente_nit (nit)
) ENGINE=InnoDB;

-- Artículo del inventario
CREATE TABLE producto (
    id_producto           INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    codigo                VARCHAR(20)   NOT NULL,
    nombre                VARCHAR(100)  NOT NULL,
    descripcion           VARCHAR(255)  NULL,
    unidad_medida         VARCHAR(20)   NOT NULL DEFAULT 'unidad',
    precio_compra         DECIMAL(12,2) NOT NULL DEFAULT 0,
    precio                DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT 'Precio de venta',
    stock                 INT           NOT NULL DEFAULT 0,
    stock_minimo          INT           NOT NULL DEFAULT 0,
    lote                  VARCHAR(30)   NULL,
    fecha_vencimiento     DATE          NULL,
    fecha_proxima_recarga DATE          NULL COMMENT 'Para extintores y botiquines que se recargan o reponen',
    id_categoria          INT UNSIGNED  NULL,
    id_proveedor          INT UNSIGNED  NULL,
    PRIMARY KEY (id_producto),
    UNIQUE KEY uq_producto_codigo (codigo),
    KEY ix_producto_nombre (nombre),
    KEY ix_producto_vencimiento (fecha_vencimiento),
    KEY ix_producto_categoria (id_categoria),
    KEY ix_producto_proveedor (id_proveedor),
    CONSTRAINT fk_producto_categoria FOREIGN KEY (id_categoria)
        REFERENCES categoria (id_categoria) ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_producto_proveedor FOREIGN KEY (id_proveedor)
        REFERENCES proveedor (id_proveedor) ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT ck_producto_precio_compra CHECK (precio_compra >= 0),
    CONSTRAINT ck_producto_precio        CHECK (precio >= 0),
    CONSTRAINT ck_producto_stock         CHECK (stock >= 0),
    CONSTRAINT ck_producto_stock_minimo  CHECK (stock_minimo >= 0)
) ENGINE=InnoDB;

-- Entrada o salida de un producto
CREATE TABLE movimiento (
    id_movimiento  INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    tipo           ENUM('ENTRADA','SALIDA') NOT NULL,
    cantidad       INT           NOT NULL,
    fecha          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    motivo         VARCHAR(60)   NULL COMMENT 'Compra, venta, devolución, ajuste, daño...',
    numero_factura VARCHAR(30)   NULL,
    observacion    VARCHAR(255)  NULL,
    id_producto    INT UNSIGNED  NOT NULL,
    id_usuario     INT UNSIGNED  NULL,
    id_cliente     INT UNSIGNED  NULL COMMENT 'Solo para salidas (ventas)',
    id_proveedor   INT UNSIGNED  NULL COMMENT 'Solo para entradas (compras o reposición)',
    PRIMARY KEY (id_movimiento),
    KEY ix_movimiento_producto (id_producto),
    KEY ix_movimiento_usuario (id_usuario),
    KEY ix_movimiento_cliente (id_cliente),
    KEY ix_movimiento_proveedor (id_proveedor),
    KEY ix_movimiento_fecha (fecha),
    CONSTRAINT fk_movimiento_producto FOREIGN KEY (id_producto)
        REFERENCES producto (id_producto) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_movimiento_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario (id_usuario) ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_movimiento_cliente FOREIGN KEY (id_cliente)
        REFERENCES cliente (id_cliente) ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_movimiento_proveedor FOREIGN KEY (id_proveedor)
        REFERENCES proveedor (id_proveedor) ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT ck_movimiento_cantidad CHECK (cantidad > 0)
) ENGINE=InnoDB;

-- Reporte generado a partir de los datos del inventario
CREATE TABLE reporte (
    id_reporte        INT UNSIGNED NOT NULL AUTO_INCREMENT,
    tipo              VARCHAR(50)  NOT NULL,
    fecha_desde       DATE         NULL COMMENT 'Inicio del periodo consultado',
    fecha_hasta       DATE         NULL COMMENT 'Fin del periodo consultado',
    fecha_generacion  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_usuario        INT UNSIGNED NULL,
    PRIMARY KEY (id_reporte),
    KEY ix_reporte_usuario (id_usuario),
    CONSTRAINT fk_reporte_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario (id_usuario) ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT ck_reporte_periodo CHECK (fecha_hasta >= fecha_desde)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 2b. MÓDULO DE SERVICIOS (SG-SST)
--     MagnusSIG también presta servicios: asesorías, capacitaciones,
--     auditorías, evaluaciones y exámenes médicos ocupacionales.
--     Comparte con el inventario las tablas usuario y cliente.
-- ---------------------------------------------------------------------

-- Agrupa los servicios por tipo
CREATE TABLE categoria_servicio (
    id_categoria_servicio INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre                VARCHAR(100) NOT NULL,
    descripcion           VARCHAR(255) NULL,
    PRIMARY KEY (id_categoria_servicio),
    UNIQUE KEY uq_categoria_servicio_nombre (nombre)
) ENGINE=InnoDB;

-- Catálogo de servicios que ofrece la empresa
CREATE TABLE servicio (
    id_servicio           INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    codigo                VARCHAR(20)   NOT NULL,
    nombre                VARCHAR(120)  NOT NULL,
    descripcion           VARCHAR(255)  NULL,
    precio_base           DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT 'Valor de referencia; el valor final se pacta en cada prestación',
    activo                TINYINT(1)    NOT NULL DEFAULT 1,
    id_categoria_servicio INT UNSIGNED  NOT NULL,
    PRIMARY KEY (id_servicio),
    UNIQUE KEY uq_servicio_codigo (codigo),
    KEY ix_servicio_categoria (id_categoria_servicio),
    CONSTRAINT fk_servicio_categoria FOREIGN KEY (id_categoria_servicio)
        REFERENCES categoria_servicio (id_categoria_servicio) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_servicio_precio CHECK (precio_base >= 0)
) ENGINE=InnoDB;

-- Registro de cada servicio contratado por un cliente
CREATE TABLE prestacion_servicio (
    id_prestacion  INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_servicio    INT UNSIGNED  NOT NULL,
    id_cliente     INT UNSIGNED  NOT NULL,
    id_usuario     INT UNSIGNED  NULL COMMENT 'Quién lo registró en el sistema',
    responsable    VARCHAR(100)  NULL COMMENT 'Profesional que presta el servicio',
    fecha_inicio   DATE          NOT NULL,
    fecha_fin      DATE          NULL,
    estado         ENUM('PROGRAMADO','EN_EJECUCION','FINALIZADO','CANCELADO') NOT NULL DEFAULT 'PROGRAMADO',
    valor          DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT 'Valor pactado con el cliente',
    numero_factura VARCHAR(30)   NULL,
    observacion    VARCHAR(255)  NULL,
    PRIMARY KEY (id_prestacion),
    KEY ix_prestacion_servicio (id_servicio),
    KEY ix_prestacion_cliente (id_cliente),
    KEY ix_prestacion_usuario (id_usuario),
    KEY ix_prestacion_fecha (fecha_inicio),
    CONSTRAINT fk_prestacion_servicio FOREIGN KEY (id_servicio)
        REFERENCES servicio (id_servicio) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_prestacion_cliente FOREIGN KEY (id_cliente)
        REFERENCES cliente (id_cliente) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_prestacion_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario (id_usuario) ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT ck_prestacion_valor   CHECK (valor >= 0),
    CONSTRAINT ck_prestacion_fechas  CHECK (fecha_fin >= fecha_inicio)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 3. DISPARADORES
--    El stock del producto se mantiene solo: una ENTRADA lo suma y una
--    SALIDA lo resta. Una salida mayor al stock disponible se rechaza.
-- ---------------------------------------------------------------------
DELIMITER $$

CREATE TRIGGER trg_movimiento_antes_insertar
BEFORE INSERT ON movimiento
FOR EACH ROW
BEGIN
    DECLARE v_stock INT;
    IF NEW.tipo = 'SALIDA' THEN
        SELECT stock INTO v_stock FROM producto WHERE id_producto = NEW.id_producto;
        IF v_stock < NEW.cantidad THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Stock insuficiente: la salida supera las unidades disponibles';
        END IF;
        IF NEW.id_proveedor IS NOT NULL THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Una salida no puede tener proveedor: el proveedor aplica solo a entradas';
        END IF;
    ELSE
        IF NEW.id_cliente IS NOT NULL THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Una entrada no puede tener cliente: el cliente aplica solo a salidas';
        END IF;
    END IF;
END$$

CREATE TRIGGER trg_movimiento_despues_insertar
AFTER INSERT ON movimiento
FOR EACH ROW
BEGIN
    IF NEW.tipo = 'ENTRADA' THEN
        UPDATE producto SET stock = stock + NEW.cantidad WHERE id_producto = NEW.id_producto;
    ELSE
        UPDATE producto SET stock = stock - NEW.cantidad WHERE id_producto = NEW.id_producto;
    END IF;
END$$

DELIMITER ;

-- ---------------------------------------------------------------------
-- 4. VISTAS
-- ---------------------------------------------------------------------

-- Productos cuyo stock está en el mínimo o por debajo
CREATE VIEW v_stock_bajo AS
SELECT p.id_producto, p.codigo, p.nombre, c.nombre AS categoria,
       p.stock, p.stock_minimo, (p.stock_minimo - p.stock) AS faltante
FROM producto p
LEFT JOIN categoria c ON c.id_categoria = p.id_categoria
WHERE p.stock <= p.stock_minimo;

-- Productos que vencen en los próximos 60 días (o ya vencidos)
CREATE VIEW v_productos_por_vencer AS
SELECT p.id_producto, p.codigo, p.nombre, p.lote, p.stock,
       p.fecha_vencimiento,
       DATEDIFF(p.fecha_vencimiento, CURDATE()) AS dias_restantes
FROM producto p
WHERE p.fecha_vencimiento IS NOT NULL
  AND p.fecha_vencimiento <= DATE_ADD(CURDATE(), INTERVAL 60 DAY);

-- Pantalla "Stock y vencimientos" de Figma 2.0: fecha clave (la más próxima entre
-- vencimiento y recarga), días restantes y estado del producto
CREATE VIEW v_stock_vencimientos AS
SELECT t.id_producto, t.codigo, t.nombre, t.lote, t.stock, t.stock_minimo, t.fecha_clave,
       DATEDIFF(t.fecha_clave, CURDATE()) AS dias_restantes,
       CASE
           WHEN t.fecha_clave IS NOT NULL AND DATEDIFF(t.fecha_clave, CURDATE()) <= 10 THEN 'Urgente'
           WHEN t.fecha_clave IS NOT NULL AND DATEDIFF(t.fecha_clave, CURDATE()) <= 30 THEN 'Por vencer'
           WHEN t.stock <= t.stock_minimo THEN 'Bajo mínimo'
           WHEN t.fecha_clave IS NULL THEN 'Sin vencimiento'
           ELSE 'Vigente'
       END AS estado
FROM (
    SELECT p.id_producto, p.codigo, p.nombre, p.lote, p.stock, p.stock_minimo,
           CASE
               WHEN p.fecha_vencimiento IS NULL THEN p.fecha_proxima_recarga
               WHEN p.fecha_proxima_recarga IS NULL THEN p.fecha_vencimiento
               ELSE LEAST(p.fecha_vencimiento, p.fecha_proxima_recarga)
           END AS fecha_clave
    FROM producto p
) t;

-- Movimientos con los nombres en lugar de los identificadores
CREATE VIEW v_movimientos_detalle AS
SELECT m.id_movimiento, m.fecha, m.tipo, p.codigo, p.nombre AS producto,
       m.cantidad, m.motivo, m.numero_factura,
       u.nombre AS registrado_por,
       COALESCE(cl.nombre, pv.nombre) AS cliente_o_proveedor
FROM movimiento m
JOIN producto p        ON p.id_producto = m.id_producto
LEFT JOIN usuario u    ON u.id_usuario  = m.id_usuario
LEFT JOIN cliente cl   ON cl.id_cliente = m.id_cliente
LEFT JOIN proveedor pv ON pv.id_proveedor = m.id_proveedor;

-- Servicios prestados con los nombres en lugar de los identificadores
CREATE VIEW v_servicios_detalle AS
SELECT ps.id_prestacion, ps.fecha_inicio, ps.fecha_fin, ps.estado,
       cs.nombre AS categoria, sv.codigo, sv.nombre AS servicio,
       cl.nombre AS cliente, ps.responsable, ps.valor, ps.numero_factura
FROM prestacion_servicio ps
JOIN servicio sv            ON sv.id_servicio = ps.id_servicio
JOIN categoria_servicio cs  ON cs.id_categoria_servicio = sv.id_categoria_servicio
JOIN cliente cl             ON cl.id_cliente = ps.id_cliente;

-- ---------------------------------------------------------------------
-- 5. DATOS DE EJEMPLO
--    Las contraseñas son claves de demostración guardadas como hash SHA-256.
--    En la aplicación real se debe usar el hash de Django.
-- ---------------------------------------------------------------------

INSERT INTO usuario (nombre, correo, contrasena, rol) VALUES
('Administrador MagnusSIG', 'admin@magnussig.com',     SHA2('demo-admin-2026', 256),  'ADMINISTRADOR'),
('Operador Bodega',         'bodega@magnussig.com',    SHA2('demo-bodega-2026', 256), 'OPERADOR'),
('Operador Ventas',         'ventas@magnussig.com',    SHA2('demo-ventas-2026', 256), 'OPERADOR');

INSERT INTO categoria (nombre, descripcion) VALUES
('Extintores',            'Extintores de distintos agentes y capacidades'),
('Botiquines',            'Botiquines y reposición de insumos de primeros auxilios'),
('Elementos de protección personal', 'Cascos, guantes, tapabocas y similares'),
('Camillas y transporte', 'Camillas rígidas y accesorios de inmovilización'),
('Higiene y bioseguridad','Gel antibacterial, alcohol y desinfectantes');

INSERT INTO proveedor (nit, nombre, telefono, correo, direccion) VALUES
('900123456-1', 'Extintores del Sur S.A.S.',   '3101234567', 'ventas@extintoressur.com',  'Cra. 5 # 12-30, Neiva'),
('900654321-7', 'Distribuidora Médica Huila',  '3207654321', 'pedidos@dmhuila.com',        'Calle 8 # 4-15, Neiva'),
('800987654-3', 'Seguridad Industrial Andina', '3159876543', 'contacto@sialandina.com',    'Av. Circunvalar # 20-45, Bogotá');

INSERT INTO cliente (nit, nombre, telefono, correo) VALUES
('891180001-2', 'Constructora Surcolombiana Ltda.', '3001112233', 'compras@surcolombiana.com'),
('900456789-0', 'Clínica Los Andes S.A.S.',         '3012223344', 'logistica@clinicalosandes.com'),
('900222333-5', 'Colegio San Agustín',              '3023334455', 'rectoria@colsanagustin.edu.co');

INSERT INTO producto (codigo, nombre, descripcion, unidad_medida, precio_compra, precio, stock, stock_minimo,
                      lote, fecha_vencimiento, fecha_proxima_recarga, id_categoria, id_proveedor) VALUES
('EXT-ABC-10', 'Extintor ABC 10 lb',      'Extintor multipropósito polvo químico seco', 'unidad', 70000, 95000, 0, 5,  'L2026-01', '2027-06-30', '2027-01-15', 1, 1),
('EXT-CO2-10', 'Extintor CO2 10 lb',      'Extintor de dióxido de carbono',             'unidad', 150000, 195000, 0, 3, 'L2026-02', '2027-09-30', '2027-03-10', 1, 1),
('BOT-TA-001', 'Botiquín tipo A',         'Botiquín para empresas hasta 10 personas',   'unidad', 32000, 48000, 0, 8,   'L2026-03', '2026-12-15', NULL,         2, 2),
('BOT-TB-001', 'Botiquín tipo B',         'Botiquín para empresas de 10 a 50 personas', 'unidad', 78000, 110000, 0, 4,  'L2026-03', '2027-02-28', NULL,         2, 2),
('EPP-CAS-01', 'Casco de seguridad',      'Casco dieléctrico con barboquejo',           'unidad', 21000, 32000, 0, 10,  NULL,        NULL,         NULL,         3, 3),
('EPP-GUA-01', 'Guantes de nitrilo',      'Caja x 100 unidades',                        'caja',   30000, 48000, 0, 6,   'L2026-05', '2028-05-31', NULL,         3, 3),
('EPP-TAP-95', 'Tapabocas N95',           'Caja x 20 unidades',                         'caja',   45000, 65000, 0, 10,  'L2026-06', '2027-11-30', NULL,         3, 2),
('CAM-RIG-01', 'Camilla rígida',          'Camilla de polietileno con arnés',           'unidad', 150000, 210000, 0, 2, NULL,        NULL,         NULL,         4, 3),
('HIG-GEL-500','Gel antibacterial 500 ml','Frasco con dosificador',                     'frasco', 7000, 12000, 0, 15,   'L2026-07', '2026-12-01', NULL,         5, 2);

-- Las entradas llevan proveedor y las salidas llevan cliente.
-- Las entradas y salidas actualizan el stock automáticamente (disparadores).
INSERT INTO movimiento (tipo, cantidad, fecha, motivo, numero_factura, observacion, id_producto, id_usuario, id_cliente, id_proveedor) VALUES
('ENTRADA', 20, '2026-10-05 09:00:00', 'Compra',  'FC-1001', 'Compra inicial de extintores',        1, 2, NULL, 1),
('ENTRADA', 10, '2026-10-05 09:10:00', 'Compra',  'FC-1001', NULL,                                  2, 2, NULL, 1),
('ENTRADA', 15, '2026-10-06 10:00:00', 'Compra',  'FC-1002', 'Botiquines tipo A',                   3, 2, NULL, 2),
('ENTRADA',  8, '2026-10-06 10:05:00', 'Compra',  'FC-1002', 'Botiquines tipo B',                   4, 2, NULL, 2),
('ENTRADA', 30, '2026-10-07 14:00:00', 'Compra',  'FC-1003', 'Cascos',                              5, 2, NULL, 3),
('ENTRADA', 12, '2026-10-07 14:10:00', 'Compra',  'FC-1003', NULL,                                  6, 2, NULL, 3),
('ENTRADA', 25, '2026-10-08 08:30:00', 'Compra',  'FC-1004', NULL,                                  7, 2, NULL, 2),
('ENTRADA',  4, '2026-10-08 08:40:00', 'Compra',  'FC-1005', NULL,                                  8, 2, NULL, 3),
('ENTRADA', 40, '2026-10-09 11:00:00', 'Compra',  'FC-1006', NULL,                                  9, 2, NULL, 2),
('SALIDA',  12, '2026-10-12 15:00:00', 'Venta',   'FV-2001', 'Dotación de obra',                    1, 3, 1, NULL),
('SALIDA',  20, '2026-10-12 15:10:00', 'Venta',   'FV-2001', NULL,                                  5, 3, 1, NULL),
('SALIDA',   9, '2026-10-14 09:30:00', 'Venta',   'FV-2002', 'Reposición de botiquines',            3, 3, 2, NULL),
('SALIDA',  10, '2026-10-14 09:40:00', 'Venta',   'FV-2002', NULL,                                  7, 3, 2, NULL),
('SALIDA',  35, '2026-10-20 16:00:00', 'Venta',   'FV-2003', 'Campaña de higiene',                  9, 3, 3, NULL),
('SALIDA',   3, '2026-10-21 10:00:00', 'Venta',   'FV-2004', NULL,                                  8, 3, 2, NULL),
('ENTRADA',  6, '2026-10-26 08:00:00', 'Devolución', NULL,   'Devolución de cliente en buen estado', 5, 2, NULL, NULL);

INSERT INTO reporte (tipo, fecha_desde, fecha_hasta, fecha_generacion, id_usuario) VALUES
('Stock actual',                 NULL,         NULL,         '2026-10-30 08:00:00', 1),
('Productos por vencer o recargar', '2026-10-24', '2026-11-23', '2026-10-30 08:05:00', 1),
('Movimientos del mes',          '2026-10-01', '2026-10-31', '2026-10-31 17:00:00', 1);

-- Servicios de SST (los precios son de demostración)
INSERT INTO categoria_servicio (nombre, descripcion) VALUES
('Asesoría SG-SST',               'Diagnóstico, diseño, implementación, mantenimiento y administración del SG-SST'),
('Capacitación',                  'Capacitaciones y entrenamientos en seguridad y salud en el trabajo'),
('Auditoría',                     'Auditorías internas, de proveedores, PESV e ISO'),
('Evaluación y diagnóstico',      'Riesgos laborales, riesgo psicosocial, profesiograma y análisis de puesto'),
('Exámenes médicos ocupacionales','Gestión de exámenes médicos ocupacionales');

INSERT INTO servicio (codigo, nombre, descripcion, precio_base, id_categoria_servicio) VALUES
('ASE-SGSST-01', 'Asesoría en la implementación del SG-SST',  'Acompañamiento para implementar el SG-SST',          2500000, 1),
('CAP-PA-01',    'Capacitación en primeros auxilios',         'Taller teórico-práctico de primeros auxilios',        900000, 2),
('CAP-INC-01',   'Capacitación en control de incendios',      'Uso de extintores y brigadas contra incendio',        950000, 2),
('CAP-PESV-01',  'Capacitación en PESV',                      'Plan Estratégico de Seguridad Vial',                  850000, 2),
('AUD-INT-01',   'Auditoría interna del SG-SST',              'Auditoría interna al sistema de gestión',            1800000, 3),
('AUD-ISO-45',   'Auditoría ISO 45001',                       'Auditoría con base en la norma ISO 45001',           2800000, 3),
('AUD-PRV-01',   'Auditoría a proveedores',                   'Evaluación de proveedores y contratistas',           1500000, 3),
('EVA-RIE-01',   'Evaluación de riesgos laborales',           'Identificación y valoración de peligros',            1600000, 4),
('EVA-PSI-01',   'Batería de riesgo psicosocial',             'Aplicación y análisis de la batería psicosocial',    2200000, 4),
('EVA-PRO-01',   'Profesiograma',                             'Perfil de exigencias por cargo',                     1200000, 4),
('EVA-APT-01',   'Análisis de puesto de trabajo',             'Estudio de condiciones del puesto',                  1100000, 4),
('MED-EMO-01',   'Gestión de exámenes médicos ocupacionales', 'Coordinación de exámenes de ingreso, periódicos y egreso', 600000, 5);

INSERT INTO prestacion_servicio (id_servicio, id_cliente, id_usuario, responsable, fecha_inicio, fecha_fin, estado, valor, numero_factura, observacion) VALUES
(1,  1, 1, 'Profesional SST A',  '2026-09-01', '2026-10-15', 'FINALIZADO',   2500000, 'FS-3001', 'Implementación completa del SG-SST'),
(2,  3, 1, 'Profesional SST B',    '2026-10-10', '2026-10-10', 'FINALIZADO',    900000, 'FS-3002', 'Capacitación a 25 docentes'),
(3,  1, 1, 'Profesional SST B',    '2026-10-18', '2026-10-18', 'FINALIZADO',    950000, 'FS-3003', 'Brigada de obra'),
(5,  2, 1, 'Profesional SST A',  '2026-10-20', NULL,         'EN_EJECUCION', 1800000, NULL,      'Auditoría en curso'),
(9,  2, 1, 'Profesional SST A',  '2026-11-03', NULL,         'PROGRAMADO',   2200000, NULL,      'Programada para la primera semana de noviembre'),
(8,  3, 1, 'Profesional SST B',    '2026-11-10', NULL,         'PROGRAMADO',   1600000, NULL,      NULL),
(12, 1, 1, 'Profesional SST A',  '2026-10-25', '2026-10-30', 'FINALIZADO',    600000, 'FS-3004', 'Exámenes de ingreso de 30 trabajadores'),
(4,  2, 1, 'Profesional SST B',    '2026-09-20', NULL,         'CANCELADO',     850000, NULL,      'Cancelado por el cliente');
