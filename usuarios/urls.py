from django.urls import path
from .views import login_view, LoginView, acceso_denegado_view, panel_placeholder

urlpatterns = [
    path('', login_view, name='login-page'),
    path('login/', LoginView.as_view(), name='login-api'),
    path('acceso-denegado/', acceso_denegado_view, name='acceso-denegado'),
    path('panel-admin/', panel_placeholder, {'nombre_rol': 'Administrador'}, name='panel-admin'),
    path('panel-repartidor/', panel_placeholder, {'nombre_rol': 'Repartidor'}, name='panel-repartidor'),
]

