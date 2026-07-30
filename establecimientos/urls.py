from django.urls import path
from .views import (
    registro_cliente_view,
    registro_establecimiento_view,
    crear_cliente,
    crear_establecimiento,
)

urlpatterns = [
    path('registro-cliente/', registro_cliente_view, name='registro_cliente'),
    path('registro-establecimiento/', registro_establecimiento_view, name='registro_establecimiento'),
    path('clientes/', crear_cliente, name='crear_cliente'),
    path('nuevo/', crear_establecimiento, name='crear_establecimiento'),
]