-- ==========================================
-- PROCEDIMIENTOS ALMACENADOS
-- ==========================================

-- 1. Registrar visita
DELIMITER $$
CREATE PROCEDURE proalmc_registrar_visita(
    IN p_observaciones VARCHAR(200),
    IN p_fecha DATETIME,
    IN p_ruta_visita INT,
    IN p_establecimiento INT,
    IN p_empleado INT,
    IN p_edo_visita VARCHAR(10)
)
BEGIN
    INSERT INTO visita (observaciones, fecha, ruta_visita, establecimiento, empleado, edo_visita)
    VALUES (p_observaciones, p_fecha, p_ruta_visita, p_establecimiento, p_empleado, p_edo_visita);

    SELECT LAST_INSERT_ID() AS visita_id;
END$$
DELIMITER ;

-- 2. Registrar pedido
DELIMITER $$
CREATE OR REPLACE PROCEDURE proalmc_registrar_pedido(
    IN p_observaciones VARCHAR(200),
    IN p_fecha DATETIME,
    IN p_visita INT,
    IN p_edo_pedido VARCHAR(10),
    IN p_detalle JSON
)
BEGIN
    DECLARE v_pedido_id INT;
    DECLARE v_producto VARCHAR(10);
    DECLARE v_cantidad INT;
    DECLARE v_precio DECIMAL(10,2);
    DECLARE v_importe DECIMAL(10,2);
    DECLARE i INT DEFAULT 0;
    DECLARE n INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error al registrar el pedido, se realizó rollback';
    END;

    START TRANSACTION;

        INSERT INTO pedido (observaciones, fecha, subtotal, iva, total, visita, entrega, edo_pedido)
        VALUES (p_observaciones, p_fecha, 0, 0, 0, p_visita, NULL, p_edo_pedido);

        SET v_pedido_id = LAST_INSERT_ID();
        SET n = JSON_LENGTH(p_detalle);

        WHILE i < n DO
            SET v_producto = JSON_UNQUOTE(JSON_EXTRACT(p_detalle, CONCAT('$[', i, '].producto')));
            SET v_cantidad = JSON_EXTRACT(p_detalle, CONCAT('$[', i, '].cantidad'));
            SET v_precio = JSON_EXTRACT(p_detalle, CONCAT('$[', i, '].precio_unitario'));
            SET v_importe = ROUND(v_cantidad * v_precio, 2);

            INSERT INTO detalle_pedido (num_pedido, cod_producto, cantidad, precioUnitario, importe)
            VALUES (v_pedido_id, v_producto, v_cantidad, v_precio, v_importe);

            SET i = i + 1;
        END WHILE;

        UPDATE visita SET edo_visita = 'EVI004' WHERE numero = p_visita;

    COMMIT;

    SELECT v_pedido_id AS pedido_id;
END$$
DELIMITER ;


-- 3. Consultar stock del pedido con advertencias
DELIMITER $$
CREATE OR REPLACE PROCEDURE proalmc_consultar_stock_pedido(
    IN p_pedido_id INT
)
BEGIN
    SELECT
        pr.codigo AS producto_id,
        pr.nombre AS producto_nombre,
        dp.cantidad AS cantidad_pedida,
        pr.stock AS stock_actual,
        COALESCE(SUM(dp2.cantidad), 0) AS cantidad_comprometida,
        (pr.stock - COALESCE(SUM(dp2.cantidad), 0)) AS stock_disponible,
        CASE
            WHEN (pr.stock - COALESCE(SUM(dp2.cantidad), 0)) <= 0 THEN 'SIN STOCK'
            WHEN (pr.stock - COALESCE(SUM(dp2.cantidad), 0)) < dp.cantidad THEN 'STOCK INSUFICIENTE'
            ELSE 'OK'
        END AS advertencia
    FROM detalle_pedido dp
    INNER JOIN producto pr ON pr.codigo = dp.cod_producto
    LEFT JOIN detalle_pedido dp2 ON dp2.cod_producto = dp.cod_producto
        INNER JOIN pedido p2 ON p2.num = dp2.num_pedido
            AND p2.entrega IS NOT NULL
            AND p2.edo_pedido NOT IN ('EPD005', 'EPD006')
            AND p2.num <> p_pedido_id
    WHERE dp.num_pedido = p_pedido_id
    GROUP BY pr.codigo, pr.nombre, dp.cantidad, pr.stock;
END$$
DELIMITER ;

