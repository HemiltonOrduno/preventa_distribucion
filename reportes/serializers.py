"""Serializers del Modulo de Administrador (Modulo 8 - Reportes)."""

from datetime import date

from django.utils import timezone
from rest_framework import serializers

from .catalogos import (
    DIAS_PEDIDO_REZAGADO, MOVIMIENTOS_ENTRADA, MOVIMIENTOS_SALIDA, tono,
)
from .models import (
    DetalleMovimiento, DetallePedido, Devolucion, Entrega,
    EntregaEstablecimiento, Movimiento, Pago, Pedido,
)


def fecha_local(valor):
    """Convierte un datetime a date local, funcione o no USE_TZ.

    Con USE_TZ = True los datetimes llegan con zona horaria y hay que
    convertirlos; con USE_TZ = False llegan naive y localtime() falla.
    Este helper cubre ambos casos para que el modulo no dependa de como
    quede configurado el proyecto.
    """
    if valor is None:
        return None
    if timezone.is_aware(valor):
        return timezone.localtime(valor).date()
    return valor.date()


def _nombre_empleado(empleado):
    if empleado is None:
        return None
    partes = [
        empleado.nombre_de_pila,
        empleado.apellido_paterno,
        empleado.apellido_materno,
    ]
    return ' '.join(p for p in partes if p)


class PedidoHistorialSerializer(serializers.ModelSerializer):
    """RF44 - Renglon del historial de pedidos."""

    establecimiento = serializers.SerializerMethodField()
    establecimiento_id = serializers.SerializerMethodField()
    zona = serializers.SerializerMethodField()
    vendedor = serializers.SerializerMethodField()
    vendedor_id = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()
    estado_id = serializers.CharField(source='edo_pedido_id', read_only=True)
    estado_tono = serializers.SerializerMethodField()
    entrega_num = serializers.IntegerField(source='entrega_id', read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'num', 'fecha', 'establecimiento', 'establecimiento_id', 'zona',
            'vendedor', 'vendedor_id', 'subtotal', 'iva', 'total',
            'estado', 'estado_id', 'estado_tono', 'entrega_num', 'observaciones',
        ]
        read_only_fields = fields

    def get_establecimiento(self, obj):
        est = getattr(obj.visita, 'establecimiento', None)
        return est.nombre if est else None

    def get_establecimiento_id(self, obj):
        return getattr(obj.visita, 'establecimiento_id', None)

    def get_zona(self, obj):
        est = getattr(obj.visita, 'establecimiento', None)
        zona = getattr(est, 'zona', None) if est else None
        return zona.nombre if zona else None

    def get_vendedor(self, obj):
        return _nombre_empleado(getattr(obj.visita, 'empleado', None))

    def get_vendedor_id(self, obj):
        return getattr(obj.visita, 'empleado_id', None)

    def get_estado(self, obj):
        return obj.edo_pedido.nombre if obj.edo_pedido_id else None

    def get_estado_tono(self, obj):
        return tono(obj.edo_pedido_id)


class DetallePedidoSerializer(serializers.ModelSerializer):
    """Renglon de producto dentro de un pedido."""

    producto = serializers.CharField(source='cod_producto.nombre', read_only=True)
    producto_id = serializers.CharField(source='cod_producto_id', read_only=True)

    class Meta:
        model = DetallePedido
        fields = ['producto_id', 'producto', 'cantidad', 'precio_unitario', 'importe']
        read_only_fields = fields


class PedidoDetalleSerializer(PedidoHistorialSerializer):
    """RF44 - Pedido con sus renglones de producto."""

    detalles = DetallePedidoSerializer(many=True, read_only=True)

    class Meta(PedidoHistorialSerializer.Meta):
        fields = PedidoHistorialSerializer.Meta.fields + ['detalles']
        read_only_fields = fields


class OpcionSerializer(serializers.Serializer):
    """Elemento generico para poblar los selectores de filtro.

    'id' se declara como texto porque los catalogos del esquema usan
    llaves VARCHAR (EPD001, TP002...) mientras que zonas y empleados
    usan enteros. CharField sirve para ambos casos.
    """

    id = serializers.CharField()
    nombre = serializers.CharField()


# ---------------------------------------------------------------------------
# RF45 - Historial de entregas
# ---------------------------------------------------------------------------

