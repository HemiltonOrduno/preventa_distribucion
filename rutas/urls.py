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
    path('rutas-visita-hoy/', views.rutas_visita_hoy, name='rutas_visita_hoy'),
    path('ruta-visita/<int:ruta_id>/asignar-vendedor/', views.asignar_vendedor_ruta, name='asignar_vendedor_ruta'),
    path('ruta-visita/<int:ruta_id>/ruta/', views.calcular_ruta_visita_coordinador, name='ruta_visita_coordinador'),
    path('gestionar-rutas-visita/', views.gestionar_rutas_visita, name='gestionar_rutas_visita'),
path('gestionar-rutas-entrega/', views.gestionar_rutas_entrega, name='gestionar_rutas_entrega'),
path('gestionar-zonas/', views.gestionar_zonas, name='gestionar_zonas'),
path('gestionar-establecimientos/', views.gestionar_establecimientos, name='gestionar_establecimientos'),
path('rutas-visita-todas/', views.rutas_visita_todas, name='rutas_visita_todas'),
]