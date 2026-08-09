"""Semantica de color de los catalogos de estado (RFN-27).

Un solo lugar define que tono le corresponde a cada estado del sistema.
Los serializers exponen el tono junto al nombre para que ninguna pantalla
tenga que repetir la logica de colores en JavaScript.

Tonos disponibles y su significado operativo:
    verde  #10B981  proceso concluido con exito
    ambar  #F78A00  en curso o esperando accion
    rojo   #991B1B  cancelado, pausado o perdida
    gris   #414A5E  etapa intermedia sin carga semantica
"""

VERDE = 'verde'
AMBAR = 'ambar'
ROJO = 'rojo'
GRIS = 'gris'

TONOS = {
    # --- Estados de pedido ---
    'EPD001': AMBAR,   # Pendiente de validacion
    'EPD002': AMBAR,   # En proceso
    'EPD003': GRIS,    # Registrado
    'EPD004': GRIS,    # Surtido
    'EPD005': VERDE,   # Entregado
    'EPD006': ROJO,    # Cancelado

    # --- Estados de entrega ---
    'EEN001': GRIS,    # Creada
    'EEN002': AMBAR,   # En proceso
    'EEN003': GRIS,    # Cargada
    'EEN004': VERDE,   # Completada

    # --- Estados de visita ---
    'EVI001': AMBAR,   # Pendiente
    'EVI002': AMBAR,   # En camino
    'EVI003': AMBAR,   # En proceso
    'EVI004': VERDE,   # Completada
    'EVI005': GRIS,    # Completada sin pedido

    # --- Estados de ruta de entrega ---
    'ERET001': GRIS,   # Creada
    'ERET002': AMBAR,  # En camino
    'ERET003': VERDE,  # Entregada
    'ERET004': ROJO,   # Pausada

    # --- Tipos de pago ---
    'TP001': VERDE,    # Efectivo
    'TP002': GRIS,     # Tarjeta

    # --- Tipos de movimiento ---
    'TM001': VERDE,    # Entrada
    'TM002': GRIS,     # Salida por pedido
    'TM003': ROJO,     # Salida por merma
    'TM004': AMBAR,    # Entrada por devolucion
}


def tono(codigo):
    """Devuelve el tono de un codigo de catalogo. Gris si no esta mapeado."""
    if not codigo:
        return GRIS
    return TONOS.get(codigo, GRIS)


# Codigos usados como constante en la logica de reportes.
ENTREGA_COMPLETADA = 'EEN004'
PEDIDO_ENTREGADO = 'EPD005'
PEDIDO_CANCELADO = 'EPD006'

# Movimientos que suman o restan existencias. El signo lo determina el
# tipo, no la cantidad: en DETALLE_MOVIMIENTO todas las cantidades son
# positivas y el trigger tg_actualizar_stock decide si suma o resta.
MOVIMIENTOS_ENTRADA = ('TM001', 'TM004')   # Entrada, Entrada por devolucion
MOVIMIENTOS_SALIDA = ('TM002', 'TM003')    # Salida por pedido, Salida por merma

# Un pedido esta activo mientras no se haya entregado ni cancelado: sigue
# ocupando inventario, ruta o cobranza. Es el universo del RF49.
PEDIDOS_ACTIVOS = (
    'EPD001',   # Pendiente de validacion
    'EPD002',   # En proceso
    'EPD003',   # Registrado
    'EPD004',   # Surtido
)

# Dias sin avanzar a partir de los cuales un pedido activo se marca como
# rezagado en el monitor.
DIAS_PEDIDO_REZAGADO = 3

# Formas de pago diferenciadas por el RF55.
PAGO_EFECTIVO = 'TP001'
PAGO_TARJETA = 'TP002'