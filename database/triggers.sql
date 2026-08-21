-- Active: 1772565691688@@127.0.0.1@3306@inpredis_db
#################
#####TRIGGERS####
#################


####Trigger 1: Verificar zona y capacidad

DELIMITER $$
CREATE OR REPLACE TRIGGER tg_verificar_zona_capacidad
BEFORE UPDATE ON pedido
FOR EACH ROW
BEGIN
    DECLARE zona_entrega INT;
    DECLARE zona_nuevo_pedido INT;
    DECLARE peso_actual DECIMAL(10,2);
    DECLARE peso_nuevo_pedido DECIMAL(10,2);
    DECLARE capacidad_vehiculo DECIMAL(10,2);
    DECLARE total_pedidos INT;
    DECLARE es_express BOOLEAN DEFAULT FALSE;

    IF NEW.entrega IS NOT NULL AND OLD.entrega IS NULL THEN

        SELECT COUNT(*) INTO total_pedidos
        FROM pedido
        WHERE entrega = NEW.entrega;

        SELECT e.zona INTO zona_nuevo_pedido
        FROM visita v
        INNER JOIN establecimiento e ON e.numero = v.establecimiento
        WHERE v.numero = NEW.visita;

        SELECT m.capacidad INTO capacidad_vehiculo
        FROM vehiculo v
        INNER JOIN modelo m ON m.numero = v.modelo
        WHERE v.entrega = NEW.entrega;

        SET es_express = (capacidad_vehiculo IS NOT NULL AND capacidad_vehiculo < 11);

        IF es_express THEN
            IF NEW.devolucion_origen IS NULL THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Esta camioneta Express es exclusiva para pedidos de devolución';
            END IF;
        ELSE
            IF NEW.devolucion_origen IS NOT NULL THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Los pedidos de devolución solo pueden ir en la camioneta Express';
            END IF;

            IF total_pedidos > 0 THEN
                SELECT e.zona INTO zona_entrega
                FROM pedido p
                INNER JOIN visita v ON v.numero = p.visita
                INNER JOIN establecimiento e ON e.numero = v.establecimiento
                WHERE p.entrega = NEW.entrega
                LIMIT 1;

                IF zona_entrega <> zona_nuevo_pedido THEN
                    SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'El pedido no pertenece a la zona de esta entrega';
                END IF;
            END IF;
        END IF;

        IF capacidad_vehiculo > 0 THEN
            SELECT COALESCE(SUM(dp.cantidad * pr.peso), 0) / 1000 INTO peso_actual
            FROM pedido p
            INNER JOIN detalle_pedido dp ON dp.num_pedido = p.num
            INNER JOIN producto pr ON pr.codigo = dp.cod_producto
            WHERE p.entrega = NEW.entrega;

            SELECT COALESCE(SUM(dp.cantidad * pr.peso), 0) / 1000 INTO peso_nuevo_pedido
            FROM detalle_pedido dp
            INNER JOIN producto pr ON pr.codigo = dp.cod_producto
            WHERE dp.num_pedido = NEW.num;

            IF (peso_actual + peso_nuevo_pedido) > capacidad_vehiculo THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'El peso total de los pedidos excede la capacidad del vehículo';
            END IF;
        END IF;

        INSERT INTO bitacora_trigger (trigger_nombre, detalle, fecha)
        VALUES ('tg_verificar_zona_capacidad',
                CONCAT('Pedido ', NEW.num, ' aceptado en entrega ', NEW.entrega,
                       IF(es_express, ' (Express, multi-zona)', CONCAT(' (zona ', zona_nuevo_pedido, ')')),
                       ', peso ', ROUND(peso_actual + peso_nuevo_pedido, 2), ' kg de ',
                       capacidad_vehiculo, ' kg'),
                NOW());
    END IF;
END$$
DELIMITER ;


###TRIGGER 2: un establecimiento solo a una ruta asi solo es una visita a la semana por el negocio
DELIMITER $$
CREATE OR REPLACE TRIGGER tg_establecimiento_una_sola_ruta
BEFORE INSERT ON ruta_visita_orden
FOR EACH ROW
BEGIN
    DECLARE v_existe INT;

    SELECT COUNT(*) INTO v_existe
    FROM ruta_visita_orden
    WHERE establecimiento = NEW.establecimiento
      AND ruta_visita <> NEW.ruta_visita;

    IF v_existe > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El establecimiento ya pertenece a otra ruta de visita';
    END IF;

    INSERT INTO bitacora_trigger (trigger_nombre, detalle, fecha)
    VALUES ('tg_establecimiento_una_sola_ruta',
            CONCAT('Establecimiento ', NEW.establecimiento,
                   ' aceptado en la ruta ', NEW.ruta_visita),
            NOW());
