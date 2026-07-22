-- ==========================================
-- ÍNDICES
-- ==========================================

-- Pedido
CREATE INDEX idx_pedido_fecha ON pedido(fecha);
CREATE INDEX idx_pedido_estado ON pedido(edo_pedido);
CREATE INDEX idx_pedido_entrega ON pedido(entrega);
CREATE INDEX idx_pedido_visita ON pedido(visita);

-- Detalle pedido
CREATE INDEX idx_detalle_pedido_pedido ON detalle_pedido(num_pedido);
CREATE INDEX idx_detalle_pedido_producto ON detalle_pedido(cod_producto);

-- Visita
CREATE INDEX idx_visita_empleado_fecha ON visita(empleado, fecha);
CREATE INDEX idx_visita_establecimiento ON visita(establecimiento);
CREATE INDEX idx_visita_ruta ON visita(ruta_visita);
CREATE INDEX idx_visita_estado ON visita(edo_visita);

-- Establecimiento
CREATE INDEX idx_establecimiento_zona ON establecimiento(zona);
CREATE INDEX idx_establecimiento_estado ON establecimiento(edo_establecimiento);

-- Entrega
CREATE INDEX idx_entrega_estado ON entrega(edo_entrega);
CREATE INDEX idx_entrega_empleado ON entrega(empleado);

-- Ruta entrega
CREATE INDEX idx_ruta_entrega_empleado ON ruta_entrega(empleado);
CREATE INDEX idx_ruta_entrega_estado ON ruta_entrega(edo_ruta_entrega);

-- Ruta visita
CREATE INDEX idx_ruta_visita_zona ON ruta_visita(zona);
CREATE INDEX idx_ruta_visita_empleado ON ruta_visita(empleado);
CREATE INDEX idx_ruta_visita_estado ON ruta_visita(edo_ruta_visita);

-- Movimientos
CREATE INDEX idx_movimiento_tipo ON movimientos(tipo_movimiento);
CREATE INDEX idx_movimiento_fecha ON movimientos(fecha);
CREATE INDEX idx_movimiento_empleado ON movimientos(empleado);

-- Detalle movimiento
CREATE INDEX idx_detalle_movimiento ON detalle_movimiento(cod_movimientos);
CREATE INDEX idx_detalle_movimiento_producto ON detalle_movimiento(cod_producto);

-- Pago
CREATE INDEX idx_pago_pedido ON pago(pedido);
CREATE INDEX idx_pago_establecimiento ON pago(establecimiento);
CREATE INDEX idx_pago_fecha ON pago(fecha);

-- Devolucion
CREATE INDEX idx_devolucion_entrega ON devolucion(entrega);
CREATE INDEX idx_devolucion_fecha ON devolucion(fecha);

-- Empleado
CREATE INDEX idx_empleado_rol ON empleado(rol);
CREATE INDEX idx_empleado_estado ON empleado(edo_empleado);

-- Vehiculo
CREATE INDEX idx_vehiculo_estado ON vehiculo(edo_vehiculo);
CREATE INDEX idx_vehiculo_tipo ON vehiculo(tipo_vehiculo);

-- Entrega estable
CREATE INDEX idx_entrega_estable_entrega ON entrega_estable(entrega);
CREATE INDEX idx_entrega_estable_establecimiento ON entrega_estable(establecimiento);