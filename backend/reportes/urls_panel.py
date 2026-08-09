"""Pantallas del Modulo de Administrador.

Se separan de urls.py porque config/urls.py monta la app bajo 'api/reportes/',
y las pantallas HTML no deben vivir bajo un prefijo de API.

Alta en config/urls.py:
    path('panel/reportes/', include('reportes.urls_panel')),
"""

from django.urls import path

from . import views

app_name = 'panel_admin'

urlpatterns = [
    # GET /panel/pedidos/
    path(
        'pedidos/',
        views.HistorialPedidosPantalla.as_view(),
        name='historial-pedidos',
    ),
    # GET /panel/entregas/
    path(
        'entregas/',
        views.HistorialEntregasPantalla.as_view(),
        name='historial-entregas',
    ),
    # GET /panel/cobros/
    path(
        'cobros/',
        views.HistorialCobrosPantalla.as_view(),
        name='historial-cobros',
    ),
    # GET /panel/devoluciones/
    path(
        'devoluciones/',
        views.HistorialDevolucionesPantalla.as_view(),
        name='historial-devoluciones',
    ),
    # GET /panel/movimientos/
    path(
        'movimientos/',
        views.HistorialMovimientosPantalla.as_view(),
        name='historial-movimientos',
    ),
    # GET /panel/activos/
    path(
        'activos/',
        views.PedidosActivosPantalla.as_view(),
        name='pedidos-activos',
    ),
    # GET /panel/volumen-pedidos/
    path(
        'volumen-pedidos/',
        views.VolumenPedidosPantalla.as_view(),
        name='volumen-pedidos',
    ),
    # GET /panel/ventas-vendedor/
    path(
        'ventas-vendedor/',
        views.VentasPorVendedorPantalla.as_view(),
        name='ventas-vendedor',
    ),
    # GET /panel/ventas-cliente/
    path(
        'ventas-cliente/',
        views.VentasPorClientePantalla.as_view(),
        name='ventas-cliente',
    ),
    # GET /panel/desempeno-repartidor/
    path(
        'desempeno-repartidor/',
        views.DesempenoRepartidorPantalla.as_view(),
        name='desempeno-repartidor',
    ),
    # GET /panel/productos-vendidos/
    path(
        'productos-vendidos/',
        views.ProductosMasVendidosPantalla.as_view(),
        name='productos-vendidos',
    ),
    # GET /panel/cobranza/
    path(
        'cobranza/',
        views.ReporteCobranzaPantalla.as_view(),
        name='reporte-cobranza',
    ),
]