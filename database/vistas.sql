-- ==========================================
-- VISTAS
-- ==========================================

-- 1. Pedidos pendientes de validación para el almacenista*******
CREATE OR REPLACE VIEW vta_pedidos_pendientes_almacenista AS
SELECT
    p.num AS pedido_id,
    p.fecha,
    p.subtotal,
    p.iva,
    p.total,
    p.observaciones,
    p.devolucion_origen,
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

-- 2. Vehículos disponibles para carga *********
CREATE OR REPLACE VIEW vta_vehiculos_disponibles AS
SELECT
ve.numero AS vehiculo_id,
ve.placas,
ve.serie_vin,
ve.entrega,
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

-- 3. Stock de productos con alerta de inventario*******
CREATE OR REPLACE VIEW vta_stock_productos AS
SELECT
    p.codigo AS producto_id,
    p.nombre,
    p.marca,
    p.descripcion,
    p.imagen,
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
FROM producto p;


-- 4. Establecimientos por zona para el coordinador **********
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
INNER JOIN empleado em ON em.num = e.empleado;


-- 5. Establecimientos sin ruta ********
CREATE OR REPLACE VIEW vta_establecimientos_sin_ruta AS
SELECT
    e.numero AS establecimiento_id,
    e.nombre AS establecimiento_nombre,
    e.estCalle AS calle,
    e.estNumero AS numero,
    e.estColonia AS colonia,
    e.telefono,
    e.latitud,
    e.longitud,
    e.fecha_registro,
    z.num AS zona_id,
    z.nombre AS zona_nombre,
    CONCAT(rep.repNombre, ' ', rep.repApellPat) AS representante
FROM establecimiento e
INNER JOIN zona z ON z.num = e.zona
INNER JOIN rep_establecimiento rep ON rep.numero = e.rep_establecimiento
WHERE NOT EXISTS (
    SELECT 1
    FROM ruta_visita_orden rvo
    WHERE rvo.establecimiento = e.numero
);