class EntregaHistorialSerializer(serializers.ModelSerializer):
    """RF45 - Renglon del historial de entregas.

    total_pedidos, total_paradas y monto llegan anotados desde la vista
    mediante subconsultas, para no multiplicar filas al unir dos
    relaciones inversas distintas.
    """

    repartidor = serializers.SerializerMethodField()
    repartidor_id = serializers.IntegerField(source='empleado_id', read_only=True)
    ruta = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()
    estado_id = serializers.CharField(source='edo_entrega_id', read_only=True)
    estado_tono = serializers.SerializerMethodField()
    total_pedidos = serializers.IntegerField(read_only=True)
    total_paradas = serializers.IntegerField(read_only=True)
    monto = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True,
    )

    class Meta:
        model = Entrega
        fields = [
            'numero', 'fecha_creacion', 'fecha_entrega',
            'repartidor', 'repartidor_id', 'ruta',
            'total_pedidos', 'total_paradas', 'monto',
            'estado', 'estado_id', 'estado_tono',
        ]
        read_only_fields = fields

    def get_repartidor(self, obj):
        return _nombre_empleado(obj.empleado) if obj.empleado_id else None

    def get_ruta(self, obj):
        rutas = list(obj.rutas.all())
        return rutas[0].nombre if rutas else None

    def get_estado(self, obj):
        return obj.edo_entrega.nombre if obj.edo_entrega_id else None

    def get_estado_tono(self, obj):
        return tono(obj.edo_entrega_id)


class ParadaSerializer(serializers.ModelSerializer):
    """Confirmacion de llegada a un establecimiento."""

    establecimiento = serializers.CharField(
        source='establecimiento.nombre', read_only=True,
    )

    class Meta:
        model = EntregaEstablecimiento
        fields = ['establecimiento', 'fecha_entrega', 'hora_entrega']
        read_only_fields = fields


class EntregaDetalleSerializer(EntregaHistorialSerializer):
    """RF45 - Entrega con sus pedidos y paradas confirmadas."""

    pedidos = serializers.SerializerMethodField()
    paradas = ParadaSerializer(many=True, read_only=True)
    dias_en_ruta = serializers.SerializerMethodField()

    class Meta(EntregaHistorialSerializer.Meta):
        fields = EntregaHistorialSerializer.Meta.fields + [
            'pedidos', 'paradas', 'dias_en_ruta',
        ]
        read_only_fields = fields

    def get_pedidos(self, obj):
        return PedidoHistorialSerializer(obj.pedidos.all(), many=True).data

    def get_dias_en_ruta(self, obj):
        if not obj.fecha_entrega or not obj.fecha_creacion:
            return None
        return (obj.fecha_entrega.date() - obj.fecha_creacion).days


# ---------------------------------------------------------------------------
# RF46 - Historial de cobros
# ---------------------------------------------------------------------------

class PagoHistorialSerializer(serializers.ModelSerializer):
    """RF46 - Renglon del historial de cobros."""

    cobrador = serializers.SerializerMethodField()
    cobrador_id = serializers.IntegerField(source='empleado_id', read_only=True)
    establecimiento = serializers.CharField(
        source='establecimiento.nombre', read_only=True,
    )
    establecimiento_id = serializers.IntegerField(read_only=True)
    zona = serializers.SerializerMethodField()
    forma_pago = serializers.CharField(source='tipo_pago.nombre', read_only=True)
    forma_pago_id = serializers.CharField(source='tipo_pago_id', read_only=True)
    forma_pago_tono = serializers.SerializerMethodField()
    pedido_num = serializers.IntegerField(source='pedido_id', read_only=True)
    pedido_total = serializers.DecimalField(
        source='pedido.total', max_digits=10, decimal_places=2, read_only=True,
    )
    estado_pedido = serializers.SerializerMethodField()
    estado_pedido_tono = serializers.SerializerMethodField()

    class Meta:
        model = Pago
        fields = [
            'codigo', 'fecha', 'monto',
            'cobrador', 'cobrador_id',
            'establecimiento', 'establecimiento_id', 'zona',
            'forma_pago', 'forma_pago_id', 'forma_pago_tono',
            'pedido_num', 'pedido_total',
            'estado_pedido', 'estado_pedido_tono',
        ]
        read_only_fields = fields

    def get_cobrador(self, obj):
        return _nombre_empleado(obj.empleado) if obj.empleado_id else None

    def get_zona(self, obj):
        zona = getattr(obj.establecimiento, 'zona', None)
        return zona.nombre if zona else None

    def get_forma_pago_tono(self, obj):
        return tono(obj.tipo_pago_id)

    def get_estado_pedido(self, obj):
        edo = getattr(obj.pedido, 'edo_pedido', None)
        return edo.nombre if edo else None

    def get_estado_pedido_tono(self, obj):
        return tono(getattr(obj.pedido, 'edo_pedido_id', None))


