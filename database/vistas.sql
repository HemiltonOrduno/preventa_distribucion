-- ==========================================
-- VISTAS
-- ==========================================

-- 1. Ruta de visita del vendedor con establecimientos y estado
CREATE OR REPLACE VIEW vta_ruta_visita_vendedor AS
SELECT
    rv.numero AS ruta_id,
    rv.nombre AS ruta_nombre,
    CONCAT(em.empNombre, ' ', em.empApellPat) AS vendedor,
    e.numero AS establecimiento_id,
    e.nombre AS establecimiento_nombre,
    e.estCalle AS calle,
    e.estNumero AS numero,
    e.estColonia AS colonia,
    e.latitud,
    e.longitud,
    z.nombre AS zona,
    v.numero AS visita_id,
    v.fecha AS fecha_visita,
    ev.nombre AS estado_visita,
    erv.nombre AS estado_ruta,
    rv.zona AS zona_id,
    em.num AS empleado_id
FROM ruta_visita rv
INNER JOIN empleado em ON em.num = rv.empleado
INNER JOIN zona z ON z.num = rv.zona
INNER JOIN establecimiento e ON e.zona = rv.zona
INNER JOIN edo_ruta_visita erv ON erv.codigo = rv.edo_ruta_visita
LEFT JOIN visita v ON v.establecimiento = e.numero AND v.ruta_visita = rv.numero
LEFT JOIN edo_visita ev ON ev.codigo = v.edo_visita;

-- 2. Pedidos pendientes de validación para el almacenista
CREATE OR REPLACE VIEW vta_pedidos_pendientes_almacenista AS
SELECT
    p.num AS pedido_id,
    p.fecha,
    p.subtotal,
    p.iva,
    p.total,
    ep.nombre AS estado_pedido,
    e.numero AS establecimiento_id,
    e.nombre AS establecimiento_nombre,
    e.estColonia AS colonia,
    z.nombre AS zona,
    z.num AS zona_id,
    CONCAT(em.empNombre, ' ', em.empApellPat) AS vendedor,
    v.numero AS visita_id
FROM pedido p
INNER JOIN edo_pedido ep ON ep.codigo = p.edo_pedido
INNER JOIN visita v ON v.numero = p.visita
INNER JOIN establecimiento e ON e.numero = v.establecimiento
INNER JOIN zona z ON z.num = e.zona
INNER JOIN empleado em ON em.num = v.empleado
WHERE p.edo_pedido = 'EPD001';

-- 3. Vehículos disponibles para carga
CREATE OR REPLACE VIEW vta_vehiculos_disponibles AS
SELECT
    ve.numero AS vehiculo_id,
    ve.placas,
    ve.serie_vin,
    tv.nombre AS tipo_vehiculo,
    mo.nombre AS modelo,
    mo.ano,
    mo.capacidad,
    ma.nombre AS marca,
    ev.nombre AS estado,
    CONCAT(em.empNombre, ' ', em.empApellPat) AS repartidor_asignado,
    em.num AS empleado_id
FROM vehiculo ve
INNER JOIN tipo_vehiculo tv ON tv.codigo = ve.tipo_vehiculo
INNER JOIN modelo mo ON mo.numero = ve.modelo
INNER JOIN marca ma ON ma.codigo = mo.marca
INNER JOIN edo_vehiculo ev ON ev.codigo = ve.edo_vehiculo
INNER JOIN empleado em ON em.num = ve.empleado
WHERE ve.edo_vehiculo = 'EV001';

-- 4. Stock de productos con alerta de inventario
CREATE OR REPLACE VIEW vta_stock_productos AS
SELECT
    p.codigo AS producto_id,
    p.nombre,
    p.descripcion,
    p.precio,
    p.stock,
    p.peso,
    p.fecha_caducidad,
    CASE
        WHEN p.stock = 0 THEN 'Agotado'
        WHEN p.stock < 50 THEN 'Bajo'
        WHEN p.stock < 200 THEN 'Normal'
        ELSE 'Suficiente'
    END AS nivel_stock,
    CASE
        WHEN p.fecha_caducidad < CURDATE() THEN 'Caducado'
        WHEN p.fecha_caducidad < DATE_ADD(CURDATE(), INTERVAL 30 DAY) THEN 'Por caducar'
        ELSE 'Vigente'
    END AS estado_caducidad
FROM producto p
ORDER BY p.stock ASC;

-- 5. Entregas activas para el coordinador
CREATE OR REPLACE VIEW vta_entregas_activas_coordinador AS
SELECT
    en.numero AS entrega_id,
    en.fecha_creacion,
    en.fecha_entrega,
    ee.nombre AS estado_entrega,
    CONCAT(em.empNombre, ' ', em.empApellPat) AS repartidor,
    em.num AS repartidor_id,
    ve.placas AS vehiculo_placas,
    tv.nombre AS tipo_vehiculo,
    mo.capacidad AS capacidad_vehiculo,
    COUNT(p.num) AS total_pedidos,
    SUM(p.subtotal) AS total_entrega,
    re.numero AS ruta_entrega_id,
    re.nombre AS ruta_entrega_nombre,
    er.nombre AS estado_ruta
