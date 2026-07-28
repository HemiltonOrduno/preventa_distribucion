"""Pantallas del Modulo de Administrador.

Se separan de urls.py porque config/urls.py monta la app bajo 'api/reportes/',
y las pantallas HTML no deben vivir bajo un prefijo de API.

Alta en config/urls.py:
    path('panel/', include('reportes.urls_panel')),
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
]

