from django.urls import path
from . import views
from .views import vehiculos_disponibles, pedidos_validados_por_zona, crear_entrega, almacenista_cargar_camion_view, proximo_numero_entrega

urlpatterns = [
    path('vehiculos-disponibles/', vehiculos_disponibles, name='vehiculos_disponibles'),
    path('pedidos-validados/', pedidos_validados_por_zona, name='pedidos_validados_por_zona'),
    path('entregas/', crear_entrega, name='crear_entrega'),
    path('proximo-numero-entrega/', proximo_numero_entrega, name='proximo_numero_entrega'),
    path('almacenista/cargar-camion/', almacenista_cargar_camion_view, name='almacenista_cargar_camion'),
    path('ruta-entrega/', views.ruta_entrega_view, name='ruta_entrega'),
    path('pedidos/', views.pedidos_view, name='pedidos_repartidor'),
    path('mi-ruta/', views.mi_ruta, name='mi_ruta'),
    path('pedido/<int:pedido_id>/detalle/', views.detalle_pedido, name='detalle_pedido'),
    path('iniciar-ruta/', views.iniciar_ruta, name='iniciar_ruta'),
    path('finalizar-ruta/', views.finalizar_ruta, name='finalizar_ruta'),
    path('registrar-cobro/', views.registrar_cobro, name='registrar_cobro'),
    path('registrar-devolucion/', views.registrar_devolucion, name='registrar_devolucion'),
    path('confirmar-entrega/', views.confirmar_entrega_establecimiento, name='confirmar_entrega'),
    path('entregas-disponibles/', views.entregas_disponibles, name='entregas_disponibles'),
    path('tomar-entrega/', views.tomar_entrega, name='tomar_entrega'),

]