from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from .models import Usuario
from .serializers import LoginSerializer, UsuarioDataSerializer


def login_view(request):
    return render(request, 'usuarios/login.html')


def acceso_denegado_view(request):
    return render(request, 'usuarios/acceso_denegado.html', status=403)


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
        request.session['empleado_num'] = usuario.empleado.num
        request.session['rol'] = usuario.empleado.rol.nombre

        data = UsuarioDataSerializer(usuario).data
        return Response(data, status=status.HTTP_200_OK)


class UsuarioListCreate:
    pass


class UsuarioDetail:
    pass