# ---------------------------------------------------------------------------
# RF47 - Historial de devoluciones
# ---------------------------------------------------------------------------

class DetalleMovimientoSerializer(serializers.ModelSerializer):
    """Renglon de producto dentro de un movimiento de inventario."""

    producto = serializers.CharField(source='cod_producto.nombre', read_only=True)
    producto_id = serializers.CharField(source='cod_producto_id', read_only=True)

    class Meta:
        model = DetalleMovimiento
        fields = ['producto_id', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
        read_only_fields = fields


class DevolucionHistorialSerializer(serializers.ModelSerializer):
    """RF47 - Renglon del historial de devoluciones.

    unidades y valor llegan anotados desde la vista por subconsulta.
    DEVOLUCION no referencia productos: se llega a ellos a traves de
    MOVIMIENTOS -> DETALLE_MOVIMIENTO.
    """

    entrega_num = serializers.IntegerField(source='entrega_id', read_only=True)
    repartidor = serializers.SerializerMethodField()
    repartidor_id = serializers.SerializerMethodField()
    estado_entrega = serializers.SerializerMethodField()
    estado_entrega_tono = serializers.SerializerMethodField()
    fecha_entrega = serializers.SerializerMethodField()
    unidades = serializers.IntegerField(read_only=True)
    valor = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True,
    )
    productos = serializers.IntegerField(read_only=True)

    class Meta:
        model = Devolucion
        fields = [
            'codigo', 'fecha', 'cantidad', 'motivo', 'descripcion',
            'entrega_num', 'fecha_entrega',
            'repartidor', 'repartidor_id',
            'estado_entrega', 'estado_entrega_tono',
            'unidades', 'valor', 'productos',
        ]
        read_only_fields = fields

    def _entrega(self, obj):
        return obj.entrega if obj.entrega_id else None

    def get_repartidor(self, obj):
        entrega = self._entrega(obj)
        if entrega is None or not entrega.empleado_id:
            return None
        return _nombre_empleado(entrega.empleado)

    def get_repartidor_id(self, obj):
        entrega = self._entrega(obj)
        return entrega.empleado_id if entrega else None

    def get_estado_entrega(self, obj):
        entrega = self._entrega(obj)
        if entrega is None or not entrega.edo_entrega_id:
            return None
        return entrega.edo_entrega.nombre

    def get_estado_entrega_tono(self, obj):
        entrega = self._entrega(obj)
        return tono(entrega.edo_entrega_id) if entrega else None

    def get_fecha_entrega(self, obj):
        entrega = self._entrega(obj)
        return entrega.fecha_entrega if entrega else None


class MovimientoDevolucionSerializer(serializers.ModelSerializer):
    """Movimiento de inventario generado por una devolucion."""

    tipo = serializers.CharField(source='tipo_movimiento.nombre', read_only=True)
    tipo_id = serializers.CharField(source='tipo_movimiento_id', read_only=True)
    tipo_tono = serializers.SerializerMethodField()
    responsable = serializers.SerializerMethodField()
    detalles = DetalleMovimientoSerializer(many=True, read_only=True)

    class Meta:
        model = Movimiento
        fields = [
            'codigo', 'fecha', 'observaciones',
            'tipo', 'tipo_id', 'tipo_tono', 'responsable', 'detalles',
        ]
        read_only_fields = fields

    def get_tipo_tono(self, obj):
        return tono(obj.tipo_movimiento_id)

    def get_responsable(self, obj):
        return _nombre_empleado(obj.empleado) if obj.empleado_id else None


class DevolucionDetalleSerializer(DevolucionHistorialSerializer):
    """RF47 - Devolucion con los movimientos de inventario que genero."""

    movimientos = MovimientoDevolucionSerializer(many=True, read_only=True)

    class Meta(DevolucionHistorialSerializer.Meta):
        fields = DevolucionHistorialSerializer.Meta.fields + ['movimientos']
        read_only_fields = fields


