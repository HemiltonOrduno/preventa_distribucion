from django.urls import path
from .views import vehiculos_disponibles, pedidos_validados_por_zona, crear_entrega
from .views import almacenista_cargar_camion_view  # agrégalo al import existente

urlpatterns = [
    path('vehiculos-disponibles/', vehiculos_disponibles, name='vehiculos_disponibles'),
    path('pedidos-validados/', pedidos_validados_por_zona, name='pedidos_validados_por_zona'),
    path('entregas/', crear_entrega, name='crear_entrega'),
        path('almacenista/cargar-camion/', almacenista_cargar_camion_view, name='almacenista_cargar_camion'),

]