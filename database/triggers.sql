-- Active: 1785279407257@@127.0.0.1@3306@inpredis_db
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

    IF NEW.entrega IS NOT NULL AND OLD.entrega IS NULL THEN

        SELECT COUNT(*) INTO total_pedidos
        FROM pedido
        WHERE entrega = NEW.entrega;

        SELECT e.zona INTO zona_nuevo_pedido
        FROM visita v
        INNER JOIN establecimiento e ON e.numero = v.establecimiento
        WHERE v.numero = NEW.visita;

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

        SELECT m.capacidad INTO capacidad_vehiculo
        FROM vehiculo v
        INNER JOIN modelo m ON m.numero = v.modelo
        WHERE v.entrega = NEW.entrega;

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

    END IF;
END$$
DELIMITER ;

###TRIGGER 2, CAMPOS CALCULADOS ###

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
END$$
DELIMITER ;

-- NUEVOS TRIGGERS 

DELIMITER $$
CREATE OR REPLACE TRIGGER tg_recalcular_importe_detalle
BEFORE UPDATE ON detalle_pedido
FOR EACH ROW
BEGIN
    -- Por qué: el importe de cada línea (cantidad * precio) se guarda
    -- como columna física, no se calcula al leer. Si el almacenista
    -- ajusta la cantidad (RF19) con un UPDATE directo, el importe se
    -- quedaría desactualizado a menos que alguien lo recalcule a mano.
    -- Este trigger lo hace automáticamente ANTES de guardar el UPDATE,
    -- así ninguna vista futura puede "olvidarse" de hacerlo.
    SET NEW.importe = NEW.cantidad * NEW.precioUnitario;
END$$
DELIMITER ;

-- Triggers correridos y actualizados
DELIMITER $$
CREATE OR REPLACE TRIGGER tg_campos_calculados_pedido_update
AFTER UPDATE ON detalle_pedido
FOR EACH ROW
BEGIN
    DECLARE nuevo_total DECIMAL(10,2);

    IF NEW.importe <> OLD.importe THEN
        -- Calculamos el total nuevo UNA sola vez, en una variable,
        -- y esa misma variable se usa en las tres asignaciones de abajo.
        -- Así evitamos que la 2da/3ra línea del SET vean un "total"
        -- que la 1ra línea ya modificó (el bug de arriba).
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
CREATE OR REPLACE TRIGGER tg_campos_calculados_pedido_delete
AFTER DELETE ON detalle_pedido
FOR EACH ROW
BEGIN
    DECLARE nuevo_total DECIMAL(10,2);

    -- Mismo motivo que arriba.
    SET nuevo_total = (SELECT total FROM pedido WHERE num = OLD.num_pedido) - OLD.importe;

    UPDATE pedido
    SET total = nuevo_total,
        subtotal = (nuevo_total / 1.16),
        iva = ((nuevo_total / 1.16) * 0.16)
    WHERE num = OLD.num_pedido;
END$$
DELIMITER ;