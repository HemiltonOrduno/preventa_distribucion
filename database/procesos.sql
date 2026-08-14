
#####PROCEDIMIENTOS ALMACENADOS####

###PROCEDIMIENTO 1: ASIGNAR VENDEDOR A RUTA DE VISITA###
-- El coordinador asigna un vendedor a la ruta de un dia. Un vendedor
-- no puede cubrir dos rutas la misma fecha, y una ruta ya asignada no
-- se reasigna.

###DROP PROCEDURE IF EXISTS procoord_asignar_vendedor_ruta;

DELIMITER $$
CREATE PROCEDURE sp_asignar_vendedor_ruta(
    IN p_ruta_visita INT,
    IN p_empleado INT,
    IN p_fecha DATE
)
BEGIN
    DECLARE v_ocupado INT;
    DECLARE v_existe INT;

    SELECT COUNT(*) INTO v_ocupado
    FROM ruta_visita_semana
    WHERE empleado = p_empleado
      AND fecha = p_fecha
      AND ruta_visita <> p_ruta_visita
      AND edo_ruta_visita IN ('ERV006', 'ERV003');

    IF v_ocupado > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El vendedor ya tiene una ruta asignada esa fecha';
    END IF;

    SELECT COUNT(*) INTO v_existe
    FROM ruta_visita_semana
    WHERE ruta_visita = p_ruta_visita AND fecha = p_fecha;

    IF v_existe > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La ruta ya fue asignada para esa fecha';
    END IF;

    INSERT INTO ruta_visita_semana (ruta_visita, fecha, empleado, edo_ruta_visita)
    VALUES (p_ruta_visita, p_fecha, p_empleado, 'ERV006');

    -- Deja rastro de la ejecucion para poder verificar que el
    -- procedimiento corre desde la aplicacion
    INSERT INTO bitacora_procedimiento (procedimiento, detalle, resultado, fecha)
    VALUES ('sp_asignar_vendedor_ruta',
            CONCAT('Ruta ', p_ruta_visita, ' asignada al empleado ',
                   p_empleado, ' para el ', p_fecha),
            'OK', NOW());
END$$

END$$
DELIMITER ;

###PROCEDIMIENTO 2: CONSULTAR STOCK DE UN PEDIDO###
-- Devuelve los productos de un pedido con la cantidad solicitada y la
-- existencia actual, marcando si alcanza. Lo usa el almacenista al
-- validar el pedido antes de confirmarlo.

DELIMITER $$
CREATE PROCEDURE sp_consultar_stock_pedido(
    IN p_pedido INT
)
BEGIN
    SELECT
        dp.cod_producto,
        pr.nombre AS producto_nombre,
        pr.imagen,
        dp.cantidad,
        dp.precioUnitario AS precio_unitario,
        dp.importe,
        pr.stock AS stock_disponible,
        CASE WHEN pr.stock >= dp.cantidad THEN 'SUFICIENTE'
             ELSE 'INSUFICIENTE' END AS cobertura
    FROM detalle_pedido dp
    INNER JOIN producto pr ON pr.codigo = dp.cod_producto
    WHERE dp.num_pedido = p_pedido;

    INSERT INTO bitacora_procedimiento (procedimiento, detalle, resultado, fecha)
    VALUES ('sp_consultar_stock_pedido',
            CONCAT('Consulta de stock del pedido ', p_pedido),
            'OK', NOW());
END$$
DELIMITER ;


###PROCEDIMIENTO 3: INICIAR RUTA DE ENTREGA###
-- El repartidor sale del almacen: la entrega pasa a En proceso, el
-- vehiculo queda en ruta y la ruta de entrega en camino. Los tres
-- cambios van juntos porque representan una sola operacion.

DELIMITER $$
CREATE PROCEDURE sp_iniciar_ruta_entrega(
    IN p_entrega INT
)
BEGIN
    DECLARE v_vehiculo INT;
    DECLARE v_estado VARCHAR(10);

    SELECT edo_entrega INTO v_estado
    FROM entrega WHERE numero = p_entrega;

    IF v_estado IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La entrega no existe';
    END IF;

    IF v_estado = 'EEN002' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Esta ruta ya fue iniciada';
    END IF;

    SELECT numero INTO v_vehiculo
    FROM vehiculo WHERE entrega = p_entrega LIMIT 1;

    UPDATE entrega SET edo_entrega = 'EEN002' WHERE numero = p_entrega;

    IF v_vehiculo IS NOT NULL THEN
        UPDATE vehiculo SET edo_vehiculo = 'EV002' WHERE numero = v_vehiculo;
    END IF;

    UPDATE ruta_entrega SET edo_ruta_entrega = 'ERET002'
    WHERE entrega = p_entrega;

    INSERT INTO bitacora_procedimiento (procedimiento, detalle, resultado, fecha)
    VALUES ('sp_iniciar_ruta_entrega',
            CONCAT('Entrega ', p_entrega, ' iniciada, vehiculo ',
                   COALESCE(v_vehiculo, 0)),
            'OK', NOW());
END$$
DELIMITER ;


###PROCEDIMIENTO 4: REGISTRAR PRODUCTO NUEVO###
-- Dar de alta un producto
-- validar la fecha de caducidad
-- precio y peso validos

