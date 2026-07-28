from django.urls import path
from .views import (
    ruta_del_dia_view,
    visita_view,
    levantar_pedido_view,
    visita_sin_pedido_view,
)

urlpatterns = [
    path('ruta-del-dia/', ruta_del_dia_view, name='ruta_del_dia'),
    path('visita/', visita_view, name='visita'),
    path('levantar-pedido/', levantar_pedido_view, name='levantar_pedido'),
    path('visita-sin-pedido/', visita_sin_pedido_view, name='visita_sin_pedido'),
]