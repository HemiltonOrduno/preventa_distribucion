from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import check_password
from .models import Usuario
from .serializers import LoginSerializer, UsuarioDataSerializer
from django.shortcuts import redirect


ROL_REDIRECT = {
    'Vendedor': '/api/visitas/ruta-del-dia/',
    'Coordinador': '/api/rutas/coordinador/',
    'Almacenista': '/api/inventario/almacenista/movimientos/',
    'Administrador': '/panel/reportes/pedidos/',
    'Repartidor': '/api/entregas/ruta-entrega/',
}


def login_view(request):
    return render(request, 'usuarios/login.html')


def acceso_denegado_view(request):
    return render(request, 'usuarios/acceso_denegado.html', status=403)


def panel_placeholder(request, nombre_rol):
    return HttpResponse(f"<h1>Panel de {nombre_rol}</h1><p>Módulo en construcción.</p>")


class LoginView(APIView):
    # El proyecto tiene IsAuthenticated como permiso global (config/settings.py),
    # pero el login es el único endpoint al que se debe poder entrar SIN estar
    # logueado todavía, por eso se sobreescribe aquí, no en settings.py.
    permission_classes = [AllowAny]
    authentication_classes = []

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

        try:
            contrasena_valida = check_password(contrasena_input, usuario.contrasena)
        except ValueError:
            # Pasa cuando el hash guardado en la BD no tiene un formato reconocido
            # (por ejemplo, si la base de datos no está actualizada con el fix de contraseñas)
            return Response({'detail': 'Usuario o contraseña incorrectos'}, status=status.HTTP_401_UNAUTHORIZED)

        if not contrasena_valida:
            return Response({'detail': 'Usuario o contraseña incorrectos'}, status=status.HTTP_401_UNAUTHORIZED)

        request.session['usuario_num'] = usuario.num
        request.session['empleado_num'] = usuario.empleado.num
        request.session['rol'] = usuario.empleado.rol.nombre
        # Se guarda el nombre para mostrarlo en el panel de perfil de cada
        # modulo, sin volver a consultar la base en cada pantalla.
        request.session['nombre_usuario'] = (
            f"{usuario.empleado.nombre_de_pila} {usuario.empleado.apellido_paterno}"
        )

        data = UsuarioDataSerializer(usuario).data
        data['redirect_url'] = ROL_REDIRECT.get(usuario.empleado.rol.nombre, '/')
        return Response(data, status=status.HTTP_200_OK)

def logout_view(request):
    request.session.flush()
    return redirect('login-page')


class UsuarioListCreate:
    pass


class UsuarioDetail:
    pass