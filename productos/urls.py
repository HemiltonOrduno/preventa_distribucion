from django.urls import path
from .views import registrar_producto, listar_productos

urlpatterns = [
    path('productos/', registrar_producto, name='registrar_producto'),
    path('productos/activos/', listar_productos, name='listar_productos'),
]