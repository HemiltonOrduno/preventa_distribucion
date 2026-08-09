"""Vistas del Modulo de Administrador (Modulo 8 - Reportes)."""

from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.conf import settings
from django.db.models import (
    Avg, Count, DecimalField, IntegerField, Max, OuterRef, Q, Subquery, Sum,
)
from django.db.models.functions import (
    Coalesce, TruncDate, TruncMonth, TruncWeek,
)
from django.utils import timezone
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.models import Empleado

from .catalogos import (
    DIAS_PEDIDO_REZAGADO, ENTREGA_COMPLETADA, MOVIMIENTOS_ENTRADA,
    MOVIMIENTOS_SALIDA, PAGO_EFECTIVO, PAGO_TARJETA, PEDIDOS_ACTIVOS,
    PEDIDO_CANCELADO, PEDIDO_ENTREGADO, tono,
)
from .models import (
    DetalleMovimiento, DetallePedido, Devolucion, EdoEntrega, EdoPedido,
    Entrega, Establecimiento, EntregaEstablecimiento, Movimiento, Pago,
    Pedido, Producto, TipoMovimiento, TipoPago, Visita, Zona,
)
from .permissions import EsAdministrador
from .serializers import (
    fecha_local,
    PedidoActivoSerializer,
    MovimientoDetalleSerializer,
    MovimientoHistorialSerializer,
    DevolucionDetalleSerializer,
    DevolucionHistorialSerializer,
    EntregaDetalleSerializer,
    EntregaHistorialSerializer,
    OpcionSerializer,
    PagoHistorialSerializer,
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


def _inicio_del_dia(fecha):
    """Primer instante de un dia, respetando USE_TZ.

    Se evita a proposito el lookup __date de Django: en MySQL genera
    CONVERT_TZ(), y si el servidor no tiene cargadas las tablas de zonas
    horarias (caso tipico de XAMPP) esa funcion devuelve NULL y el filtro
    deja de coincidir con nada, sin lanzar ningun error.
    """
    momento = datetime.combine(fecha, time.min)
    if settings.USE_TZ:
        momento = timezone.make_aware(momento, timezone.get_current_timezone())
    return momento


def _fin_del_dia(fecha):
    """Ultimo instante de un dia, respetando USE_TZ."""
    momento = datetime.combine(fecha, time.max)
    if settings.USE_TZ:
        momento = timezone.make_aware(momento, timezone.get_current_timezone())
    return momento


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

        # pedido.fecha es DATETIME: se acota por instante inicial y final
        # del dia para incluir lo capturado despues de medianoche.
        if inicio:
            consulta = consulta.filter(fecha__gte=_inicio_del_dia(inicio))
        if fin:
            consulta = consulta.filter(fecha__lte=_fin_del_dia(fin))

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

        con_cobros = Pago.objects.values_list('empleado_id', flat=True).distinct()
        cobradores = [
            {
                'id': e.pk,
                'nombre': ' '.join(
                    p for p in [
                        e.nombre_de_pila, e.apellido_paterno, e.apellido_materno
                    ] if p
                ),
            }
            for e in Empleado.objects
                .filter(pk__in=con_cobros)
                .order_by('apellido_paterno', 'nombre_de_pila')
        ]

        formas_pago = [
            {'id': t.codigo, 'nombre': t.nombre}
            for t in TipoPago.objects.order_by('codigo')
        ]

        # Los motivos son texto libre en DEVOLUCION: se ofrecen los que
        # existen realmente en vez de un catalogo fijo.
        motivos = [
            {'id': m, 'nombre': m}
            for m in Devolucion.objects
                .exclude(motivo__isnull=True)
                .exclude(motivo__exact='')
                .values_list('motivo', flat=True)
                .distinct()
                .order_by('motivo')
        ]

        con_movimientos = (
            Movimiento.objects.values_list('empleado_id', flat=True).distinct()
        )
        responsables = [
            {
                'id': e.pk,
                'nombre': ' '.join(
                    p for p in [
                        e.nombre_de_pila, e.apellido_paterno, e.apellido_materno
                    ] if p
                ),
            }
            for e in Empleado.objects
                .filter(pk__in=con_movimientos)
                .order_by('apellido_paterno', 'nombre_de_pila')
        ]

        tipos_movimiento = [
            {'id': t.codigo, 'nombre': t.nombre}
            for t in TipoMovimiento.objects.order_by('codigo')
        ]

        productos = [
            {'id': p.codigo, 'nombre': p.nombre}
            for p in Producto.objects.order_by('nombre')
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
            'cobradores': OpcionSerializer(cobradores, many=True).data,
            'formas_pago': OpcionSerializer(formas_pago, many=True).data,
            'motivos': OpcionSerializer(motivos, many=True).data,
            'responsables': OpcionSerializer(responsables, many=True).data,
            'tipos_movimiento': OpcionSerializer(tipos_movimiento, many=True).data,
            'productos': OpcionSerializer(productos, many=True).data,
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
        columna = 'fecha_creacion' if campo == 'creacion' else 'fecha_entrega'
        # fecha_creacion es DATE y fecha_entrega es DATETIME. Para la
        # primera basta comparar fechas; para la segunda hacen falta los
        # limites del dia.
        es_datetime = columna == 'fecha_entrega'

        inicio = _leer_fecha(self.request, 'fecha_inicio')
        fin = _leer_fecha(self.request, 'fecha_fin')
        if inicio and fin and inicio > fin:
            raise ErrorFiltro(
                'La fecha inicial no puede ser posterior a la fecha final.'
            )
        if inicio:
            consulta = consulta.filter(**{
                columna + '__gte': _inicio_del_dia(inicio) if es_datetime else inicio
            })
        if fin:
            consulta = consulta.filter(**{
                columna + '__lte': _fin_del_dia(fin) if es_datetime else fin
            })

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


# ---------------------------------------------------------------------------
# RF46 - Historial de cobros
# ---------------------------------------------------------------------------

class HistorialCobrosAPIView(ListAPIView):
    """RF46 - Historial de cobros con filtro por fecha y por usuario.

    GET /api/reportes/cobros/
        ?fecha_inicio=2026-07-01&fecha_fin=2026-07-31
        &cobrador=8&forma_pago=TP001&zona=2&q=abarrotes&page=1

    El desglose por forma de pago que exige el RF55 se adelanta aqui en
    el bloque 'resumen', porque es el mismo universo de datos.
    """

    permission_classes = [EsAdministrador]
    serializer_class = PagoHistorialSerializer
    pagination_class = PaginacionReportes

    def _filtrar(self, consulta):
        inicio = _leer_fecha(self.request, 'fecha_inicio')
        fin = _leer_fecha(self.request, 'fecha_fin')
        if inicio and fin and inicio > fin:
            raise ErrorFiltro(
                'La fecha inicial no puede ser posterior a la fecha final.'
            )
        # pago.fecha es DATETIME.
        if inicio:
            consulta = consulta.filter(fecha__gte=_inicio_del_dia(inicio))
        if fin:
            consulta = consulta.filter(fecha__lte=_fin_del_dia(fin))

        cobrador = _leer_entero(self.request, 'cobrador')
        if cobrador:
            consulta = consulta.filter(empleado_id=cobrador)

        forma = _leer_texto(self.request, 'forma_pago')
        if forma:
            consulta = consulta.filter(tipo_pago_id=forma)

        zona = _leer_entero(self.request, 'zona')
        if zona:
            consulta = consulta.filter(establecimiento__zona_id=zona)

        texto = (self.request.query_params.get('q') or '').strip()
        if texto:
            consulta = consulta.filter(establecimiento__nombre__icontains=texto)

        return consulta

    def get_queryset(self):
        return self._filtrar(
            Pago.objects
            .select_related(
                'empleado',
                'tipo_pago',
                'establecimiento',
                'establecimiento__zona',
                'pedido',
                'pedido__edo_pedido',
            )
            .order_by('-fecha', '-codigo')
        )

    def _resumen(self, consulta):
        totales = consulta.aggregate(
            cobros=Count('codigo'), monto=Sum('monto'),
        )

        # Desglose por forma de pago (RF55).
        desglose = []
        agrupado = (
            consulta
            .values('tipo_pago_id', 'tipo_pago__nombre')
            .annotate(cobros=Count('codigo'), monto=Sum('monto'))
            .order_by('-monto')
        )
        total_monto = totales['monto'] or Decimal('0.00')
        for fila in agrupado:
            monto = fila['monto'] or Decimal('0.00')
            porcentaje = (
                float(monto) / float(total_monto) * 100 if total_monto else 0.0
            )
            desglose.append({
                'forma_pago_id': fila['tipo_pago_id'],
                'forma_pago': fila['tipo_pago__nombre'],
                'tono': tono(fila['tipo_pago_id']),
                'cobros': fila['cobros'],
                'monto': monto,
                'porcentaje': round(porcentaje, 1),
            })

        return {
            'cobros': totales['cobros'] or 0,
            'monto': total_monto,
            'promedio': (
                total_monto / totales['cobros'] if totales['cobros'] else Decimal('0.00')
            ),
            'desglose': desglose,
        }

    def list(self, request, *args, **kwargs):
        try:
            consulta = self.filter_queryset(self.get_queryset())
            resumen = self._resumen(consulta)
        except ErrorFiltro as error:
            return Response(
                {'error': str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        pagina = self.paginate_queryset(consulta)
        serializer = self.get_serializer(pagina, many=True)
        respuesta = self.get_paginated_response(serializer.data)
        respuesta.data['resumen'] = resumen
        return respuesta


# ---------------------------------------------------------------------------
# RF47 - Historial de devoluciones
# ---------------------------------------------------------------------------

def _devoluciones_anotadas():
    """Devoluciones con unidades, valor y numero de productos.

    DEVOLUCION no guarda que se devolvio: el detalle vive en
    DETALLE_MOVIMIENTO, alcanzable via MOVIMIENTOS.devolucion. Se resuelve
    por subconsulta para no multiplicar filas.
    """
    detalle = (
        DetalleMovimiento.objects
        .filter(cod_movimiento__devolucion=OuterRef('pk'))
        .values('cod_movimiento__devolucion')
        .annotate(
            u=Sum('cantidad'),
            v=Sum('subtotal'),
            p=Count('cod_producto', distinct=True),
        )
    )

    return (
        Devolucion.objects
        .select_related('entrega', 'entrega__empleado', 'entrega__edo_entrega')
        .annotate(
            unidades=Coalesce(
                Subquery(detalle.values('u')[:1], output_field=IntegerField()), 0
            ),
            valor=Coalesce(
                Subquery(detalle.values('v')[:1], output_field=DINERO),
                Decimal('0.00'),
                output_field=DINERO,
            ),
            productos=Coalesce(
                Subquery(detalle.values('p')[:1], output_field=IntegerField()), 0
            ),
        )
        .order_by('-fecha', '-codigo')
    )


class HistorialDevolucionesAPIView(ListAPIView):
    """RF47 - Historial de devoluciones con filtro por fecha y por usuario.

    GET /api/reportes/devoluciones/
        ?fecha_inicio=2026-07-01&fecha_fin=2026-07-31
        &repartidor=8&motivo=Producto+danado&entrega=7&page=1
    """

    permission_classes = [EsAdministrador]
    serializer_class = DevolucionHistorialSerializer
    pagination_class = PaginacionReportes

    def _filtrar(self, consulta):
        inicio = _leer_fecha(self.request, 'fecha_inicio')
        fin = _leer_fecha(self.request, 'fecha_fin')
        if inicio and fin and inicio > fin:
            raise ErrorFiltro(
                'La fecha inicial no puede ser posterior a la fecha final.'
            )
        # devolucion.fecha es DATE, no DATETIME.
        if inicio:
            consulta = consulta.filter(fecha__gte=inicio)
        if fin:
            consulta = consulta.filter(fecha__lte=fin)

        repartidor = _leer_entero(self.request, 'repartidor')
        if repartidor:
            consulta = consulta.filter(entrega__empleado_id=repartidor)

        entrega = _leer_entero(self.request, 'entrega')
        if entrega:
            consulta = consulta.filter(entrega_id=entrega)

        motivo = _leer_texto(self.request, 'motivo')
        if motivo:
            consulta = consulta.filter(motivo__icontains=motivo)

        return consulta

    def get_queryset(self):
        return self._filtrar(_devoluciones_anotadas())

    def _resumen(self):
        plano = self._filtrar(Devolucion.objects.all())

        del_inventario = (
            DetalleMovimiento.objects
            .filter(cod_movimiento__devolucion__in=plano)
            .aggregate(unidades=Sum('cantidad'), valor=Sum('subtotal'))
        )

        # Motivo mas frecuente del periodo.
        top = (
            plano
            .exclude(motivo__isnull=True)
            .exclude(motivo__exact='')
            .values('motivo')
            .annotate(veces=Count('codigo'))
            .order_by('-veces')
            .first()
        )

        return {
            'devoluciones': plano.count(),
            'unidades': del_inventario['unidades'] or 0,
            'valor': del_inventario['valor'] or Decimal('0.00'),
            'motivo_frecuente': top['motivo'] if top else None,
            'motivo_frecuente_veces': top['veces'] if top else 0,
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


class DevolucionDetalleAPIView(RetrieveAPIView):
    """RF47 - Devolucion con los movimientos de inventario que genero."""

    permission_classes = [EsAdministrador]
    serializer_class = DevolucionDetalleSerializer
    lookup_field = 'codigo'

    def get_queryset(self):
        return _devoluciones_anotadas().prefetch_related(
            'movimientos__tipo_movimiento',
            'movimientos__empleado',
            'movimientos__detalles__cod_producto',
        )


# ---------------------------------------------------------------------------
# RF48 - Historial de movimientos de inventario
# ---------------------------------------------------------------------------

def _movimientos_anotados():
    """Movimientos con unidades, valor y numero de productos distintos."""
    detalle = (
        DetalleMovimiento.objects
        .filter(cod_movimiento=OuterRef('pk'))
        .values('cod_movimiento')
        .annotate(
            u=Sum('cantidad'),
            v=Sum('subtotal'),
            p=Count('cod_producto', distinct=True),
        )
    )

    return (
        Movimiento.objects
        .select_related('tipo_movimiento', 'empleado', 'devolucion')
        .annotate(
            unidades=Coalesce(
                Subquery(detalle.values('u')[:1], output_field=IntegerField()), 0
            ),
            valor=Coalesce(
                Subquery(detalle.values('v')[:1], output_field=DINERO),
                Decimal('0.00'),
                output_field=DINERO,
            ),
            productos=Coalesce(
                Subquery(detalle.values('p')[:1], output_field=IntegerField()), 0
            ),
        )
        .order_by('-fecha', '-codigo')
    )


class HistorialMovimientosAPIView(ListAPIView):
    """RF48 - Historial de movimientos de inventario.

    GET /api/reportes/movimientos/
        ?fecha_inicio=2026-07-01&fecha_fin=2026-07-31
        &responsable=8&tipo=TM003&producto=P0012&sentido=salida&page=1
    """

    permission_classes = [EsAdministrador]
    serializer_class = MovimientoHistorialSerializer
    pagination_class = PaginacionReportes

    def _filtrar(self, consulta):
        inicio = _leer_fecha(self.request, 'fecha_inicio')
        fin = _leer_fecha(self.request, 'fecha_fin')
        if inicio and fin and inicio > fin:
            raise ErrorFiltro(
                'La fecha inicial no puede ser posterior a la fecha final.'
            )
        # movimientos.fecha es DATETIME.
        if inicio:
            consulta = consulta.filter(fecha__gte=_inicio_del_dia(inicio))
        if fin:
            consulta = consulta.filter(fecha__lte=_fin_del_dia(fin))

        responsable = _leer_entero(self.request, 'responsable')
        if responsable:
            consulta = consulta.filter(empleado_id=responsable)

        tipo = _leer_texto(self.request, 'tipo')
        if tipo:
            consulta = consulta.filter(tipo_movimiento_id=tipo)

        sentido = (_leer_texto(self.request, 'sentido') or '').lower()
        if sentido == 'entrada':
            consulta = consulta.filter(tipo_movimiento_id__in=MOVIMIENTOS_ENTRADA)
        elif sentido == 'salida':
            consulta = consulta.filter(tipo_movimiento_id__in=MOVIMIENTOS_SALIDA)
        elif sentido:
            raise ErrorFiltro(
                "El parametro 'sentido' solo acepta 'entrada' o 'salida'."
            )

        producto = _leer_texto(self.request, 'producto')
        if producto:
            # distinct() porque un movimiento puede tener varios renglones.
            consulta = consulta.filter(
                detalles__cod_producto_id=producto
            ).distinct()

        return consulta

    def get_queryset(self):
        return self._filtrar(_movimientos_anotados())

    def _resumen(self):
        plano = self._filtrar(Movimiento.objects.all())

        def sumar(codigos):
            datos = (
                DetalleMovimiento.objects
                .filter(
                    cod_movimiento__in=plano,
                    cod_movimiento__tipo_movimiento_id__in=codigos,
                )
                .aggregate(u=Sum('cantidad'), v=Sum('subtotal'))
            )
            return (datos['u'] or 0, datos['v'] or Decimal('0.00'))

        entradas_u, entradas_v = sumar(MOVIMIENTOS_ENTRADA)
        salidas_u, salidas_v = sumar(MOVIMIENTOS_SALIDA)

        return {
            'movimientos': plano.count(),
            'entradas': entradas_u,
            'salidas': salidas_u,
            'valor_entradas': entradas_v,
            'valor_salidas': salidas_v,
            'neto': entradas_u - salidas_u,
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


class MovimientoDetalleAPIView(RetrieveAPIView):
    """RF48 - Movimiento con sus renglones de producto."""

    permission_classes = [EsAdministrador]
    serializer_class = MovimientoDetalleSerializer
    lookup_field = 'codigo'

    def get_queryset(self):
        return _movimientos_anotados().prefetch_related('detalles__cod_producto')


# ---------------------------------------------------------------------------
# RF49 - Estado actual de pedidos activos
# ---------------------------------------------------------------------------

class PedidosActivosAPIView(ListAPIView):
    """RF49 - Monitor de pedidos que siguen en curso.

    GET /api/reportes/pedidos-activos/
        ?estado=EPD004&zona=2&vendedor=8&sin_entrega=1&rezagados=1&page=1

    A diferencia de los RF44-RF48 este no es un historico: no recibe rango
    de fechas porque siempre refleja la situacion del momento. El universo
    son los pedidos que no estan entregados ni cancelados.
    """

    permission_classes = [EsAdministrador]
    serializer_class = PedidoActivoSerializer
    pagination_class = PaginacionReportes

    def _filtrar(self, consulta):
        consulta = consulta.filter(edo_pedido_id__in=PEDIDOS_ACTIVOS)

        estado = _leer_texto(self.request, 'estado')
        if estado:
            if estado not in PEDIDOS_ACTIVOS:
                raise ErrorFiltro(
                    'Ese estado no corresponde a un pedido activo.'
                )
            consulta = consulta.filter(edo_pedido_id=estado)

        zona = _leer_entero(self.request, 'zona')
        if zona:
            consulta = consulta.filter(visita__establecimiento__zona_id=zona)

        vendedor = _leer_entero(self.request, 'vendedor')
        if vendedor:
            consulta = consulta.filter(visita__empleado_id=vendedor)

        if self.request.query_params.get('sin_entrega') in ('1', 'true', 'si'):
            consulta = consulta.filter(entrega__isnull=True)

        if self.request.query_params.get('rezagados') in ('1', 'true', 'si'):
            corte = date.today() - timedelta(days=DIAS_PEDIDO_REZAGADO)
            consulta = consulta.filter(fecha__lte=_fin_del_dia(corte))

        return consulta

    def get_queryset(self):
        # Ascendente a proposito: lo mas viejo primero, que es lo que
        # requiere atencion en un monitor de operacion.
        return self._filtrar(
            Pedido.objects
            .select_related(
                'visita',
                'visita__empleado',
                'visita__establecimiento',
                'visita__establecimiento__zona',
                'edo_pedido',
                'entrega',
                'entrega__empleado',
                'entrega__edo_entrega',
            )
            .order_by('fecha', 'num')
        )

    def _resumen(self):
        plano = self._filtrar(Pedido.objects.all())
        corte = date.today() - timedelta(days=DIAS_PEDIDO_REZAGADO)

        # Conteo por estado, incluyendo los que quedaron en cero para que
        # el tablero no cambie de forma entre consultas.
        conteos = dict(
            plano.values_list('edo_pedido_id')
                 .annotate(n=Count('num'))
                 .values_list('edo_pedido_id', 'n')
        )
        etiquetas = dict(
            EdoPedido.objects
            .filter(codigo__in=PEDIDOS_ACTIVOS)
            .values_list('codigo', 'nombre')
        )
        por_estado = [
            {
                'estado_id': codigo,
                'estado': etiquetas.get(codigo, codigo),
                'tono': tono(codigo),
                'pedidos': conteos.get(codigo, 0),
            }
            for codigo in PEDIDOS_ACTIVOS
        ]

        totales = plano.aggregate(pedidos=Count('num'), monto=Sum('total'))
        mas_viejo = plano.order_by('fecha').values_list('fecha', flat=True).first()

        return {
            'pedidos': totales['pedidos'] or 0,
            'monto': totales['monto'] or Decimal('0.00'),
            'sin_entrega': plano.filter(entrega__isnull=True).count(),
            'rezagados': plano.filter(fecha__lte=_fin_del_dia(corte)).count(),
            'dias_umbral': DIAS_PEDIDO_REZAGADO,
            'antiguedad_maxima': (
                (date.today() - fecha_local(mas_viejo)).days
                if mas_viejo else 0
            ),
            'por_estado': por_estado,
            # Marca de hora del servidor. datetime.now() (naive, hora
            # local) sirve en ambas configuraciones de USE_TZ; el frontend
            # solo la muestra, no opera con ella.
            'actualizado': datetime.now().isoformat(timespec='seconds'),
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


# ---------------------------------------------------------------------------
# RF50 - Reporte de volumen de pedidos por periodo
# ---------------------------------------------------------------------------

AGRUPACIONES = {
    'dia': (TruncDate, '%d %b'),
    'semana': (TruncWeek, 'Sem. %d %b'),
    'mes': (TruncMonth, '%b %Y'),
}

MESES_ES = {
    1: 'ene', 2: 'feb', 3: 'mar', 4: 'abr', 5: 'may', 6: 'jun',
    7: 'jul', 8: 'ago', 9: 'sep', 10: 'oct', 11: 'nov', 12: 'dic',
}


def _etiqueta_periodo(valor, agrupacion):
    """Etiqueta corta y legible en espanol para el eje de la grafica."""
    if valor is None:
        return 'Sin fecha'
    if hasattr(valor, 'date'):
        valor = valor.date()
    if agrupacion == 'mes':
        return '{} {}'.format(MESES_ES[valor.month], valor.year)
    if agrupacion == 'semana':
        return 'Sem. {} {}'.format(valor.day, MESES_ES[valor.month])
    return '{} {}'.format(valor.day, MESES_ES[valor.month])


class VolumenPedidosAPIView(APIView):
    """RF50 - Volumen de pedidos agrupado por periodo.

    GET /api/reportes/volumen-pedidos/
        ?fecha_inicio=2026-07-01&fecha_fin=2026-07-31
        &agrupacion=dia|semana|mes&zona=2&vendedor=8

    Reporte agregado: no se pagina, porque el numero de periodos es
    acotado por definicion y la grafica necesita la serie completa.
    """

    permission_classes = [EsAdministrador]

    def get(self, request):
        try:
            agrupacion = (request.query_params.get('agrupacion') or 'dia').lower()
            if agrupacion not in AGRUPACIONES:
                raise ErrorFiltro(
                    "El parametro 'agrupacion' solo acepta 'dia', 'semana' o 'mes'."
                )

            inicio = _leer_fecha(request, 'fecha_inicio')
            fin = _leer_fecha(request, 'fecha_fin')
            if inicio and fin and inicio > fin:
                raise ErrorFiltro(
                    'La fecha inicial no puede ser posterior a la fecha final.'
                )

            consulta = Pedido.objects.all()
            if inicio:
                consulta = consulta.filter(fecha__gte=_inicio_del_dia(inicio))
            if fin:
                consulta = consulta.filter(fecha__lte=_fin_del_dia(fin))

            zona = _leer_entero(request, 'zona')
            if zona:
                consulta = consulta.filter(visita__establecimiento__zona_id=zona)

            vendedor = _leer_entero(request, 'vendedor')
            if vendedor:
                consulta = consulta.filter(visita__empleado_id=vendedor)

        except ErrorFiltro as error:
            return Response(
                {'error': str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        truncador = AGRUPACIONES[agrupacion][0]
        agrupado = (
            consulta
            .annotate(periodo=truncador('fecha'))
            .values('periodo')
            .annotate(
                pedidos=Count('num'),
                monto=Sum('total'),
                promedio=Avg('total'),
                entregados=Count('num', filter=Q(edo_pedido_id=PEDIDO_ENTREGADO)),
                cancelados=Count('num', filter=Q(edo_pedido_id=PEDIDO_CANCELADO)),
            )
            .order_by('periodo')
        )

        periodos = [
            {
                'periodo': fila['periodo'],
                'etiqueta': _etiqueta_periodo(fila['periodo'], agrupacion),
                'pedidos': fila['pedidos'],
                'monto': fila['monto'] or Decimal('0.00'),
                'promedio': fila['promedio'] or Decimal('0.00'),
                'entregados': fila['entregados'],
                'cancelados': fila['cancelados'],
            }
            for fila in agrupado
        ]

        totales = consulta.aggregate(
            pedidos=Count('num'),
            monto=Sum('total'),
            promedio=Avg('total'),
            entregados=Count('num', filter=Q(edo_pedido_id=PEDIDO_ENTREGADO)),
            cancelados=Count('num', filter=Q(edo_pedido_id=PEDIDO_CANCELADO)),
        )

        pico = max(periodos, key=lambda p: p['pedidos']) if periodos else None

        return Response({
            'agrupacion': agrupacion,
            'periodos': periodos,
            'resumen': {
                'pedidos': totales['pedidos'] or 0,
                'monto': totales['monto'] or Decimal('0.00'),
                'promedio': totales['promedio'] or Decimal('0.00'),
                'entregados': totales['entregados'] or 0,
                'cancelados': totales['cancelados'] or 0,
                'num_periodos': len(periodos),
                'pico_etiqueta': pico['etiqueta'] if pico else None,
                'pico_pedidos': pico['pedidos'] if pico else 0,
                'media_por_periodo': (
                    round((totales['pedidos'] or 0) / len(periodos), 1)
                    if periodos else 0
                ),
            },
        })


# ---------------------------------------------------------------------------
# RF51 - Reporte de ventas por vendedor
# ---------------------------------------------------------------------------

class VentasPorVendedorAPIView(APIView):
    """RF51 - Ventas agrupadas por vendedor.

    GET /api/reportes/ventas-vendedor/
        ?fecha_inicio=2026-07-01&fecha_fin=2026-07-31&zona=2&orden=monto

    No se apoya en la vista vta_reporte_ventas_admin porque esa agrupa por
    zona y periodo, y expone el vendedor como nombre concatenado sin id:
    no permite enlazar de forma confiable con EMPLEADO ni desglosar la
    efectividad de visita que pide un reporte de desempeno comercial.
    """

    permission_classes = [EsAdministrador]

    ORDENES = {
        'monto': '-monto',
        'pedidos': '-pedidos',
        'promedio': '-promedio',
        'nombre': 'nombre',
    }

    def get(self, request):
        try:
            inicio = _leer_fecha(request, 'fecha_inicio')
            fin = _leer_fecha(request, 'fecha_fin')
            if inicio and fin and inicio > fin:
                raise ErrorFiltro(
                    'La fecha inicial no puede ser posterior a la fecha final.'
                )

            orden = (request.query_params.get('orden') or 'monto').lower()
            if orden not in self.ORDENES:
                raise ErrorFiltro(
                    "El parametro 'orden' acepta 'monto', 'pedidos', "
                    "'promedio' o 'nombre'."
                )

            zona = _leer_entero(request, 'zona')

        except ErrorFiltro as error:
            return Response(
                {'error': str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        pedidos = Pedido.objects.all()
        visitas = Visita.objects.all()

        if inicio:
            pedidos = pedidos.filter(fecha__gte=_inicio_del_dia(inicio))
            visitas = visitas.filter(fecha__gte=_inicio_del_dia(inicio))
        if fin:
            pedidos = pedidos.filter(fecha__lte=_fin_del_dia(fin))
            visitas = visitas.filter(fecha__lte=_fin_del_dia(fin))
        if zona:
            pedidos = pedidos.filter(visita__establecimiento__zona_id=zona)
            visitas = visitas.filter(establecimiento__zona_id=zona)

        agrupado = (
            pedidos
            .values('visita__empleado_id')
            .annotate(
                pedidos=Count('num'),
                monto=Sum('total'),
                promedio=Avg('total'),
                entregados=Count('num', filter=Q(edo_pedido_id=PEDIDO_ENTREGADO)),
                cancelados=Count('num', filter=Q(edo_pedido_id=PEDIDO_CANCELADO)),
                establecimientos=Count(
                    'visita__establecimiento_id', distinct=True
                ),
            )
        )

        # Las visitas se cuentan aparte: unirlas en la misma consulta
        # multiplicaria filas contra PEDIDO e inflaria los totales.
        conteo_visitas = dict(
            visitas.values_list('empleado_id')
                   .annotate(n=Count('numero'))
                   .values_list('empleado_id', 'n')
        )

        identificadores = [f['visita__empleado_id'] for f in agrupado]
        empleados = {
            e.pk: ' '.join(
                p for p in [
                    e.nombre_de_pila, e.apellido_paterno, e.apellido_materno
                ] if p
            )
            for e in Empleado.objects.filter(pk__in=identificadores)
        }

        filas = []
        for fila in agrupado:
            identificador = fila['visita__empleado_id']
            hechas = conteo_visitas.get(identificador, 0)
            colocados = fila['pedidos']
            filas.append({
                'vendedor_id': identificador,
                'nombre': empleados.get(identificador, 'Sin asignar'),
                'pedidos': colocados,
                'monto': fila['monto'] or Decimal('0.00'),
                'promedio': fila['promedio'] or Decimal('0.00'),
                'entregados': fila['entregados'],
                'cancelados': fila['cancelados'],
                'establecimientos': fila['establecimientos'],
                'visitas': hechas,
                # Que porcentaje de las visitas termino en pedido.
                'efectividad': (
                    round(colocados / hechas * 100, 1) if hechas else None
                ),
                'cumplimiento': (
                    round(fila['entregados'] / colocados * 100, 1)
                    if colocados else 0
                ),
            })

        clave = self.ORDENES[orden]
        descendente = clave.startswith('-')
        campo = clave.lstrip('-')
        filas.sort(key=lambda f: f[campo], reverse=descendente)

        for posicion, fila in enumerate(filas, start=1):
            fila['posicion'] = posicion

        totales = pedidos.aggregate(
            pedidos=Count('num'),
            monto=Sum('total'),
            promedio=Avg('total'),
        )
        lider = filas[0] if filas else None

        return Response({
            'vendedores': filas,
            'orden': orden,
            'resumen': {
                'vendedores': len(filas),
                'pedidos': totales['pedidos'] or 0,
                'monto': totales['monto'] or Decimal('0.00'),
                'promedio': totales['promedio'] or Decimal('0.00'),
                'visitas': sum(conteo_visitas.values()),
                'lider_nombre': lider['nombre'] if lider else None,
                'lider_monto': lider['monto'] if lider else Decimal('0.00'),
            },
        })


# ---------------------------------------------------------------------------
# RF52 - Reporte de ventas por cliente
# ---------------------------------------------------------------------------

class VentasPorClienteAPIView(APIView):
    """RF52 - Ventas agrupadas por establecimiento.

    GET /api/reportes/ventas-cliente/
        ?fecha_inicio=2026-07-01&fecha_fin=2026-07-31
        &zona=2&vendedor=8&orden=monto&sin_compras=1

    Con sin_compras=1 se agregan los establecimientos que no registraron
    ningun pedido en el rango. Es informacion que no existe en PEDIDO
    (justamente porque no hay pedido) y que un reporte de clientes
    necesita para detectar cartera dormida.
    """

    permission_classes = [EsAdministrador]

    ORDENES = {
        'monto': '-monto',
        'pedidos': '-pedidos',
        'promedio': '-promedio',
        'reciente': '-dias_sin_comprar',
        'nombre': 'nombre',
    }

    def get(self, request):
        try:
            inicio = _leer_fecha(request, 'fecha_inicio')
            fin = _leer_fecha(request, 'fecha_fin')
            if inicio and fin and inicio > fin:
                raise ErrorFiltro(
                    'La fecha inicial no puede ser posterior a la fecha final.'
                )

            orden = (request.query_params.get('orden') or 'monto').lower()
            if orden not in self.ORDENES:
                raise ErrorFiltro(
                    "El parametro 'orden' acepta 'monto', 'pedidos', "
                    "'promedio', 'reciente' o 'nombre'."
                )

            zona = _leer_entero(request, 'zona')
            vendedor = _leer_entero(request, 'vendedor')

        except ErrorFiltro as error:
            return Response(
                {'error': str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        pedidos = Pedido.objects.all()
        if inicio:
            pedidos = pedidos.filter(fecha__gte=_inicio_del_dia(inicio))
        if fin:
            pedidos = pedidos.filter(fecha__lte=_fin_del_dia(fin))
        if zona:
            pedidos = pedidos.filter(visita__establecimiento__zona_id=zona)
        if vendedor:
            pedidos = pedidos.filter(visita__empleado_id=vendedor)

        agrupado = (
            pedidos
            .values(
                'visita__establecimiento_id',
                'visita__establecimiento__nombre',
                'visita__establecimiento__zona__nombre',
            )
            .annotate(
                pedidos=Count('num'),
                monto=Sum('total'),
                promedio=Avg('total'),
                entregados=Count('num', filter=Q(edo_pedido_id=PEDIDO_ENTREGADO)),
                cancelados=Count('num', filter=Q(edo_pedido_id=PEDIDO_CANCELADO)),
                ultima=Max('fecha'),
            )
        )

        hoy = date.today()
        filas = []
        con_compras = set()

        for fila in agrupado:
            identificador = fila['visita__establecimiento_id']
            con_compras.add(identificador)
            ultima = fecha_local(fila['ultima'])
            filas.append({
                'establecimiento_id': identificador,
                'nombre': fila['visita__establecimiento__nombre'],
                'zona': fila['visita__establecimiento__zona__nombre'],
                'pedidos': fila['pedidos'],
                'monto': fila['monto'] or Decimal('0.00'),
                'promedio': fila['promedio'] or Decimal('0.00'),
                'entregados': fila['entregados'],
                'cancelados': fila['cancelados'],
                'ultima_compra': ultima,
                'dias_sin_comprar': (hoy - ultima).days if ultima else None,
                'sin_compras': False,
            })

        # Cartera dormida: establecimientos activos que no compraron.
        if request.query_params.get('sin_compras') in ('1', 'true', 'si'):
            dormidos = Establecimiento.objects.exclude(pk__in=con_compras)
            if zona:
                dormidos = dormidos.filter(zona_id=zona)
            for est in dormidos.select_related('zona').order_by('nombre'):
                filas.append({
                    'establecimiento_id': est.pk,
                    'nombre': est.nombre,
                    'zona': est.zona.nombre if est.zona_id else None,
                    'pedidos': 0,
                    'monto': Decimal('0.00'),
                    'promedio': Decimal('0.00'),
                    'entregados': 0,
                    'cancelados': 0,
                    'ultima_compra': None,
                    'dias_sin_comprar': None,
                    'sin_compras': True,
                })

        clave = self.ORDENES[orden]
        descendente = clave.startswith('-')
        campo = clave.lstrip('-')

        def ordenar(fila):
            valor = fila[campo]
            if valor is None:
                # Los que no compraron van siempre al final.
                return Decimal('-1') if campo != 'nombre' else 'zzz'
            return valor

        filas.sort(key=ordenar, reverse=descendente)

        for posicion, fila in enumerate(filas, start=1):
            fila['posicion'] = posicion

        totales = pedidos.aggregate(
            pedidos=Count('num'), monto=Sum('total'), promedio=Avg('total'),
        )
        activos = [f for f in filas if not f['sin_compras']]
        lider = max(activos, key=lambda f: f['monto']) if activos else None

        return Response({
            'clientes': filas,
            'orden': orden,
            'resumen': {
                'clientes': len(activos),
                'sin_compras': len(filas) - len(activos),
                'pedidos': totales['pedidos'] or 0,
                'monto': totales['monto'] or Decimal('0.00'),
                'promedio': totales['promedio'] or Decimal('0.00'),
                'lider_nombre': lider['nombre'] if lider else None,
                'lider_monto': lider['monto'] if lider else Decimal('0.00'),
            },
        })


# ---------------------------------------------------------------------------
# RF53 - Reporte de desempeno por repartidor
# ---------------------------------------------------------------------------

def _sin_zona(momento):
    """Devuelve el datetime como naive, venga o no con zona horaria."""
    if momento is None:
        return None
    if timezone.is_aware(momento):
        return timezone.make_naive(momento, timezone.get_current_timezone())
    return momento


class DesempenoRepartidorAPIView(APIView):
    """RF53 - Numero de entregas y tiempos por repartidor.

    GET /api/reportes/desempeno-repartidor/
        ?fecha_inicio=2026-07-01&fecha_fin=2026-07-31
        &campo_fecha=creacion|entrega&orden=entregas

    Los tiempos se calculan en Python y no con aritmetica de fechas en
    SQL: fecha_creacion es DATE y fecha_entrega es DATETIME, y restarlas
    en MySQL depende de la version del motor. El volumen de entregas de
    un periodo es acotado, asi que el costo es despreciable.
    """

    permission_classes = [EsAdministrador]

    ORDENES = {
        'entregas': '-entregas',
        'completadas': '-completadas',
        'monto': '-monto',
        'tiempo': 'horas_promedio',
        'nombre': 'nombre',
    }

    def get(self, request):
        try:
            campo = (request.query_params.get('campo_fecha') or 'creacion').lower()
            if campo not in ('creacion', 'entrega'):
                raise ErrorFiltro(
                    "El parametro 'campo_fecha' solo acepta 'creacion' o 'entrega'."
                )

            orden = (request.query_params.get('orden') or 'entregas').lower()
            if orden not in self.ORDENES:
                raise ErrorFiltro(
                    "El parametro 'orden' acepta 'entregas', 'completadas', "
                    "'monto', 'tiempo' o 'nombre'."
                )

            inicio = _leer_fecha(request, 'fecha_inicio')
            fin = _leer_fecha(request, 'fecha_fin')
            if inicio and fin and inicio > fin:
                raise ErrorFiltro(
                    'La fecha inicial no puede ser posterior a la fecha final.'
                )

        except ErrorFiltro as error:
            return Response(
                {'error': str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        entregas = Entrega.objects.all()
        columna = 'fecha_creacion' if campo == 'creacion' else 'fecha_entrega'
        if inicio:
            entregas = entregas.filter(**{
                columna + '__gte': _inicio_del_dia(inicio)
                if columna == 'fecha_entrega' else inicio
            })
        if fin:
            entregas = entregas.filter(**{
                columna + '__lte': _fin_del_dia(fin)
                if columna == 'fecha_entrega' else fin
            })

        # 1) Conteo de entregas y completadas por repartidor.
        base = dict()
        for fila in (
            entregas.values('empleado_id').annotate(
                entregas=Count('numero'),
                completadas=Count(
                    'numero', filter=Q(edo_entrega_id=ENTREGA_COMPLETADA)
                ),
            )
        ):
            base[fila['empleado_id']] = {
                'entregas': fila['entregas'],
                'completadas': fila['completadas'],
            }

        # 2) Pedidos y monto distribuido.
        pedidos = {
            fila['entrega__empleado_id']: (fila['n'], fila['m'])
            for fila in (
                Pedido.objects
                .filter(entrega__in=entregas)
                .values('entrega__empleado_id')
                .annotate(n=Count('num'), m=Sum('total'))
            )
        }

        # 3) Paradas confirmadas.
        paradas = dict(
            EntregaEstablecimiento.objects
            .filter(entrega__in=entregas)
            .values_list('entrega__empleado_id')
            .annotate(n=Count('establecimiento'))
            .values_list('entrega__empleado_id', 'n')
        )

        # 4) Devoluciones generadas en esas entregas.
        devoluciones = dict(
            Devolucion.objects
            .filter(entrega__in=entregas)
            .values_list('entrega__empleado_id')
            .annotate(n=Count('codigo'))
            .values_list('entrega__empleado_id', 'n')
        )

        # 5) Tiempos: solo entregas ya concluidas.
        tiempos = {}
        for identificador, creacion, entregada in (
            entregas
            .filter(fecha_entrega__isnull=False, fecha_creacion__isnull=False)
            .values_list('empleado_id', 'fecha_creacion', 'fecha_entrega')
        ):
            arranque = datetime.combine(creacion, time.min)
            cierre = _sin_zona(entregada)
            horas = (cierre - arranque).total_seconds() / 3600
            if horas < 0:
                # Dato inconsistente: la entrega quedo antes de crearse.
                continue
            tiempos.setdefault(identificador, []).append(horas)

        empleados = {
            e.pk: ' '.join(
                p for p in [
                    e.nombre_de_pila, e.apellido_paterno, e.apellido_materno
                ] if p
            )
            for e in Empleado.objects.filter(pk__in=base.keys())
        }

        filas = []
        for identificador, datos in base.items():
            serie = tiempos.get(identificador, [])
            cantidad, monto = pedidos.get(identificador, (0, None))
            filas.append({
                'repartidor_id': identificador,
                'nombre': empleados.get(identificador, 'Sin asignar'),
                'entregas': datos['entregas'],
                'completadas': datos['completadas'],
                'cumplimiento': (
                    round(datos['completadas'] / datos['entregas'] * 100, 1)
                    if datos['entregas'] else 0
                ),
                'pedidos': cantidad,
                'monto': monto or Decimal('0.00'),
                'paradas': paradas.get(identificador, 0),
                'devoluciones': devoluciones.get(identificador, 0),
                'horas_promedio': (
                    round(sum(serie) / len(serie), 1) if serie else None
                ),
                'horas_minimo': round(min(serie), 1) if serie else None,
                'horas_maximo': round(max(serie), 1) if serie else None,
                'medidas': len(serie),
            })

        clave = self.ORDENES[orden]
        descendente = clave.startswith('-')
        campo_orden = clave.lstrip('-')

        def ordenar(fila):
            valor = fila[campo_orden]
            if valor is None:
                # Sin tiempo medido, siempre al final.
                return float('inf') if not descendente else -1
            return valor

        filas.sort(key=ordenar, reverse=descendente)
        for posicion, fila in enumerate(filas, start=1):
            fila['posicion'] = posicion

        todas = [h for serie in tiempos.values() for h in serie]
        con_tiempo = [f for f in filas if f['horas_promedio'] is not None]
        mas_rapido = min(con_tiempo, key=lambda f: f['horas_promedio']) if con_tiempo else None

        return Response({
            'repartidores': filas,
            'orden': orden,
            'campo_fecha': campo,
            'resumen': {
                'repartidores': len(filas),
                'entregas': sum(f['entregas'] for f in filas),
                'completadas': sum(f['completadas'] for f in filas),
                'monto': sum((f['monto'] for f in filas), Decimal('0.00')),
                'horas_promedio': (
                    round(sum(todas) / len(todas), 1) if todas else None
                ),
                'rapido_nombre': mas_rapido['nombre'] if mas_rapido else None,
                'rapido_horas': mas_rapido['horas_promedio'] if mas_rapido else None,
            },
        })


# ---------------------------------------------------------------------------
# RF54 - Reporte de productos mas vendidos
# ---------------------------------------------------------------------------

class ProductosMasVendidosAPIView(APIView):
    """RF54 - Ranking de productos por unidades y por monto.

    GET /api/reportes/productos-vendidos/
        ?fecha_inicio=2026-07-01&fecha_fin=2026-07-31
        &zona=2&vendedor=8&universo=sin_cancelados&orden=unidades&tope=0

    'universo' define que pedidos cuentan como venta:
        sin_cancelados (por defecto) - todo menos los cancelados
        entregados                   - solo lo que efectivamente llego
        todos                        - incluye cancelados
    Un pedido cancelado nunca se cobro ni salio del almacen, asi que
    contarlo como venta inflaria el reporte.
    """

    permission_classes = [EsAdministrador]

    ORDENES = {
        'unidades': '-unidades',
        'monto': '-importe',
        'pedidos': '-pedidos',
        'nombre': 'nombre',
    }

    UNIVERSOS = ('sin_cancelados', 'entregados', 'todos')

    def get(self, request):
        try:
            universo = (
                request.query_params.get('universo') or 'sin_cancelados'
            ).lower()
            if universo not in self.UNIVERSOS:
                raise ErrorFiltro(
                    "El parametro 'universo' acepta 'sin_cancelados', "
                    "'entregados' o 'todos'."
                )

            orden = (request.query_params.get('orden') or 'unidades').lower()
            if orden not in self.ORDENES:
                raise ErrorFiltro(
                    "El parametro 'orden' acepta 'unidades', 'monto', "
                    "'pedidos' o 'nombre'."
                )

            tope = _leer_entero(request, 'tope') or 0
            if tope < 0:
                raise ErrorFiltro("El parametro 'tope' no puede ser negativo.")

            inicio = _leer_fecha(request, 'fecha_inicio')
            fin = _leer_fecha(request, 'fecha_fin')
            if inicio and fin and inicio > fin:
                raise ErrorFiltro(
                    'La fecha inicial no puede ser posterior a la fecha final.'
                )

            zona = _leer_entero(request, 'zona')
            vendedor = _leer_entero(request, 'vendedor')

        except ErrorFiltro as error:
            return Response(
                {'error': str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        renglones = DetallePedido.objects.all()

        if universo == 'entregados':
            renglones = renglones.filter(
                num_pedido__edo_pedido_id=PEDIDO_ENTREGADO
            )
        elif universo == 'sin_cancelados':
            renglones = renglones.exclude(
                num_pedido__edo_pedido_id=PEDIDO_CANCELADO
            )

        if inicio:
            renglones = renglones.filter(
                num_pedido__fecha__gte=_inicio_del_dia(inicio)
            )
        if fin:
            renglones = renglones.filter(
                num_pedido__fecha__lte=_fin_del_dia(fin)
            )
        if zona:
            renglones = renglones.filter(
                num_pedido__visita__establecimiento__zona_id=zona
            )
        if vendedor:
            renglones = renglones.filter(
                num_pedido__visita__empleado_id=vendedor
            )

        agrupado = (
            renglones
            .values('cod_producto_id', 'cod_producto__nombre')
            .annotate(
                unidades=Sum('cantidad'),
                importe=Sum('importe'),
                pedidos=Count('num_pedido_id', distinct=True),
                clientes=Count(
                    'num_pedido__visita__establecimiento_id', distinct=True
                ),
                precio_promedio=Avg('precio_unitario'),
            )
        )

        # Stock actual para senalar riesgo de faltante en los mas vendidos.
        existencias = dict(
            Producto.objects.values_list('codigo', 'stock')
        )

        filas = []
        for fila in agrupado:
            codigo = fila['cod_producto_id']
            filas.append({
                'producto_id': codigo,
                'nombre': fila['cod_producto__nombre'],
                'unidades': fila['unidades'] or 0,
                'importe': fila['importe'] or Decimal('0.00'),
                'pedidos': fila['pedidos'],
                'clientes': fila['clientes'],
                'precio_promedio': fila['precio_promedio'] or Decimal('0.00'),
                'stock': existencias.get(codigo, 0),
            })

        total_unidades = sum(f['unidades'] for f in filas)
        total_importe = sum((f['importe'] for f in filas), Decimal('0.00'))

        for fila in filas:
            fila['parte_unidades'] = (
                round(fila['unidades'] / total_unidades * 100, 1)
                if total_unidades else 0
            )
            fila['parte_importe'] = (
                round(float(fila['importe']) / float(total_importe) * 100, 1)
                if total_importe else 0
            )
            # Cuantos periodos de venta cubre el stock que queda.
            fila['cobertura'] = (
                round(fila['stock'] / fila['unidades'], 1)
                if fila['unidades'] else None
            )

        clave = self.ORDENES[orden]
        descendente = clave.startswith('-')
        campo = clave.lstrip('-')
        filas.sort(key=lambda f: f[campo], reverse=descendente)

        for posicion, fila in enumerate(filas, start=1):
            fila['posicion'] = posicion

        if tope:
            filas = filas[:tope]

        lider = max(filas, key=lambda f: f['unidades']) if filas else None

        return Response({
            'productos': filas,
            'orden': orden,
            'universo': universo,
            'resumen': {
                'productos': len(filas),
                'unidades': total_unidades,
                'importe': total_importe,
                'lider_nombre': lider['nombre'] if lider else None,
                'lider_unidades': lider['unidades'] if lider else 0,
                'lider_parte': lider['parte_unidades'] if lider else 0,
            },
        })


# ---------------------------------------------------------------------------
# RF55 - Reporte de cobranza
# ---------------------------------------------------------------------------

class ReporteCobranzaAPIView(APIView):
    """RF55 - Cobranza diferenciando efectivo y tarjeta.

    GET /api/reportes/cobranza/
        ?fecha_inicio=2026-07-01&fecha_fin=2026-07-31
        &agrupacion=dia|semana|mes&cobrador=8&zona=2

    Devuelve cuatro bloques:
      periodos    serie temporal con el corte efectivo/tarjeta
      formas      totales por forma de pago
      cobradores  desglose por persona que cobro
      conciliacion  facturado contra cobrado de los pedidos entregados
    """

    permission_classes = [EsAdministrador]

    def get(self, request):
        try:
            agrupacion = (request.query_params.get('agrupacion') or 'dia').lower()
            if agrupacion not in AGRUPACIONES:
                raise ErrorFiltro(
                    "El parametro 'agrupacion' solo acepta 'dia', 'semana' o 'mes'."
                )

            inicio = _leer_fecha(request, 'fecha_inicio')
            fin = _leer_fecha(request, 'fecha_fin')
            if inicio and fin and inicio > fin:
                raise ErrorFiltro(
                    'La fecha inicial no puede ser posterior a la fecha final.'
                )

            cobrador = _leer_entero(request, 'cobrador')
            zona = _leer_entero(request, 'zona')

        except ErrorFiltro as error:
            return Response(
                {'error': str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        cobros = Pago.objects.all()
        if inicio:
            cobros = cobros.filter(fecha__gte=_inicio_del_dia(inicio))
        if fin:
            cobros = cobros.filter(fecha__lte=_fin_del_dia(fin))
        if cobrador:
            cobros = cobros.filter(empleado_id=cobrador)
        if zona:
            cobros = cobros.filter(establecimiento__zona_id=zona)

        # --- Serie temporal con el corte por forma de pago ---
        truncador = AGRUPACIONES[agrupacion][0]
        periodos = [
            {
                'periodo': fila['periodo'],
                'etiqueta': _etiqueta_periodo(fila['periodo'], agrupacion),
                'cobros': fila['cobros'],
                'total': fila['total'] or Decimal('0.00'),
                'efectivo': fila['efectivo'] or Decimal('0.00'),
                'tarjeta': fila['tarjeta'] or Decimal('0.00'),
            }
            for fila in (
                cobros
                .annotate(periodo=truncador('fecha'))
                .values('periodo')
                .annotate(
                    cobros=Count('codigo'),
                    total=Sum('monto'),
                    efectivo=Sum('monto', filter=Q(tipo_pago_id=PAGO_EFECTIVO)),
                    tarjeta=Sum('monto', filter=Q(tipo_pago_id=PAGO_TARJETA)),
                )
                .order_by('periodo')
            )
        ]

        # --- Totales por forma de pago ---
        totales = cobros.aggregate(cobros=Count('codigo'), monto=Sum('monto'))
        monto_total = totales['monto'] or Decimal('0.00')

        formas = []
        for fila in (
            cobros
            .values('tipo_pago_id', 'tipo_pago__nombre')
            .annotate(cobros=Count('codigo'), monto=Sum('monto'))
            .order_by('-monto')
        ):
            monto = fila['monto'] or Decimal('0.00')
            formas.append({
                'forma_pago_id': fila['tipo_pago_id'],
                'forma_pago': fila['tipo_pago__nombre'],
                'tono': tono(fila['tipo_pago_id']),
                'cobros': fila['cobros'],
                'monto': monto,
                'porcentaje': (
                    round(float(monto) / float(monto_total) * 100, 1)
                    if monto_total else 0
                ),
            })

        # --- Desglose por persona que cobro ---
        agrupado = list(
            cobros
            .values('empleado_id')
            .annotate(
                cobros=Count('codigo'),
                total=Sum('monto'),
                efectivo=Sum('monto', filter=Q(tipo_pago_id=PAGO_EFECTIVO)),
                tarjeta=Sum('monto', filter=Q(tipo_pago_id=PAGO_TARJETA)),
            )
            .order_by('-total')
        )
        nombres = {
            e.pk: ' '.join(
                p for p in [
                    e.nombre_de_pila, e.apellido_paterno, e.apellido_materno
                ] if p
            )
            for e in Empleado.objects.filter(
                pk__in=[f['empleado_id'] for f in agrupado]
            )
        }
        cobradores = [
            {
                'cobrador_id': fila['empleado_id'],
                'nombre': nombres.get(fila['empleado_id'], 'Sin asignar'),
                'cobros': fila['cobros'],
                'total': fila['total'] or Decimal('0.00'),
                'efectivo': fila['efectivo'] or Decimal('0.00'),
                'tarjeta': fila['tarjeta'] or Decimal('0.00'),
            }
            for fila in agrupado
        ]

        # --- Conciliacion: facturado contra cobrado ---
        # Se toma la cohorte de pedidos ENTREGADOS del rango y se compara
        # contra los pagos ligados a esos pedidos, sin importar cuando se
        # cobraron. Comparar dos rangos de fechas distintos daria un numero
        # enganoso, porque un pago puede corresponder a un pedido anterior.
        entregados = Pedido.objects.filter(edo_pedido_id=PEDIDO_ENTREGADO)
        if inicio:
            entregados = entregados.filter(fecha__gte=_inicio_del_dia(inicio))
        if fin:
            entregados = entregados.filter(fecha__lte=_fin_del_dia(fin))
        if zona:
            entregados = entregados.filter(
                visita__establecimiento__zona_id=zona
            )

        facturado = entregados.aggregate(
            pedidos=Count('num'), monto=Sum('total')
        )
        recuperado = (
            Pago.objects
            .filter(pedido__in=entregados)
            .aggregate(monto=Sum('monto'))
        )
        monto_facturado = facturado['monto'] or Decimal('0.00')
        monto_recuperado = recuperado['monto'] or Decimal('0.00')

        return Response({
            'agrupacion': agrupacion,
            'periodos': periodos,
            'formas': formas,
            'cobradores': cobradores,
            'conciliacion': {
                'pedidos_entregados': facturado['pedidos'] or 0,
                'facturado': monto_facturado,
                'recuperado': monto_recuperado,
                'pendiente': monto_facturado - monto_recuperado,
                'avance': (
                    round(float(monto_recuperado) / float(monto_facturado) * 100, 1)
                    if monto_facturado else 0
                ),
            },
            'resumen': {
                'cobros': totales['cobros'] or 0,
                'monto': monto_total,
                'efectivo': next(
                    (f['monto'] for f in formas
                     if f['forma_pago_id'] == PAGO_EFECTIVO),
                    Decimal('0.00'),
                ),
                'tarjeta': next(
                    (f['monto'] for f in formas
                     if f['forma_pago_id'] == PAGO_TARJETA),
                    Decimal('0.00'),
                ),
                'promedio': (
                    monto_total / totales['cobros'] if totales['cobros']
                    else Decimal('0.00')
                ),
            },
        })


class HistorialPedidosPantalla(TemplateView):
    """Sirve la interfaz del RF44."""

    template_name = 'reportes/historial_pedidos.html'
    extra_context = {'seccion': 'pedidos'}


class HistorialEntregasPantalla(TemplateView):
    """Sirve la interfaz del RF45."""

    template_name = 'reportes/historial_entregas.html'
    extra_context = {'seccion': 'entregas'}


class HistorialCobrosPantalla(TemplateView):
    """Sirve la interfaz del RF46."""

    template_name = 'reportes/historial_cobros.html'
    extra_context = {'seccion': 'cobros'}


class HistorialDevolucionesPantalla(TemplateView):
    """Sirve la interfaz del RF47."""

    template_name = 'reportes/historial_devoluciones.html'
    extra_context = {'seccion': 'devoluciones'}


class HistorialMovimientosPantalla(TemplateView):
    """Sirve la interfaz del RF48."""

    template_name = 'reportes/historial_movimientos.html'
    extra_context = {'seccion': 'movimientos'}


class PedidosActivosPantalla(TemplateView):
    """Sirve la interfaz del RF49."""

    template_name = 'reportes/pedidos_activos.html'
    extra_context = {'seccion': 'activos'}


class VolumenPedidosPantalla(TemplateView):
    """Sirve la interfaz del RF50."""

    template_name = 'reportes/volumen_pedidos.html'
    extra_context = {'seccion': 'volumen'}


class VentasPorVendedorPantalla(TemplateView):
    """Sirve la interfaz del RF51."""

    template_name = 'reportes/ventas_vendedor.html'
    extra_context = {'seccion': 'ventas_vendedor'}


class VentasPorClientePantalla(TemplateView):
    """Sirve la interfaz del RF52."""

    template_name = 'reportes/ventas_cliente.html'
    extra_context = {'seccion': 'ventas_cliente'}


class DesempenoRepartidorPantalla(TemplateView):
    """Sirve la interfaz del RF53."""

    template_name = 'reportes/desempeno_repartidor.html'
    extra_context = {'seccion': 'desempeno'}


class ProductosMasVendidosPantalla(TemplateView):
    """Sirve la interfaz del RF54."""

    template_name = 'reportes/productos_vendidos.html'
    extra_context = {'seccion': 'productos'}


class ReporteCobranzaPantalla(TemplateView):
    """Sirve la interfaz del RF55."""

    template_name = 'reportes/reporte_cobranza.html'
    extra_context = {'seccion': 'cobranza'}