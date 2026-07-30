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
    almacenista_pedidos_view,
    ruta_del_dia_api,
    iniciar_visita,
    realizar_visita,
    levantar_pedido,
    visita_sin_pedido,
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

    # --- API del vendedor (RF04-15) ---
    path('api/ruta-del-dia/', ruta_del_dia_api, name='ruta_del_dia_api'),
    path('api/visitas/', iniciar_visita, name='iniciar_visita'),
    path('api/visitas/<int:visita_id>/realizar/', realizar_visita, name='realizar_visita'),
    path('api/visitas/<int:visita_id>/pedido/', levantar_pedido, name='levantar_pedido_api'),
    path('api/visitas/<int:visita_id>/sin-pedido/', visita_sin_pedido, name='visita_sin_pedido_api'),
]