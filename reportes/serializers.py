"""Serializers del Modulo de Administrador (Modulo 8 - Reportes)."""

from rest_framework import serializers

from .catalogos import tono
from .models import DetallePedido, Entrega, EntregaEstablecimiento, Pedido


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