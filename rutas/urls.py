from django.urls import path
from . import views

urlpatterns = [
    path('mapa/', views.mapa, name='mapa'),
    path('calcular-ruta-visita/', views.calcular_ruta_visita, name='calcular_ruta_visita'),
    path('calcular-ruta-entrega/', views.calcular_ruta_entrega, name='calcular_ruta_entrega'),
    path('coordinador/', views.coordinador, name='coordinador'),
    path('rutas-activas/', views.rutas_activas, name='rutas_activas'),
    path('ruta-visita/<int:ruta_id>/detalle/', views.ruta_visita_detalle, name='ruta_visita_detalle'),
    path('entrega/<int:entrega_id>/establecimientos/', views.obtener_establecimientos_entrega, name='establecimientos_entrega'),
    path('entrega/<int:entrega_id>/ruta/', views.calcular_ruta_entrega_coordinador, name='ruta_entrega_coordinador'),
]