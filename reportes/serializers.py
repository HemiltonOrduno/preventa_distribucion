"""Serializers del Modulo de Administrador (Modulo 8 - Reportes)."""

from rest_framework import serializers

from .models import DetallePedido, Pedido


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
    entrega_num = serializers.IntegerField(source='entrega_id', read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'num', 'fecha', 'establecimiento', 'establecimiento_id', 'zona',
            'vendedor', 'vendedor_id', 'subtotal', 'iva', 'total',
            'estado', 'estado_id', 'entrega_num', 'observaciones',
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