-- 4. Crear entrega
DELIMITER $$
CREATE OR REPLACE PROCEDURE proalmc_crear_entrega(
    IN p_empleado INT,
    IN p_vehiculo INT
)
BEGIN
    DECLARE v_edo_vehiculo VARCHAR(10);
    DECLARE v_entrega_id INT;

    SELECT edo_vehiculo INTO v_edo_vehiculo
    FROM vehiculo WHERE numero = p_vehiculo;

    IF v_edo_vehiculo <> 'EV001' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El vehículo no está disponible para carga';
    END IF;

    START TRANSACTION;

        INSERT INTO entrega (fecha_creacion, fecha_entrega, empleado, edo_entrega)
        VALUES (CURDATE(), NULL, p_empleado, 'EEN001');

        SET v_entrega_id = LAST_INSERT_ID();

    COMMIT;

    SELECT v_entrega_id AS entrega_id;
END$$
DELIMITER ;

-- 5. Agregar pedido a entrega
DELIMITER $$
CREATE OR REPLACE PROCEDURE proalmc_agregar_pedido_entrega(
    IN p_pedido_id INT,
    IN p_entrega_id INT
)
BEGIN
    DECLARE v_edo_pedido VARCHAR(10);

    SELECT edo_pedido INTO v_edo_pedido
    FROM pedido WHERE num = p_pedido_id;

    IF v_edo_pedido <> 'EPD003' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El pedido debe estar en estado Registrado para ser asignado a una entrega';
    END IF;

    START TRANSACTION;

        UPDATE pedido
        SET entrega = p_entrega_id,
            edo_pedido = 'EPD004'
        WHERE num = p_pedido_id;

    COMMIT;

    SELECT 'Pedido agregado correctamente a la entrega' AS mensaje;
END$$
DELIMITER ;

-- 6. Cerrar entrega
DELIMITER $$
CREATE OR REPLACE PROCEDURE proalmc_cerrar_entrega(
    IN p_entrega_id INT,
    IN p_empleado INT,
    IN p_vehiculo INT
)
BEGIN
    DECLARE v_edo_entrega VARCHAR(10);
    DECLARE v_edo_vehiculo VARCHAR(10);

    SELECT edo_entrega INTO v_edo_entrega
    FROM entrega WHERE numero = p_entrega_id;

    SELECT edo_vehiculo INTO v_edo_vehiculo
    FROM vehiculo WHERE numero = p_vehiculo;

    IF v_edo_entrega <> 'EEN002' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La entrega debe estar En proceso para poder cerrarla';
    END IF;

    IF v_edo_vehiculo <> 'EV001' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El vehículo debe estar Disponible para poder cargarlo';
    END IF;

    START TRANSACTION;

        UPDATE entrega
        SET edo_entrega = 'EEN003'
        WHERE numero = p_entrega_id;

        INSERT INTO emp_vehiculo (empleado, vehiculo, fecha_cargo)
        VALUES (p_empleado, p_vehiculo, CURDATE());

    COMMIT;

    SELECT 'Entrega cerrada y lista para salir' AS mensaje;
END$$
DELIMITER ;

-- 7. Iniciar ruta de entrega
DELIMITER $$
CREATE OR REPLACE PROCEDURE proalmc_iniciar_ruta_entrega(
    IN p_entrega_id INT,
    IN p_vehiculo INT
)
BEGIN
    DECLARE v_edo_entrega VARCHAR(10);

    SELECT edo_entrega INTO v_edo_entrega
    FROM entrega WHERE numero = p_entrega_id;

    IF v_edo_entrega <> 'EEN003' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La entrega debe estar Cargada para poder iniciar la ruta';
    END IF;

    START TRANSACTION;

        UPDATE entrega
        SET edo_entrega = 'EEN002'
        WHERE numero = p_entrega_id;

        UPDATE vehiculo
        SET edo_vehiculo = 'EV002'
        WHERE numero = p_vehiculo;

        UPDATE ruta_entrega
        SET edo_ruta_entrega = 'ERET002'
        WHERE entrega = p_entrega_id;

    COMMIT;

    SELECT 'Ruta de entrega iniciada' AS mensaje;
END$$
DELIMITER ;

-- 8. Finalizar ruta de entrega
DELIMITER $$
CREATE OR REPLACE PROCEDURE proalmc_finalizar_ruta_entrega(
    IN p_entrega_id INT,
    IN p_vehiculo INT
)
BEGIN
    DECLARE v_edo_entrega VARCHAR(10);

    SELECT edo_entrega INTO v_edo_entrega
    FROM entrega WHERE numero = p_entrega_id;

    IF v_edo_entrega <> 'EEN002' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La entrega debe estar En camino para poder finalizarla';
    END IF;

    START TRANSACTION;

        UPDATE entrega
        SET edo_entrega = 'EEN004',
            fecha_entrega = NOW()
        WHERE numero = p_entrega_id;

        UPDATE vehiculo
        SET edo_vehiculo = 'EV001',
            entrega = NULL
        WHERE numero = p_vehiculo;

        UPDATE ruta_entrega
        SET edo_ruta_entrega = 'ERET003'
        WHERE entrega = p_entrega_id;

    COMMIT;

    SELECT 'Ruta de entrega finalizada, vehículo disponible' AS mensaje;
