from django.urls import path

from .views import (
    ruta_del_dia_view,
    visita_view,
    levantar_pedido_view,
    visita_sin_pedido_view,
    pedidos_pendientes,
    pedido_detalle,
    ajustar_cantidad_pedido,
    cancelar_producto_pedido,
    almacenista_pedidos_view  # agrégalo al import existente

)

urlpatterns = [
    path('ruta-del-dia/', ruta_del_dia_view, name='ruta_del_dia'),
    path('visita/', visita_view, name='visita'),
    path('levantar-pedido/', levantar_pedido_view, name='levantar_pedido'),
    path('visita-sin-pedido/', visita_sin_pedido_view, name='visita_sin_pedido'),
    path('pedidos-pendientes/', pedidos_pendientes, name='pedidos_pendientes'),
    path('pedidos/<int:pedido_id>/detalle/', pedido_detalle, name='pedido_detalle'),
    path('pedidos/<int:pedido_id>/detalle/<str:cod_producto>/ajustar/', ajustar_cantidad_pedido, name='ajustar_cantidad_pedido'),
    path('pedidos/<int:pedido_id>/detalle/<str:cod_producto>/cancelar/', cancelar_producto_pedido, name='cancelar_producto_pedido'),
    path('almacenista/pedidos/', almacenista_pedidos_view, name='almacenista_pedidos'),

]