DELIMITER $$
CREATE PROCEDURE sp_registrar_producto(
    IN p_nombre VARCHAR(60),
    IN p_descripcion VARCHAR(100),
    IN p_imagen VARCHAR(255),
    IN p_precio DECIMAL(10,2),
    IN p_fecha_caducidad DATE,
    IN p_stock INT,
    IN p_peso DECIMAL(5,2),
    OUT p_codigo VARCHAR(10)
)
BEGIN
    DECLARE v_siguiente INT;
    DECLARE v_repetido INT;

    IF p_fecha_caducidad <= CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La fecha de caducidad debe ser posterior a hoy';
    END IF;

    IF p_precio <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El precio debe ser mayor a cero';
    END IF;

    IF p_peso <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El peso debe ser mayor a cero';
    END IF;

    -- edite esto, para validar nombre y peso por que pueden existir el mismo nombre mas no el mismo peso y el nombre
    SELECT COUNT(*) INTO v_repetido
    FROM producto
    WHERE nombre = CONVERT(p_nombre USING utf8mb4) COLLATE utf8mb4_0900_ai_ci
      AND peso = p_peso;

    IF v_repetido > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Ya existe un producto con ese nombre y presentacion';
    END IF;


    SELECT COALESCE(MAX(CAST(SUBSTRING(codigo, 2) AS UNSIGNED)), 0) + 1
      INTO v_siguiente
    FROM producto;

    SET p_codigo = CONCAT('P', LPAD(v_siguiente, 3, '0'));

    INSERT INTO producto (codigo, nombre, descripcion, imagen, precio,
                          fecha_caducidad, stock, peso)
    VALUES (p_codigo, p_nombre, p_descripcion, p_imagen, p_precio,
            p_fecha_caducidad, p_stock, p_peso);

    INSERT INTO bitacora_procedimiento (procedimiento, detalle, resultado, fecha)
    VALUES ('sp_registrar_producto',
            CONCAT('Producto ', p_codigo, ' registrado: ', p_nombre,
                   ' (', p_peso, ' g)'),
            'OK', NOW());
END$$
DELIMITER ;



###PROCEDIMIENTO 5: REGISTRAR DEVOLUCION EN LA ENTREGA###
-- El repartidor registra la devolucion durante la entrega. Se valida
-- que el producto pertenezca al pedido y que no se devuelva mas de lo
-- entregado. Si el pedido ya estaba cobrado, se genera el reembolso
-- como un pago negativo para que la cobranza cuadre.
-- Los CONVERT en las comparaciones evitan el choque de collation entre
-- los parametros del procedimiento y las columnas de las tablas.

DELIMITER $$
CREATE PROCEDURE sp_registrar_devolucion(
    IN p_entrega INT,
    IN p_pedido INT,
    IN p_cod_producto VARCHAR(10),
    IN p_cantidad INT,
    IN p_motivo VARCHAR(40),
    IN p_descripcion VARCHAR(150),
    IN p_cod_cambio VARCHAR(10),
    IN p_empleado INT,
    OUT p_devolucion INT,
    OUT p_importe DECIMAL(10,2),
    OUT p_reembolso DECIMAL(10,2)
)
BEGIN
    DECLARE v_cantidad_pedida INT;
    DECLARE v_precio DECIMAL(10,2);
    DECLARE v_ya_devuelto INT;
    DECLARE v_establecimiento INT;
    DECLARE v_ya_cobrado DECIMAL(10,2);

    IF p_cantidad <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La cantidad debe ser mayor a cero';
    END IF;

    SELECT dp.cantidad, dp.precioUnitario
      INTO v_cantidad_pedida, v_precio
    FROM detalle_pedido dp
    WHERE dp.num_pedido = p_pedido
      AND dp.cod_producto = CONVERT(p_cod_producto USING utf8mb4) COLLATE utf8mb4_0900_ai_ci;

    IF v_cantidad_pedida IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Ese producto no pertenece al pedido';
    END IF;

    SELECT COALESCE(SUM(cantidad), 0) INTO v_ya_devuelto
    FROM devolucion
    WHERE pedido = p_pedido
      AND cod_producto = CONVERT(p_cod_producto USING utf8mb4) COLLATE utf8mb4_0900_ai_ci;

    IF (p_cantidad + v_ya_devuelto) > v_cantidad_pedida THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'No puedes devolver mas piezas de las entregadas';
    END IF;

    SET p_importe = ROUND(p_cantidad * v_precio, 2);

    INSERT INTO devolucion (fecha, cantidad, motivo, descripcion, entrega,
                            cod_producto, pedido, importe, cod_producto_cambio)
    VALUES (CURDATE(), p_cantidad, p_motivo, p_descripcion, p_entrega,
            p_cod_producto, p_pedido, p_importe, p_cod_cambio);

    SET p_devolucion = LAST_INSERT_ID();

    -- El establecimiento se deriva del pedido
    SELECT v.establecimiento INTO v_establecimiento
    FROM pedido p
    INNER JOIN visita v ON v.numero = p.visita
    WHERE p.num = p_pedido;

    SELECT COALESCE(SUM(monto), 0) INTO v_ya_cobrado
    FROM pago WHERE pedido = p_pedido;

    SET p_reembolso = 0;

    IF v_ya_cobrado > 0 THEN
        SET p_reembolso = p_importe;
        INSERT INTO pago (monto, fecha, tipo_pago, empleado, establecimiento, pedido)
        VALUES (-p_reembolso, NOW(), 'TP001', p_empleado, v_establecimiento, p_pedido);
    END IF;

    INSERT INTO bitacora_procedimiento (procedimiento, detalle, resultado, fecha)
    VALUES ('sp_registrar_devolucion',
            CONCAT('Devolucion ', p_devolucion, ': ', p_cantidad, ' pza(s) de ',
                   p_cod_producto, ' del pedido ', p_pedido,
                   ', reembolso ', p_reembolso),
            'OK', NOW());
END$$
DELIMITER ;