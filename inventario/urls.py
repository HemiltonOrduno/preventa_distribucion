from django.urls import path
from .views import registrar_movimiento, consultar_stock
from .views import almacenista_movimientos_view  # agrégalo al import existente
from .views import catalogo_stock  # agrégalo al import existente
from .views import perfil_actual 
from .views import devoluciones_pendientes  # RF40: origen = Devolución

urlpatterns = [
    path('movimientos/', registrar_movimiento, name='registrar_movimiento'),
    path('productos/<str:cod_producto>/stock/', consultar_stock, name='consultar_stock'),
    path('almacenista/movimientos/', almacenista_movimientos_view, name='almacenista_movimientos'),
    path('catalogo-stock/', catalogo_stock, name='catalogo_stock'),
    path('perfil-actual/', perfil_actual, name='perfil_actual'),
    path('devoluciones-pendientes/', devoluciones_pendientes, name='devoluciones_pendientes'),
]