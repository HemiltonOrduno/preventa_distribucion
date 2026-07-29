"""Vistas del Modulo de Administrador (Modulo 8 - Reportes)."""

from datetime import datetime
from decimal import Decimal

from django.db.models import (
    Avg, Count, DecimalField, IntegerField, OuterRef, Subquery, Sum,
)
from django.db.models.functions import Coalesce
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.models import Empleado

from .catalogos import ENTREGA_COMPLETADA
from .models import (
    EdoEntrega, EdoPedido, Entrega, EntregaEstablecimiento, Pedido, Visita, Zona,
)
from .permissions import EsAdministrador
from .serializers import (
    EntregaDetalleSerializer,
    EntregaHistorialSerializer,
    OpcionSerializer,
    PedidoDetalleSerializer,
    PedidoHistorialSerializer,
)

DINERO = DecimalField(max_digits=14, decimal_places=2)


class ErrorFiltro(Exception):
    """Filtro invalido enviado por el cliente (RFN-11)."""


def _leer_fecha(request, parametro):
    crudo = request.query_params.get(parametro)
    if not crudo:
        return None
    try:
        return datetime.strptime(crudo.strip(), '%Y-%m-%d').date()
    except ValueError:
        raise ErrorFiltro(
            f"El parametro '{parametro}' debe tener el formato AAAA-MM-DD."
        )


def _leer_texto(request, parametro):
    crudo = request.query_params.get(parametro)
    return crudo.strip() if crudo else None


def _leer_entero(request, parametro):
    crudo = request.query_params.get(parametro)
    if not crudo:
        return None
    try:
        return int(crudo)
    except (TypeError, ValueError):
        raise ErrorFiltro(f"El parametro '{parametro}' debe ser un numero entero.")


