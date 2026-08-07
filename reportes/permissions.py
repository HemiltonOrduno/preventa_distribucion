"""
Control de acceso basado en roles (RBAC) para el Modulo de Administrador.

Cubre RFN-01 y RF62: todo endpoint de reportes valida en el backend que
quien consulta tenga rol Administrador. No se confia en que el frontend
oculte botones.

NOTA DE INTEGRACION
-------------------
La identidad se resuelve desde request.session['empleado_num'], que
LoginView ya establece al autenticar con usuario y contrasena. La
cabecera HTTP 'X-Empleado-Id' queda solo como ruta de respaldo para
pruebas locales (curl/Postman) y unicamente funciona con
RBAC_MODO_DESARROLLO activo; nunca debe quedar activa en produccion,
porque el cliente puede fijar ese header a cualquier valor.
"""

from django.conf import settings
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission, SAFE_METHODS

from usuarios.models import Empleado

ROL_ADMINISTRADOR = 'Administrador'
CABECERA_EMPLEADO = 'HTTP_X_EMPLEADO_ID'


def obtener_empleado_actual(request):
    """Devuelve el Empleado que hace la peticion, o None.

    Punto unico de integracion con el modulo de autenticacion.
    """
    # 0) Cache de request: evita resolver dos veces si ya se llamo antes
    #    en la misma peticion (p. ej. permission + vista).
    empleado = getattr(request, 'empleado', None)
    if empleado is not None:
        return empleado

    # 1) Ruta definitiva: sesion de Django ya autenticada por LoginView.
    #    request.session['empleado_num'] se firma con SECRET_KEY del
    #    servidor, por lo que el cliente no puede falsificarla.
    empleado_num = request.session.get('empleado_num')
    if empleado_num is not None:
        empleado = (
            Empleado.objects
            .select_related('rol')
            .filter(pk=empleado_num)
            .first()
        )
        if empleado is not None:
            request.empleado = empleado
        return empleado

    # 2) Ruta temporal: cabecera explicita, SOLO util para pruebas locales
    #    con curl/Postman. Debe permanecer detras del flag de desarrollo;
    #    de lo contrario cualquiera puede suplantar a cualquier empleado
    #    con solo mandar 'X-Empleado-Id' en la peticion.
    if not getattr(settings, 'RBAC_MODO_DESARROLLO', False):
        return None

    crudo = request.META.get(CABECERA_EMPLEADO)
    if not crudo:
        return None

    try:
        identificador = int(crudo)
    except (TypeError, ValueError):
        return None

    return (
        Empleado.objects
        .select_related('rol')
        .filter(pk=identificador)
        .first()
    )


class EsAdministrador(BasePermission):
    """Permite el acceso solo a empleados con rol Administrador."""

    message = 'Se requiere rol Administrador para consultar este recurso.'

    def has_permission(self, request, view):
        # Valvula de desarrollo: permite probar los endpoints desde el
        # navegador sin cabeceras. NUNCA debe quedar activa en produccion.
        if getattr(settings, 'RBAC_MODO_DESARROLLO', False):
            return True

        empleado = obtener_empleado_actual(request)
        if empleado is None:
            self.message = 'No se identifico al empleado que hace la peticion.'
            return False

        rol = getattr(empleado, 'rol', None)
        if rol is None or rol.nombre != ROL_ADMINISTRADOR:
            self.message = 'Se requiere rol Administrador para consultar este recurso.'
            return False

        # La identidad viaja en la cookie de sesion, que el navegador manda
        # solo automaticamente, incluso en peticiones armadas desde otro
        # sitio (CSRF). DRF exime a las vistas de APIView de la validacion
        # normal de Django y SessionAuthentication solo la exige cuando
        # request.user es un usuario real de auth, cosa que aqui nunca
        # ocurre (la sesion de negocio no pasa por auth.login()). Por eso
        # se valida el token a mano para los metodos que mutan datos.
        if request.method not in SAFE_METHODS:
            try:
                SessionAuthentication().enforce_csrf(request)
            except PermissionDenied:
                self.message = (
                    'Token CSRF invalido o ausente. Vuelve a cargar la '
                    'pagina e intenta de nuevo.'
                )
                return False

        # Se deja disponible para las vistas (auditoria, filtros por alcance).
        request.empleado = empleado
        return True