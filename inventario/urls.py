from django.urls import path
from .views import registrar_movimiento, consultar_stock

urlpatterns = [
    path('movimientos/', registrar_movimiento, name='registrar_movimiento'),
    path('productos/<str:cod_producto>/stock/', consultar_stock, name='consultar_stock'),
]