FROM entrega en
INNER JOIN edo_entrega ee ON ee.codigo = en.edo_entrega
INNER JOIN empleado em ON em.num = en.empleado
INNER JOIN vehiculo ve ON ve.entrega = en.numero
INNER JOIN tipo_vehiculo tv ON tv.codigo = ve.tipo_vehiculo
INNER JOIN modelo mo ON mo.numero = ve.modelo
LEFT JOIN pedido p ON p.entrega = en.numero
LEFT JOIN ruta_entrega re ON re.entrega = en.numero
LEFT JOIN edo_ruta_entrega er ON er.codigo = re.edo_ruta_entrega
WHERE en.edo_entrega IN ('EEN001', 'EEN002', 'EEN003')
GROUP BY en.numero, en.fecha_creacion, en.fecha_entrega, ee.nombre,
         em.empNombre, em.empApellPat, em.num, ve.placas,
         tv.nombre, mo.capacidad, re.numero, re.nombre, er.nombre;

-- 6. Establecimientos por zona para el coordinador
CREATE OR REPLACE VIEW vta_establecimientos_por_zona AS
SELECT
    z.num AS zona_id,
    z.nombre AS zona_nombre,
    z.descripcion AS zona_descripcion,
    e.numero AS establecimiento_id,
    e.nombre AS establecimiento_nombre,
    e.estCalle AS calle,
    e.estNumero AS numero,
    e.estColonia AS colonia,
    e.telefono,
    e.latitud,
    e.longitud,
    e.fecha_registro,
    ee.nombre AS estado_establecimiento,
    CONCAT(rep.repNombre, ' ', rep.repApellPat) AS representante,
    rep.telefono AS telefono_representante,
    CONCAT(em.empNombre, ' ', em.empApellPat) AS vendedor_asignado
FROM zona z
INNER JOIN establecimiento e ON e.zona = z.num
INNER JOIN edo_establecimiento ee ON ee.codigo = e.edo_establecimiento
INNER JOIN rep_establecimiento rep ON rep.numero = e.rep_establecimiento
INNER JOIN empleado em ON em.num = e.empleado
ORDER BY z.num, e.nombre;

-- 7. Ruta de entrega del repartidor con pedidos y establecimientos
CREATE OR REPLACE VIEW vta_ruta_entrega_repartidor AS
SELECT
    re.numero AS ruta_id,
    re.nombre AS ruta_nombre,
    er.nombre AS estado_ruta,
    en.numero AS entrega_id,
    en.fecha_creacion,
    ee.nombre AS estado_entrega,
    CONCAT(em.empNombre, ' ', em.empApellPat) AS repartidor,
    em.num AS repartidor_id,
    ve.placas AS vehiculo_placas,
    p.num AS pedido_id,
    p.subtotal,
    p.total,
    ep.nombre AS estado_pedido,
    est.numero AS establecimiento_id,
    est.nombre AS establecimiento_nombre,
    est.estCalle AS calle,
    est.estNumero AS numero,
    est.estColonia AS colonia,
    est.latitud,
    est.longitud,
    CONCAT(rep.repNombre, ' ', rep.repApellPat) AS representante,
    rep.telefono AS telefono_representante,
    ees.fecha_entrega,
    ees.hora_entrega
FROM ruta_entrega re
INNER JOIN edo_ruta_entrega er ON er.codigo = re.edo_ruta_entrega
INNER JOIN entrega en ON en.numero = re.entrega
INNER JOIN edo_entrega ee ON ee.codigo = en.edo_entrega
INNER JOIN empleado em ON em.num = re.empleado
INNER JOIN vehiculo ve ON ve.entrega = en.numero
INNER JOIN pedido p ON p.entrega = en.numero
INNER JOIN edo_pedido ep ON ep.codigo = p.edo_pedido
INNER JOIN visita v ON v.numero = p.visita
INNER JOIN establecimiento est ON est.numero = v.establecimiento
INNER JOIN rep_establecimiento rep ON rep.numero = est.rep_establecimiento
LEFT JOIN entrega_estable ees ON ees.entrega = en.numero AND ees.establecimiento = est.numero;

-- 8. Reporte de ventas para el administrador
CREATE OR REPLACE VIEW vta_reporte_ventas_admin AS
SELECT
    z.num AS zona_id,
    z.nombre AS zona_nombre,
    DATE_FORMAT(p.fecha, '%Y-%m') AS periodo,
    COUNT(p.num) AS total_pedidos,
    SUM(p.subtotal) AS total_subtotal,
    SUM(p.iva) AS total_iva,
    SUM(p.total) AS total_ventas,
    COUNT(CASE WHEN p.edo_pedido = 'EPD005' THEN 1 END) AS pedidos_entregados,
    COUNT(CASE WHEN p.edo_pedido = 'EPD006' THEN 1 END) AS pedidos_cancelados,
    CONCAT(em.empNombre, ' ', em.empApellPat) AS vendedor
FROM pedido p
INNER JOIN visita v ON v.numero = p.visita
INNER JOIN establecimiento e ON e.numero = v.establecimiento
INNER JOIN zona z ON z.num = e.zona
INNER JOIN empleado em ON em.num = v.empleado
GROUP BY z.num, z.nombre, DATE_FORMAT(p.fecha, '%Y-%m'), em.num, em.empNombre, em.empApellPat
ORDER BY periodo DESC, total_ventas DESC;