"""
Control de acceso basado en roles (RBAC) para el Modulo de Administrador.

Cubre RFN-01 y RF62: todo endpoint de reportes valida en el backend que
quien consulta tenga rol Administrador. No se confia en que el frontend
oculte botones.

NOTA DE INTEGRACION
-------------------
El proyecto todavia no tiene autenticacion por token montada. Mientras
tanto, la identidad viaja en la cabecera HTTP 'X-Empleado-Id'.

Cuando el modulo de login este listo, lo unico que hay que cambiar es la
funcion obtener_empleado_actual(): el resto del modulo no se toca.
"""

from django.conf import settings
from rest_framework.permissions import BasePermission

from usuarios.models import Empleado

ROL_ADMINISTRADOR = 'Administrador'
CABECERA_EMPLEADO = 'HTTP_X_EMPLEADO_ID'


def obtener_empleado_actual(request):
    """Devuelve el Empleado que hace la peticion, o None.

    Punto unico de integracion con el modulo de autenticacion.
    """
    # 1) Si ya existe una sesion autenticada de Django que apunte a un
    #    empleado, se usa esa (ruta definitiva).
    empleado = getattr(request, 'empleado', None)
    if empleado is not None:
        return empleado

    # 2) Ruta temporal: cabecera explicita.
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

        # Se deja disponible para las vistas (auditoria, filtros por alcance).
        request.empleado = empleado
        return True