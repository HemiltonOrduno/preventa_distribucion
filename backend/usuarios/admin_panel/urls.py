"""Rutas del Modulo 9 - Gestion de Usuarios.

Alta en config/urls.py:
    path('api/admin/', include('usuarios.admin_panel.urls')),
    path('panel/', include('usuarios.admin_panel.urls_panel')),

Se separan de usuarios/urls.py a proposito: ese archivo pertenece al
modulo de login y no debe tocarse desde el Modulo de Administrador.
"""

from django.urls import path

from . import views

app_name = 'admin_usuarios'

urlpatterns = [
    # GET /api/admin/sesion/
    path(
        'sesion/',
        views.SesionAdminAPIView.as_view(),
        name='api-sesion',
    ),
    # GET  /api/admin/usuarios/   listado
    # POST /api/admin/usuarios/   alta (RF56 + RF57)
    path(
        'usuarios/',
        views.UsuariosAPIView.as_view(),
        name='api-usuarios',
    ),
    # GET /api/admin/usuarios/12/
    path(
        'usuarios/<int:identificador>/',
        views.UsuarioDetalleAPIView.as_view(),
        name='api-usuario-detalle',
    ),
    # PATCH /api/admin/usuarios/12/datos/        (RF59)
    path(
        'usuarios/<int:identificador>/datos/',
        views.EditarDatosAPIView.as_view(),
        name='api-usuario-datos',
    ),
    # PATCH /api/admin/usuarios/12/credenciales/ (RF60)
    path(
        'usuarios/<int:identificador>/credenciales/',
        views.EditarCredencialesAPIView.as_view(),
        name='api-usuario-credenciales',
    ),
    # PUT /api/admin/usuarios/12/licencia/       (RF58)
    path(
        'usuarios/<int:identificador>/licencia/',
        views.LicenciaUsuarioAPIView.as_view(),
        name='api-usuario-licencia',
    ),
    # POST /api/admin/usuarios/12/estado/        (RF61)
    path(
        'usuarios/<int:identificador>/estado/',
        views.CambiarEstadoAPIView.as_view(),
        name='api-usuario-estado',
    ),
    # GET /api/admin/licencias/
    path(
        'licencias/',
        views.LicenciasAPIView.as_view(),
        name='api-licencias',
    ),
    # GET /api/admin/catalogos/
    path(
        'catalogos/',
        views.CatalogosUsuariosAPIView.as_view(),
        name='api-catalogos',
    ),
]