END$$
DELIMITER ;


###TRIGGER 3: ACTUALIZAR STOCK####

DELIMITER $$
CREATE OR REPLACE TRIGGER tg_actualizar_stock
AFTER INSERT ON detalle_movimiento
FOR EACH ROW
BEGIN
    DECLARE tipo VARCHAR(50);

    SELECT nombre INTO tipo
    FROM tipo_movimiento
    WHERE codigo = (
        SELECT tipo_movimiento FROM movimientos WHERE codigo = NEW.cod_movimientos
    );

    IF tipo = 'Entrada' OR tipo = 'Entrada por devolución' THEN
        UPDATE producto
        SET stock = stock + NEW.cantidad
        WHERE codigo = NEW.cod_producto;
    ELSEIF tipo = 'Salida por pedido' OR tipo = 'Salida por merma' THEN
        UPDATE producto
        SET stock = stock - NEW.cantidad
        WHERE codigo = NEW.cod_producto;
    END IF;

    -- EVIDENCIA PAL TRIGGER --
    INSERT INTO bitacora_trigger (trigger_nombre, detalle, fecha)
    VALUES ('tg_actualizar_stock',
            CONCAT(tipo, ': ', NEW.cantidad, ' pza(s) de ', NEW.cod_producto),
            NOW());
END$$
DELIMITER ;



##la vida no es tan buena


###TRIGGER que ya no se implementaron ###

DELIMITER $$
CREATE OR REPLACE TRIGGER tg_campos_calculados_pedido
AFTER INSERT ON detalle_pedido
FOR EACH ROW
BEGIN
    UPDATE pedido
    SET total = (total + NEW.importe),
        subtotal = ((total + NEW.importe) / 1.16),
        iva = (((total + NEW.importe) / 1.16) * 0.16)
    WHERE num = NEW.num_pedido;
END$$
DELIMITER ;



-- NUEVOS TRIGGERS 

DELIMITER $$
CREATE OR REPLACE TRIGGER tg_recalcular_importe_detalle
BEFORE UPDATE ON detalle_pedido
FOR EACH ROW
BEGIN

    SET NEW.importe = NEW.cantidad * NEW.precioUnitario;
END$$
DELIMITER ;


DELIMITER $$
CREATE OR REPLACE TRIGGER tg_campos_calculados_pedido_update
AFTER UPDATE ON detalle_pedido
FOR EACH ROW
BEGIN
    DECLARE nuevo_total DECIMAL(10,2);

    IF NEW.importe <> OLD.importe THEN

        SET nuevo_total = (SELECT total FROM pedido WHERE num = NEW.num_pedido) - OLD.importe + NEW.importe;

        UPDATE pedido
        SET total = nuevo_total,
            subtotal = (nuevo_total / 1.16),
            iva = ((nuevo_total / 1.16) * 0.16)
        WHERE num = NEW.num_pedido;
    END IF;
END$$
DELIMITER ;


DELIMITER $$
CREATE OR REPLACE TRIGGER tg_campos_calculados_pedido
AFTER INSERT ON detalle_pedido
FOR EACH ROW
BEGIN
    DECLARE nuevo_total DECIMAL(10,2);

    SET nuevo_total = (SELECT total FROM pedido WHERE num = NEW.num_pedido) + NEW.importe;

    UPDATE pedido
    SET total = nuevo_total,
        subtotal = (nuevo_total / 1.16),
        iva = ((nuevo_total / 1.16) * 0.16)
    WHERE num = NEW.num_pedido;
END$$
DELIMITER ;

DELIMITER $$
CREATE OR REPLACE TRIGGER tg_campos_calculados_pedido_delete
AFTER DELETE ON detalle_pedido
FOR EACH ROW
BEGIN
    DECLARE suma_importes DECIMAL(10,2);

    SELECT COALESCE(SUM(importe), 0) INTO suma_importes
    FROM detalle_pedido
    WHERE num_pedido = OLD.num_pedido;

    UPDATE pedido
    SET subtotal = suma_importes,
        iva = ROUND(suma_importes * 0.16, 2),
        total = ROUND(suma_importes * 1.16, 2)
    WHERE num = OLD.num_pedido;
END$$
DELIMITER ;