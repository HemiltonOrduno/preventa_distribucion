"""Vistas del Modulo 9 - Gestion de Usuarios (RF56 a RF62)."""

from datetime import date

from django.db.models import Count, Q
from django.http import Http404
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from reportes.models import (
    EdoEmpleado, EdoUsuario, Licencia, Rol, TipoLicencia,
)
from reportes.permissions import EsAdministrador, obtener_empleado_actual
from usuarios.models import Empleado, Usuario

from .serializers import (
    ROLES_CON_LICENCIA,
    USUARIO_ACTIVO,
    USUARIO_INACTIVO,
    AltaUsuarioSerializer,
    CambiarEstadoSerializer,
    EditarCredencialesSerializer,
    EditarDatosSerializer,
    LicenciaSerializer,
    armar_renglon,
    nombre_completo,
)


class PaginacionUsuarios(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'tam_pagina'
    max_page_size = 200


def _consulta_base():
    """USUARIO con todo lo necesario para armar el renglon en una sola ida."""
    return (
        Usuario.objects
        .select_related(
            'empleado',
            'empleado__rol',
            'empleado__edo_empleado',
            'empleado__licencia',
            'empleado__licencia__tipo_licencia',
            'edo_usuario',
        )
        .order_by('empleado__apellido_paterno', 'empleado__nombre_de_pila')
    )


# ---------------------------------------------------------------------------
# RF62 - Acceso completo del administrador
# ---------------------------------------------------------------------------

class SesionAdminAPIView(APIView):
    """RF62 - Identidad y alcance del administrador en sesion.

    GET /api/admin/sesion/

    El RF62 se cumple en dos planos: la clase EsAdministrador bloquea en el
    backend cualquier peticion que no venga de un administrador, y este
    endpoint permite al frontend saber con quien esta tratando y que
    puede mostrar. La autorizacion nunca depende del frontend.
    """

    permission_classes = [EsAdministrador]

    def get(self, request):
        empleado = obtener_empleado_actual(request)

        if empleado is None:
            # Solo ocurre con RBAC_MODO_DESARROLLO activo.
            return Response({
                'identificado': False,
                'modo_desarrollo': True,
                'mensaje': (
                    'RBAC en modo desarrollo: no se identifico al empleado. '
                    'No dejar activo fuera de desarrollo.'
                ),
                'roles_administrables': list(
                    Rol.objects.order_by('codigo').values('codigo', 'nombre')
                ),
            })

        cuenta = (
            Usuario.objects
            .select_related('edo_usuario')
            .filter(empleado=empleado)
            .first()
        )

        return Response({
            'identificado': True,
            'empleado_id': empleado.pk,
            'nombre': nombre_completo(empleado),
            'email': empleado.email,
            'rol_id': empleado.rol_id,
            'rol': empleado.rol.nombre if empleado.rol_id else None,
            'usuario': cuenta.usuario if cuenta else None,
            'cuenta_activa': (
                cuenta.edo_usuario_id == USUARIO_ACTIVO if cuenta else False
            ),
            # El administrador puede operar sobre cualquier rol del sistema.
            'roles_administrables': list(
                Rol.objects.order_by('codigo').values('codigo', 'nombre')
            ),
            'acceso_total': True,
        })


# ---------------------------------------------------------------------------
# RF56 + RF57 - Listado y alta de usuarios
# ---------------------------------------------------------------------------

class UsuariosAPIView(ListCreateAPIView):
    """RF56 y RF57 - Consulta y alta de usuarios del sistema.

    GET  /api/admin/usuarios/?rol=R003&estado=EU001&q=lopez&page=1
    POST /api/admin/usuarios/
    """

    permission_classes = [EsAdministrador]
    pagination_class = PaginacionUsuarios
    serializer_class = AltaUsuarioSerializer

    def get_queryset(self):
        consulta = _consulta_base()

        rol = (self.request.query_params.get('rol') or '').strip()
        if rol:
            consulta = consulta.filter(empleado__rol_id=rol)

        estado = (self.request.query_params.get('estado') or '').strip()
        if estado:
            consulta = consulta.filter(edo_usuario_id=estado)

        texto = (self.request.query_params.get('q') or '').strip()
        if texto:
            consulta = consulta.filter(
                Q(usuario__icontains=texto)
                | Q(empleado__nombre_de_pila__icontains=texto)
                | Q(empleado__apellido_paterno__icontains=texto)
                | Q(empleado__apellido_materno__icontains=texto)
                | Q(empleado__email__icontains=texto)
            )

        return consulta

    def list(self, request, *args, **kwargs):
        consulta = self.filter_queryset(self.get_queryset())

        totales = {
            'usuarios': consulta.count(),
            'activos': consulta.filter(edo_usuario_id=USUARIO_ACTIVO).count(),
            'inactivos': consulta.filter(edo_usuario_id=USUARIO_INACTIVO).count(),
        }

        # Conteo por rol sobre el universo filtrado.
        etiquetas = dict(Rol.objects.values_list('codigo', 'nombre'))
        por_rol = [
            {
                'rol_id': fila['empleado__rol_id'],
                'rol': etiquetas.get(fila['empleado__rol_id'], fila['empleado__rol_id']),
                'usuarios': fila['n'],
            }
            for fila in (
                consulta.values('empleado__rol_id')
                        .annotate(n=Count('pk'))
                        .order_by('empleado__rol_id')
            )
        ]

        pagina = self.paginate_queryset(consulta)
        datos = [armar_renglon(u) for u in pagina]
        respuesta = self.get_paginated_response(datos)
        respuesta.data['resumen'] = dict(totales, por_rol=por_rol)
        return respuesta

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        advertencia = serializer.validated_data.get('advertencia')
        cuenta = serializer.save()

        cuenta = _consulta_base().get(pk=cuenta.pk)
        cuerpo = armar_renglon(cuenta)
        if advertencia:
            cuerpo['advertencia'] = advertencia

        return Response(cuerpo, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# Catalogos del modulo
# ---------------------------------------------------------------------------

class CatalogosUsuariosAPIView(APIView):
    """Alimenta los selectores de la pantalla de gestion de usuarios."""

    permission_classes = [EsAdministrador]

    def get(self, request):
        return Response({
            'roles': [
                {
                    'id': r.codigo,
                    'nombre': r.nombre,
                    'requiere_licencia': r.codigo in ROLES_CON_LICENCIA,
                }
                for r in Rol.objects.order_by('codigo')
            ],
            'estados_usuario': [
                {'id': e.codigo, 'nombre': e.nombre}
                for e in EdoUsuario.objects.order_by('codigo')
            ],
            'estados_empleado': [
                {'id': e.codigo, 'nombre': e.nombre}
                for e in EdoEmpleado.objects.order_by('codigo')
            ],
            'tipos_licencia': [
                {'id': t.codigo, 'nombre': t.nombre}
                for t in TipoLicencia.objects.order_by('codigo')
            ],
        })


# ---------------------------------------------------------------------------
# Pantalla
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# RF58 a RF61 - Operaciones sobre un usuario existente
# ---------------------------------------------------------------------------

class _BaseUsuarioAPIView(APIView):
    """Resuelve la cuenta por identificador y responde el renglon completo."""

    permission_classes = [EsAdministrador]

    def obtener(self, identificador):
        cuenta = _consulta_base().filter(pk=identificador).first()
        if cuenta is None:
            raise Http404('El usuario indicado no existe.')
        return cuenta

    def responder(self, identificador, extra=None):
        cuerpo = armar_renglon(self.obtener(identificador))
        if extra:
            cuerpo.update(extra)
        return Response(cuerpo)


class UsuarioDetalleAPIView(_BaseUsuarioAPIView):
    """GET /api/admin/usuarios/<id>/ - Ficha completa del usuario."""

    def get(self, request, identificador):
        return self.responder(identificador)


class EditarDatosAPIView(_BaseUsuarioAPIView):
    """RF59 - PATCH /api/admin/usuarios/<id>/datos/"""

    def patch(self, request, identificador):
        cuenta = self.obtener(identificador)
        serializer = EditarDatosSerializer(
            data=request.data, empleado=cuenta.empleado,
        )
        serializer.is_valid(raise_exception=True)
        serializer.guardar()
        return self.responder(identificador, {
            'mensaje': 'Datos personales actualizados.'
        })


class EditarCredencialesAPIView(_BaseUsuarioAPIView):
    """RF60 - PATCH /api/admin/usuarios/<id>/credenciales/"""

    def patch(self, request, identificador):
        cuenta = self.obtener(identificador)
        serializer = EditarCredencialesSerializer(
            data=request.data, cuenta=cuenta,
        )
        serializer.is_valid(raise_exception=True)
        serializer.guardar()

        cambios = []
        if serializer.validated_data.get('usuario'):
            cambios.append('nombre de usuario')
        if serializer.validated_data.get('contrasena'):
            cambios.append('contrasena')

        return self.responder(identificador, {
            'mensaje': 'Se actualizo: ' + ' y '.join(cambios) + '.'
        })


class LicenciaUsuarioAPIView(_BaseUsuarioAPIView):
    """RF58 - PUT /api/admin/usuarios/<id>/licencia/

    Registra la licencia si el empleado no tiene, o la renueva si ya
    existe. El codigo de LICENCIA se genera aqui porque la columna es
    VARCHAR y no tiene secuencia en la base.
    """

    def put(self, request, identificador):
        cuenta = self.obtener(identificador)
        empleado = cuenta.empleado

        serializer = LicenciaSerializer(data=request.data, empleado=empleado)
        serializer.is_valid(raise_exception=True)
        renovacion = empleado.licencia_id is not None
        serializer.guardar()

        return self.responder(identificador, {
            'mensaje': (
                'Licencia renovada.' if renovacion else 'Licencia registrada.'
            )
        })


class CambiarEstadoAPIView(_BaseUsuarioAPIView):
    """RF61 - POST /api/admin/usuarios/<id>/estado/

    Borrado logico: nunca se elimina el registro, porque pedidos, cobros y
    entregas historicas apuntan al empleado.
    """

    def post(self, request, identificador):
        cuenta = self.obtener(identificador)
        serializer = CambiarEstadoSerializer(
            data=request.data,
            cuenta=cuenta,
            solicitante=obtener_empleado_actual(request),
        )
        serializer.is_valid(raise_exception=True)
        serializer.guardar()

        activo = serializer.validated_data['activo']
        return self.responder(identificador, {
            'mensaje': (
                'La cuenta fue reactivada.' if activo
                else 'La cuenta quedo desactivada y ya no podra iniciar sesion.'
            )
        })


class LicenciasAPIView(APIView):
    """Listado de licencias con el empleado al que estan asignadas."""

    permission_classes = [EsAdministrador]

    def get(self, request):
        asignadas = {
            e.licencia_id: e
            for e in Empleado.objects
            .select_related('rol')
            .exclude(licencia__isnull=True)
        }

        hoy = date.today()
        filas = []
        for lic in (
            Licencia.objects
            .select_related('tipo_licencia')
            .order_by('vigencia')
        ):
            titular = asignadas.get(lic.pk)
            dias = (lic.vigencia - hoy).days if lic.vigencia else None
            filas.append({
                'codigo': lic.pk,
                'numlicencia': lic.numlicencia,
                'tipo_id': lic.tipo_licencia_id,
                'tipo': lic.tipo_licencia.nombre if lic.tipo_licencia_id else None,
                'vigencia': lic.vigencia,
                'dias_restantes': dias,
                'vencida': dias is not None and dias < 0,
                'por_vencer': dias is not None and 0 <= dias <= 30,
                'empleado_id': titular.pk if titular else None,
                'titular': nombre_completo(titular) if titular else None,
                'rol': titular.rol.nombre if titular and titular.rol_id else None,
            })

        return Response({
            'licencias': filas,
            'resumen': {
                'licencias': len(filas),
                'asignadas': sum(1 for f in filas if f['empleado_id']),
                'vencidas': sum(1 for f in filas if f['vencida']),
                'por_vencer': sum(1 for f in filas if f['por_vencer']),
            },
        })


class LicenciasPantalla(TemplateView):
    """Pantalla de control de licencias (apoyo al RF58)."""

    template_name = 'reportes/licencias.html'
    extra_context = {'seccion': 'licencias'}

class GestionUsuariosPantalla(TemplateView):
    """Sirve la interfaz del Modulo 9."""

    template_name = 'reportes/gestion_usuarios.html'
    extra_context = {'seccion': 'usuarios'}