class PaginacionReportes(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'tam_pagina'
    max_page_size = 200


class HistorialPedidosAPIView(ListAPIView):
    """RF44 - Historial de pedidos con filtro por fecha y por vendedor.

    GET /api/reportes/pedidos/
        ?fecha_inicio=2026-07-01&fecha_fin=2026-07-31
        &vendedor=12&estado=3&zona=2&q=abarrotes&pagina=1
    """

    permission_classes = [EsAdministrador]
    serializer_class = PedidoHistorialSerializer
    pagination_class = PaginacionReportes

    def get_queryset(self):
        consulta = (
            Pedido.objects
            .select_related(
                'visita',
                'visita__empleado',
                'visita__establecimiento',
                'visita__establecimiento__zona',
                'edo_pedido',
            )
            .order_by('-fecha', '-num')
        )

        inicio = _leer_fecha(self.request, 'fecha_inicio')
        fin = _leer_fecha(self.request, 'fecha_fin')
        if inicio and fin and inicio > fin:
            raise ErrorFiltro(
                'La fecha inicial no puede ser posterior a la fecha final.'
            )

        # pedido.fecha es DATETIME: se compara solo la parte de fecha para no
        # perder los registros capturados despues de medianoche.
        if inicio:
            consulta = consulta.filter(fecha__date__gte=inicio)
        if fin:
            consulta = consulta.filter(fecha__date__lte=fin)

        vendedor = _leer_entero(self.request, 'vendedor')
        if vendedor:
            consulta = consulta.filter(visita__empleado_id=vendedor)

        # Los catalogos del esquema usan llave VARCHAR (ej. 'EPD004').
        estado = _leer_texto(self.request, 'estado')
        if estado:
            consulta = consulta.filter(edo_pedido_id=estado)

        zona = _leer_entero(self.request, 'zona')
        if zona:
            consulta = consulta.filter(visita__establecimiento__zona_id=zona)

        texto = (self.request.query_params.get('q') or '').strip()
        if texto:
            consulta = consulta.filter(
                visita__establecimiento__nombre__icontains=texto
            )

        return consulta

    def list(self, request, *args, **kwargs):
        try:
            consulta = self.filter_queryset(self.get_queryset())
        except ErrorFiltro as error:
            return Response(
                {'error': str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        totales = consulta.aggregate(
            pedidos=Count('num'),
            monto=Sum('total'),
            promedio=Avg('total'),
        )
        resumen = {
            'pedidos': totales['pedidos'] or 0,
            'monto': totales['monto'] or Decimal('0.00'),
            'promedio': totales['promedio'] or Decimal('0.00'),
        }

        pagina = self.paginate_queryset(consulta)
        serializer = self.get_serializer(pagina, many=True)
        respuesta = self.get_paginated_response(serializer.data)
        respuesta.data['resumen'] = resumen
        return respuesta


class PedidoDetalleAPIView(RetrieveAPIView):
    """RF44 - Detalle de un pedido con sus renglones de producto."""

    permission_classes = [EsAdministrador]
    serializer_class = PedidoDetalleSerializer
    lookup_field = 'num'

    def get_queryset(self):
        return (
            Pedido.objects
            .select_related(
                'visita',
                'visita__empleado',
                'visita__establecimiento',
                'visita__establecimiento__zona',
                'edo_pedido',
            )
            .prefetch_related('detalles__cod_producto')
        )


class CatalogosFiltrosAPIView(APIView):
    """Alimenta los selectores de la pantalla de reportes."""

    permission_classes = [EsAdministrador]

    def get(self, request):
        # Solo empleados que efectivamente levantaron visitas: evita listar
        # a todo el personal en el selector de vendedor.
        con_visitas = Visita.objects.values_list('empleado_id', flat=True).distinct()
        empleados = (
            Empleado.objects
            .filter(pk__in=con_visitas)
            .order_by('apellido_paterno', 'nombre_de_pila')
        )
        vendedores = [
            {
                'id': e.pk,
                'nombre': ' '.join(
                    p for p in [
                        e.nombre_de_pila, e.apellido_paterno, e.apellido_materno
                    ] if p
                ),
            }
            for e in empleados
        ]

        con_entregas = Entrega.objects.values_list('empleado_id', flat=True).distinct()
        repartidores = [
            {
                'id': e.pk,
                'nombre': ' '.join(
                    p for p in [
                        e.nombre_de_pila, e.apellido_paterno, e.apellido_materno
                    ] if p
                ),
            }
            for e in Empleado.objects
                .filter(pk__in=con_entregas)
                .order_by('apellido_paterno', 'nombre_de_pila')
        ]

        estados_pedido = [
            {'id': e.codigo, 'nombre': e.nombre}
            for e in EdoPedido.objects.order_by('codigo')
        ]
        estados_entrega = [
            {'id': e.codigo, 'nombre': e.nombre}
            for e in EdoEntrega.objects.order_by('codigo')
        ]
        zonas = [
            {'id': z.num, 'nombre': z.nombre}
            for z in Zona.objects.order_by('nombre')
        ]

        return Response({
            'vendedores': OpcionSerializer(vendedores, many=True).data,
            'repartidores': OpcionSerializer(repartidores, many=True).data,
            'estados_pedido': OpcionSerializer(estados_pedido, many=True).data,
            'estados_entrega': OpcionSerializer(estados_entrega, many=True).data,
            'zonas': OpcionSerializer(zonas, many=True).data,
        })


# ---------------------------------------------------------------------------
# RF45 - Historial de entregas
# ---------------------------------------------------------------------------

def _entregas_anotadas():
    """Entregas con sus conteos y monto resueltos por subconsulta.

    Se usan subconsultas en lugar de Count/Sum sobre dos relaciones
    inversas distintas (pedidos y paradas), porque unir ambas
    multiplicaria las filas e inflaria los totales.
    """
    pedidos = (
        Pedido.objects
        .filter(entrega=OuterRef('pk'))
        .values('entrega')
        .annotate(n=Count('num'), m=Sum('total'))
    )
    paradas = (
        EntregaEstablecimiento.objects
        .filter(entrega=OuterRef('pk'))
        .values('entrega')
        .annotate(n=Count('establecimiento'))
    )

    return (
        Entrega.objects
        .select_related('empleado', 'edo_entrega')
        .prefetch_related('rutas')
        .annotate(
            total_pedidos=Coalesce(
                Subquery(pedidos.values('n')[:1], output_field=IntegerField()), 0
            ),
            monto=Coalesce(
                Subquery(pedidos.values('m')[:1], output_field=DINERO),
                Decimal('0.00'),
                output_field=DINERO,
            ),
            total_paradas=Coalesce(
                Subquery(paradas.values('n')[:1], output_field=IntegerField()), 0
            ),
        )
        .order_by('-fecha_creacion', '-numero')
    )


class HistorialEntregasAPIView(ListAPIView):
    """RF45 - Historial de entregas con filtro por fecha y por repartidor.

    GET /api/reportes/entregas/
        ?campo_fecha=creacion|entrega
        &fecha_inicio=2026-07-01&fecha_fin=2026-07-31
        &repartidor=8&estado=EEN004&page=1
    """

    permission_classes = [EsAdministrador]
    serializer_class = EntregaHistorialSerializer
    pagination_class = PaginacionReportes

    def _filtrar(self, consulta):
        """Aplica los filtros de la peticion a cualquier queryset de Entrega."""
        campo = (self.request.query_params.get('campo_fecha') or 'creacion').lower()
        if campo not in ('creacion', 'entrega'):
            raise ErrorFiltro(
                "El parametro 'campo_fecha' solo acepta 'creacion' o 'entrega'."
            )
        # fecha_creacion es DATE y fecha_entrega es DATETIME: __date__ funciona
        # para ambos y evita perder registros posteriores a medianoche.
        columna = 'fecha_creacion' if campo == 'creacion' else 'fecha_entrega'

        inicio = _leer_fecha(self.request, 'fecha_inicio')
        fin = _leer_fecha(self.request, 'fecha_fin')
        if inicio and fin and inicio > fin:
            raise ErrorFiltro(
                'La fecha inicial no puede ser posterior a la fecha final.'
            )
        if inicio:
            consulta = consulta.filter(**{columna + '__date__gte': inicio})
        if fin:
            consulta = consulta.filter(**{columna + '__date__lte': fin})

        repartidor = _leer_entero(self.request, 'repartidor')
        if repartidor:
            consulta = consulta.filter(empleado_id=repartidor)

        estado = _leer_texto(self.request, 'estado')
        if estado:
            consulta = consulta.filter(edo_entrega_id=estado)

        return consulta

    def get_queryset(self):
        return self._filtrar(_entregas_anotadas())

    def _resumen(self):
        """Totales del periodo.

        Se calculan sobre un queryset SIN anotaciones: MySQL no admite
        aplicar SUM() sobre el alias de una subconsulta en el mismo nivel
        del SELECT (error 1054, Unknown column). Los conteos de pedidos y
        el monto se piden directamente a PEDIDO, acotado a las entregas
        que quedaron dentro del filtro.
        """
        plano = self._filtrar(Entrega.objects.all())

        de_pedidos = (
            Pedido.objects
            .filter(entrega__in=plano)
            .aggregate(cantidad=Count('num'), monto=Sum('total'))
        )

        return {
            'entregas': plano.count(),
            'completadas': plano.filter(
                edo_entrega_id=ENTREGA_COMPLETADA
            ).count(),
            'pedidos': de_pedidos['cantidad'] or 0,
            'monto': de_pedidos['monto'] or Decimal('0.00'),
        }

    def list(self, request, *args, **kwargs):
        try:
            consulta = self.filter_queryset(self.get_queryset())
            resumen = self._resumen()
        except ErrorFiltro as error:
            return Response(
                {'error': str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        pagina = self.paginate_queryset(consulta)
        serializer = self.get_serializer(pagina, many=True)
        respuesta = self.get_paginated_response(serializer.data)
        respuesta.data['resumen'] = resumen
        return respuesta


class EntregaDetalleAPIView(RetrieveAPIView):
    """RF45 - Detalle de una entrega con sus pedidos y paradas."""

    permission_classes = [EsAdministrador]
    serializer_class = EntregaDetalleSerializer
    lookup_field = 'numero'

    def get_queryset(self):
        return _entregas_anotadas().prefetch_related(
            'pedidos__visita__empleado',
            'pedidos__visita__establecimiento__zona',
            'pedidos__edo_pedido',
            'paradas__establecimiento',
        )


class HistorialPedidosPantalla(TemplateView):
    """Sirve la interfaz del RF44."""

    template_name = 'reportes/historial_pedidos.html'
    extra_context = {'seccion': 'pedidos'}


class HistorialEntregasPantalla(TemplateView):
    """Sirve la interfaz del RF45."""

    template_name = 'reportes/historial_entregas.html'
    extra_context = {'seccion': 'entregas'}