# ---------------------------------------------------------------------------
# RF48 - Historial de movimientos de inventario
# ---------------------------------------------------------------------------

class MovimientoHistorialSerializer(serializers.ModelSerializer):
    """RF48 - Renglon del historial de movimientos de inventario.

    unidades, valor y productos llegan anotados desde la vista.
    'sentido' indica si el movimiento suma o resta existencias, segun el
    tipo: DETALLE_MOVIMIENTO siempre guarda cantidades positivas.
    """

    tipo = serializers.CharField(source='tipo_movimiento.nombre', read_only=True)
    tipo_id = serializers.CharField(source='tipo_movimiento_id', read_only=True)
    tipo_tono = serializers.SerializerMethodField()
    sentido = serializers.SerializerMethodField()
    responsable = serializers.SerializerMethodField()
    responsable_id = serializers.IntegerField(source='empleado_id', read_only=True)
    devolucion_num = serializers.IntegerField(source='devolucion_id', read_only=True)
    unidades = serializers.IntegerField(read_only=True)
    valor = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True,
    )
    productos = serializers.IntegerField(read_only=True)

    class Meta:
        model = Movimiento
        fields = [
            'codigo', 'fecha', 'observaciones',
            'tipo', 'tipo_id', 'tipo_tono', 'sentido',
            'responsable', 'responsable_id', 'devolucion_num',
            'unidades', 'valor', 'productos',
        ]
        read_only_fields = fields

    def get_tipo_tono(self, obj):
        return tono(obj.tipo_movimiento_id)

    def get_sentido(self, obj):
        if obj.tipo_movimiento_id in MOVIMIENTOS_ENTRADA:
            return 'entrada'
        if obj.tipo_movimiento_id in MOVIMIENTOS_SALIDA:
            return 'salida'
        return None

    def get_responsable(self, obj):
        return _nombre_empleado(obj.empleado) if obj.empleado_id else None


class MovimientoDetalleSerializer(MovimientoHistorialSerializer):
    """RF48 - Movimiento con sus renglones de producto."""

    detalles = DetalleMovimientoSerializer(many=True, read_only=True)
    devolucion_motivo = serializers.SerializerMethodField()

    class Meta(MovimientoHistorialSerializer.Meta):
        fields = MovimientoHistorialSerializer.Meta.fields + [
            'detalles', 'devolucion_motivo',
        ]
        read_only_fields = fields

    def get_devolucion_motivo(self, obj):
        return obj.devolucion.motivo if obj.devolucion_id else None


# ---------------------------------------------------------------------------
# RF49 - Estado actual de pedidos activos
# ---------------------------------------------------------------------------

class PedidoActivoSerializer(PedidoHistorialSerializer):
    """RF49 - Pedido en curso, con su antiguedad y situacion de entrega."""

    antiguedad_dias = serializers.SerializerMethodField()
    rezagado = serializers.SerializerMethodField()
    tiene_entrega = serializers.SerializerMethodField()
    estado_entrega = serializers.SerializerMethodField()
    estado_entrega_tono = serializers.SerializerMethodField()
    repartidor = serializers.SerializerMethodField()

    class Meta(PedidoHistorialSerializer.Meta):
        fields = PedidoHistorialSerializer.Meta.fields + [
            'antiguedad_dias', 'rezagado', 'tiene_entrega',
            'estado_entrega', 'estado_entrega_tono', 'repartidor',
        ]
        read_only_fields = fields

    def get_antiguedad_dias(self, obj):
        dia = fecha_local(obj.fecha)
        return (date.today() - dia).days if dia else None

    def get_rezagado(self, obj):
        dias = self.get_antiguedad_dias(obj)
        return dias is not None and dias >= DIAS_PEDIDO_REZAGADO

    def get_tiene_entrega(self, obj):
        return obj.entrega_id is not None

    def get_estado_entrega(self, obj):
        if not obj.entrega_id or not obj.entrega.edo_entrega_id:
            return None
        return obj.entrega.edo_entrega.nombre

    def get_estado_entrega_tono(self, obj):
        if not obj.entrega_id:
            return None
        return tono(obj.entrega.edo_entrega_id)

    def get_repartidor(self, obj):
        if not obj.entrega_id or not obj.entrega.empleado_id:
            return None
        return _nombre_empleado(obj.entrega.empleado)