"""Pantallas del Modulo 9 - Gestion de Usuarios.

Alta en config/urls.py:
    path('panel/', include('usuarios.admin_panel.urls_panel')),
"""

from django.urls import path

from . import views

app_name = 'panel_usuarios'

urlpatterns = [
    # GET /panel/usuarios/
    path(
        'usuarios/',
        views.GestionUsuariosPantalla.as_view(),
        name='gestion-usuarios',
    ),
    # GET /panel/licencias/
    path(
        'licencias/',
        views.LicenciasPantalla.as_view(),
        name='licencias',
    ),
]