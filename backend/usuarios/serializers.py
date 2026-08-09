from rest_framework import serializers
from .models import Usuario


class LoginSerializer(serializers.Serializer):
    usuario = serializers.CharField()
    contrasena = serializers.CharField(write_only=True)


class UsuarioDataSerializer(serializers.ModelSerializer):
    rol = serializers.CharField(source='empleado.rol.nombre', read_only=True)
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['num', 'usuario', 'rol', 'nombre_completo']

    def get_nombre_completo(self, obj):
        emp = obj.empleado
        return f"{emp.nombre_de_pila} {emp.apellido_paterno}"