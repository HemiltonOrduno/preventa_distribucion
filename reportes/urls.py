"""Rutas API del Modulo de Administrador (Modulo 8 - Reportes).

Este archivo se incluye desde config/urls.py bajo el prefijo 'api/reportes/',
por lo que todas las rutas de abajo son relativas a ese prefijo.
"""

from django.urls import path

from . import views

app_name = 'reportes'

urlpatterns = [
    # GET /api/reportes/pedidos/
    path(
        'pedidos/',
        views.HistorialPedidosAPIView.as_view(),
        name='api-historial-pedidos',
    ),
    # GET /api/reportes/pedidos/12/
    path(
        'pedidos/<int:num>/',
        views.PedidoDetalleAPIView.as_view(),
        name='api-pedido-detalle',
    ),
    # GET /api/reportes/entregas/
    path(
        'entregas/',
        views.HistorialEntregasAPIView.as_view(),
        name='api-historial-entregas',
    ),
    # GET /api/reportes/entregas/7/
    path(
        'entregas/<int:numero>/',
        views.EntregaDetalleAPIView.as_view(),
        name='api-entrega-detalle',
    ),
    # GET /api/reportes/cobros/
    path(
        'cobros/',
        views.HistorialCobrosAPIView.as_view(),
        name='api-historial-cobros',
    ),
    # GET /api/reportes/devoluciones/
    path(
        'devoluciones/',
        views.HistorialDevolucionesAPIView.as_view(),
        name='api-historial-devoluciones',
    ),
    # GET /api/reportes/devoluciones/3/
    path(
        'devoluciones/<int:codigo>/',
        views.DevolucionDetalleAPIView.as_view(),
        name='api-devolucion-detalle',
    ),
    # GET /api/reportes/movimientos/
    path(
        'movimientos/',
        views.HistorialMovimientosAPIView.as_view(),
        name='api-historial-movimientos',
    ),
    # GET /api/reportes/movimientos/12/
    path(
        'movimientos/<int:codigo>/',
        views.MovimientoDetalleAPIView.as_view(),
        name='api-movimiento-detalle',
    ),
    # GET /api/reportes/pedidos-activos/
    path(
        'pedidos-activos/',
        views.PedidosActivosAPIView.as_view(),
        name='api-pedidos-activos',
    ),
    # GET /api/reportes/volumen-pedidos/
    path(
        'volumen-pedidos/',
        views.VolumenPedidosAPIView.as_view(),
        name='api-volumen-pedidos',
    ),
    # GET /api/reportes/ventas-vendedor/
    path(
        'ventas-vendedor/',
        views.VentasPorVendedorAPIView.as_view(),
        name='api-ventas-vendedor',
    ),
    # GET /api/reportes/ventas-cliente/
    path(
        'ventas-cliente/',
        views.VentasPorClienteAPIView.as_view(),
        name='api-ventas-cliente',
    ),
    # GET /api/reportes/desempeno-repartidor/
    path(
        'desempeno-repartidor/',
        views.DesempenoRepartidorAPIView.as_view(),
        name='api-desempeno-repartidor',
    ),
    # GET /api/reportes/productos-vendidos/
    path(
        'productos-vendidos/',
        views.ProductosMasVendidosAPIView.as_view(),
        name='api-productos-vendidos',
    ),
    # GET /api/reportes/cobranza/
    path(
        'cobranza/',
        views.ReporteCobranzaAPIView.as_view(),
        name='api-reporte-cobranza',
    ),
    # GET /api/reportes/catalogos/
    path(
        'catalogos/',
        views.CatalogosFiltrosAPIView.as_view(),
        name='api-catalogos',
    ),
]