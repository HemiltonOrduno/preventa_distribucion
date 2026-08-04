from django.urls import path
from .views import pedidos_activos_view, pedidos_activos_api

urlpatterns = [
    path('pedidos-activos/', pedidos_activos_view, name='pedidos_activos_view'),
    path('pedidos-activos/api/', pedidos_activos_api, name='pedidos_activos_api'),
]