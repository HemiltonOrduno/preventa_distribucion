from django.urls import path
from .views import vehiculos_disponibles, pedidos_validados_por_zona, crear_entrega

urlpatterns = [
    path('vehiculos-disponibles/', vehiculos_disponibles, name='vehiculos_disponibles'),
    path('pedidos-validados/', pedidos_validados_por_zona, name='pedidos_validados_por_zona'),
    path('entregas/', crear_entrega, name='crear_entrega'),
]