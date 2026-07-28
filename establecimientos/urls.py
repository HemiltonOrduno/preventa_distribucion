from django.urls import path
from .views import registro_cliente_view, registro_establecimiento_view

urlpatterns = [
    path('registro-cliente/', registro_cliente_view, name='registro_cliente'),
    path('registro-establecimiento/', registro_establecimiento_view, name='registro_establecimiento'),
]