END$$
DELIMITER ;

-- 9. Registrar movimiento de inventario
DELIMITER $$
CREATE OR REPLACE PROCEDURE proalmc_registrar_movimiento(
    IN p_observaciones VARCHAR(150),
    IN p_tipo_movimiento VARCHAR(10),
    IN p_devolucion INT,
    IN p_empleado INT,
    IN p_detalle JSON
)
BEGIN
    DECLARE v_movimiento_id INT;
    DECLARE v_producto VARCHAR(10);
    DECLARE v_cantidad INT;
    DECLARE v_precio DECIMAL(10,2);
    DECLARE v_subtotal DECIMAL(10,2);
    DECLARE i INT DEFAULT 0;
    DECLARE n INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error al registrar el movimiento, se realizó rollback';
    END;

    START TRANSACTION;

        INSERT INTO movimientos (observaciones, fecha, tipo_movimiento, devolucion, empleado)
        VALUES (p_observaciones, NOW(), p_tipo_movimiento, p_devolucion, p_empleado);

        SET v_movimiento_id = LAST_INSERT_ID();
        SET n = JSON_LENGTH(p_detalle);

        WHILE i < n DO
            SET v_producto = JSON_UNQUOTE(JSON_EXTRACT(p_detalle, CONCAT('$[', i, '].producto')));
            SET v_cantidad = JSON_EXTRACT(p_detalle, CONCAT('$[', i, '].cantidad'));
            SET v_precio = JSON_EXTRACT(p_detalle, CONCAT('$[', i, '].precio_unitario'));
            SET v_subtotal = ROUND(v_cantidad * v_precio, 2);

            INSERT INTO detalle_movimiento (cod_movimientos, cod_producto, cantidad, precioUnitario, subtotal)
            VALUES (v_movimiento_id, v_producto, v_cantidad, v_precio, v_subtotal);

            SET i = i + 1;
        END WHILE;

    COMMIT;

    SELECT v_movimiento_id AS movimiento_id;
END$$
DELIMITER ;

-- 10. Registrar devolución (repartidor en campo)
DELIMITER $$
CREATE OR REPLACE PROCEDURE proalmc_registrar_devolucion(
    IN p_cantidad INT,
    IN p_motivo VARCHAR(40),
    IN p_descripcion VARCHAR(150),
    IN p_entrega INT
)
BEGIN
    DECLARE v_devolucion_id INT;

    INSERT INTO devolucion (fecha, cantidad, motivo, descripcion, entrega)
    VALUES (CURDATE(), p_cantidad, p_motivo, p_descripcion, p_entrega);

    SET v_devolucion_id = LAST_INSERT_ID();

    SELECT v_devolucion_id AS devolucion_id,
           'Devolución registrada, pendiente de aceptación por almacenista' AS mensaje;
END$$
DELIMITER ;

-- 11. Aceptar devolución (almacenista confirma entrada al almacén)
DELIMITER $$
CREATE OR REPLACE PROCEDURE proalmc_aceptar_devolucion(
    IN p_devolucion_id INT,
    IN p_empleado INT,
    IN p_producto VARCHAR(10),
    IN p_cantidad INT,
    IN p_precio DECIMAL(10,2)
)
BEGIN
    DECLARE v_subtotal DECIMAL(10,2);
    DECLARE v_movimiento_id INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error al aceptar la devolución, se realizó rollback';
    END;

    START TRANSACTION;

        SET v_subtotal = ROUND(p_cantidad * p_precio, 2);

        INSERT INTO movimientos (observaciones, fecha, tipo_movimiento, devolucion, empleado)
        VALUES ('Entrada por devolución aceptada por almacenista', NOW(), 'TM004', p_devolucion_id, p_empleado);

        SET v_movimiento_id = LAST_INSERT_ID();

        INSERT INTO detalle_movimiento (cod_movimientos, cod_producto, cantidad, precioUnitario, subtotal)
        VALUES (v_movimiento_id, p_producto, p_cantidad, p_precio, v_subtotal);

    COMMIT;

    SELECT v_movimiento_id AS movimiento_id,
           'Devolución aceptada, stock actualizado' AS mensaje;
END$$
DELIMITER ;

