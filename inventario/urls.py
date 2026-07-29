from django.urls import path
from .views import registrar_movimiento, consultar_stock
from .views import almacenista_movimientos_view  # agrégalo al import existente


urlpatterns = [
    path('movimientos/', registrar_movimiento, name='registrar_movimiento'),
    path('productos/<str:cod_producto>/stock/', consultar_stock, name='consultar_stock'),
    path('almacenista/movimientos/', almacenista_movimientos_view, name='almacenista_movimientos'),

]