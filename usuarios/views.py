from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from .models import Usuario
from .serializers import LoginSerializer, UsuarioDataSerializer



ROL_REDIRECT = {
    'Vendedor': '/api/visitas/ruta-del-dia/',
    'Coordinador': '/api/rutas/coordinador/',
    'Almacenista': '/api/inventario/almacenista/movimientos/',  # ajusta si eligen otra como "home"
    'Administrador': '/api/usuarios/panel-admin/',    # placeholder, aún no existe el módulo real
    'Repartidor': '/api/usuarios/panel-repartidor/',  # placeholder, aún no existe el módulo real
}


def login_view(request):
    return render(request, 'usuarios/login.html')


def acceso_denegado_view(request):
    return render(request, 'usuarios/acceso_denegado.html', status=403)


def panel_placeholder(request, nombre_rol):
    return HttpResponse(f"<h1>Panel de {nombre_rol}</h1><p>Módulo en construcción.</p>")


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario_input = serializer.validated_data['usuario']
        contrasena_input = serializer.validated_data['contrasena']

        try:
            usuario = Usuario.objects.select_related(
                'edo_usuario', 'empleado__rol'
            ).get(usuario=usuario_input)
        except Usuario.DoesNotExist:
            return Response({'detail': 'Usuario o contraseña incorrectos'}, status=status.HTTP_401_UNAUTHORIZED)

        if usuario.edo_usuario.nombre != 'Activo':
            return Response({'detail': 'Usuario inactivo'}, status=status.HTTP_403_FORBIDDEN)

        if not check_password(contrasena_input, usuario.contrasena):
            return Response({'detail': 'Usuario o contraseña incorrectos'}, status=status.HTTP_401_UNAUTHORIZED)

        request.session['usuario_num'] = usuario.num
        request.session['rol'] = usuario.empleado.rol.nombre

        data = UsuarioDataSerializer(usuario).data
        data['redirect_url'] = ROL_REDIRECT.get(usuario.empleado.rol.nombre, '/')
        return Response(data, status=status.HTTP_200_OK)


class UsuarioListCreate:
    pass


class UsuarioDetail:
    pass