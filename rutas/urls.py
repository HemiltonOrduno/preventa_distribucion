from django.urls import path
from . import views

urlpatterns = [
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
    path('ruta-entrega/<int:ruta_id>/guardar-orden/', views.guardar_orden_ruta_entrega, name='guardar_orden_ruta_entrega'),
    path('zonas/', views.zonas, name='zonas'),
    path('zonas/<int:zona_id>/actualizar/', views.actualizar_zona, name='actualizar_zona'),
    path('establecimientos/', views.establecimientos, name='establecimientos'),
    path('establecimientos/<int:est_id>/actualizar/', views.actualizar_establecimiento, name='actualizar_establecimiento'),
    path('ruta-visita/crear/', views.crear_ruta_visita, name='crear_ruta_visita'),
    path('ruta-visita/<int:ruta_id>/datos/', views.ruta_visita_datos, name='ruta_visita_datos'),
    path('ruta-visita/<int:ruta_id>/editar/', views.editar_ruta_visita, name='editar_ruta_visita'),
    path('historial-rutas/', views.historial_rutas_view, name='historial_rutas'),
    path('historial-rutas-datos/', views.historial_rutas, name='historial_rutas_api'),
    path('historial-rutas/visita/<int:ruta_id>/paradas/', views.paradas_ruta_visita, name='paradas_ruta_visita'),
    path('historial-rutas/entrega/<int:ruta_id>/paradas/', views.paradas_ruta_entrega, name='paradas_ruta_entrega'),
    
]