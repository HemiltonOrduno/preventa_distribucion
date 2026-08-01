from django.urls import path
from .views import registrar_producto, listar_productos, almacenista_nuevo_producto_view

urlpatterns = [
    path('productos/', registrar_producto, name='registrar_producto'),
    path('productos/activos/', listar_productos, name='listar_productos'),
    path('almacenista/nuevo/', almacenista_nuevo_producto_view, name='almacenista_nuevo_producto'),
]