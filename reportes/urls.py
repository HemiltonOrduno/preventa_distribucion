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
    # GET /api/reportes/catalogos/
    path(
        'catalogos/',
        views.CatalogosFiltrosAPIView.as_view(),
        name='api-catalogos',
    ),
]