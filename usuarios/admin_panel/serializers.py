"""Serializers del Modulo 9 - Gestion de Usuarios (RF56 a RF62)."""

import re
from datetime import date

from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models import Max
from rest_framework import serializers

from reportes.models import (
    EdoEmpleado, EdoUsuario, Licencia, Rol, TipoLicencia,
)
from usuarios.models import Empleado, Usuario

# Estados con los que nace toda cuenta nueva.
EMPLEADO_ACTIVO = 'EE001'
EMPLEADO_INACTIVO = 'EE002'
USUARIO_ACTIVO = 'EU001'
USUARIO_INACTIVO = 'EU002'

# Roles que requieren licencia registrada (RF58).
# El esquema y los datos muestran que no es solo el repartidor: el
# almacenista opera montacargas y el vendedor conduce para visitar
# clientes. Ajustar aqui si la operacion real cambia.
ROLES_CON_LICENCIA = (
    'R003',   # Vendedor      - licencia de automovilista
    'R004',   # Almacenista   - licencia de montacarguista
    'R005',   # Repartidor    - licencia de carga
)


def siguiente_id(modelo):
    """Calcula el siguiente identificador de una tabla sin auto_increment.

    Ni EMPLEADO.num ni USUARIO.num tienen AUTO_INCREMENT en el esquema, asi
    que el consecutivo se genera aqui. Debe llamarse SIEMPRE dentro de un
    bloque transaction.atomic() para que la lectura del maximo y la
    insercion ocurran juntas.

    El nombre real de la llave se obtiene del propio modelo, para no
    depender de como se haya declarado en la app usuarios.
    """
    llave = modelo._meta.pk.attname
    actual = modelo.objects.aggregate(maximo=Max(llave))['maximo'] or 0
    return actual + 1


def validar_telefono(valor):
    """Valida y normaliza un telefono a 10 digitos.

    La columna es VARCHAR(15) y acepta cualquier texto, asi que la regla
    se aplica aqui. Se descartan los separadores que la persona escriba
    —parentesis, guiones, espacios— y se exige que queden exactamente 10
    digitos, el largo de un numero nacional en Mexico (lada + numero).

    Devuelve el formato canonico (664) 123-4567 para que todos los
    registros queden consistentes sin importar como se capturaron.
    """
    digitos = re.sub(r'\D', '', valor or '')

    if not digitos:
        raise serializers.ValidationError('Captura el numero telefonico.')

    # Tolera el 52 de Mexico o un 1 de larga distancia al inicio.
    if len(digitos) == 12 and digitos.startswith('52'):
        digitos = digitos[2:]
    elif len(digitos) == 11 and digitos.startswith('1'):
        digitos = digitos[1:]

    if len(digitos) != 10:
        raise serializers.ValidationError(
            'El telefono debe tener exactamente 10 digitos '
            '(lada + numero). Capturaste {}.'.format(len(digitos))
        )

    return '({}) {}-{}'.format(digitos[:3], digitos[3:6], digitos[6:])


def nombre_completo(empleado):
    partes = [
        empleado.nombre_de_pila,
        empleado.apellido_paterno,
        empleado.apellido_materno,
    ]
    return ' '.join(p for p in partes if p)


# ---------------------------------------------------------------------------
# Lectura
# ---------------------------------------------------------------------------

class UsuarioListaSerializer(serializers.Serializer):
    """Renglon del listado de usuarios del sistema.

    Se arma a mano en lugar de con ModelSerializer porque los datos viven
    repartidos entre USUARIO y EMPLEADO, y la contrasena nunca debe salir.
    """

    usuario_id = serializers.IntegerField(read_only=True)
    usuario = serializers.CharField(read_only=True)
    empleado_id = serializers.IntegerField(read_only=True)
    nombre = serializers.CharField(read_only=True)
    nombre_de_pila = serializers.CharField(read_only=True)
    apellido_paterno = serializers.CharField(read_only=True)
    apellido_materno = serializers.CharField(read_only=True, allow_null=True)
    email = serializers.EmailField(read_only=True)
    telefono = serializers.CharField(read_only=True)
    fecha_nacimiento = serializers.DateField(read_only=True)
    rol_id = serializers.CharField(read_only=True)
    rol = serializers.CharField(read_only=True)
    edo_usuario_id = serializers.CharField(read_only=True)
    edo_usuario = serializers.CharField(read_only=True)
    edo_empleado_id = serializers.CharField(read_only=True)
    edo_empleado = serializers.CharField(read_only=True)
    activo = serializers.BooleanField(read_only=True)
    licencia_id = serializers.CharField(read_only=True, allow_null=True)
    licencia_num = serializers.CharField(read_only=True, allow_null=True)
    licencia_tipo_id = serializers.CharField(read_only=True, allow_null=True)
    licencia_tipo = serializers.CharField(read_only=True, allow_null=True)
    licencia_vigencia = serializers.DateField(read_only=True, allow_null=True)
    requiere_licencia = serializers.BooleanField(read_only=True)


def armar_renglon(usuario):
    """Aplana USUARIO + EMPLEADO + catalogos en un solo diccionario."""
    empleado = usuario.empleado
    licencia = empleado.licencia if empleado.licencia_id else None
    return {
        'usuario_id': usuario.pk,
        'usuario': usuario.usuario,
        'empleado_id': empleado.pk,
        'nombre': nombre_completo(empleado),
        # Campos por separado: los formularios de edicion los necesitan
        # sin tener que partir el nombre concatenado.
        'nombre_de_pila': empleado.nombre_de_pila,
        'apellido_paterno': empleado.apellido_paterno,
        'apellido_materno': empleado.apellido_materno,
        'email': empleado.email,
        'telefono': empleado.telefono,
        'fecha_nacimiento': empleado.fecha_nacimiento,
        'rol_id': empleado.rol_id,
        'rol': empleado.rol.nombre if empleado.rol_id else None,
        'edo_usuario_id': usuario.edo_usuario_id,
        'edo_usuario': usuario.edo_usuario.nombre if usuario.edo_usuario_id else None,
        'edo_empleado_id': empleado.edo_empleado_id,
        'edo_empleado': (
            empleado.edo_empleado.nombre if empleado.edo_empleado_id else None
        ),
        'activo': usuario.edo_usuario_id == USUARIO_ACTIVO,
        'licencia_id': licencia.pk if licencia else None,
        'licencia_num': getattr(licencia, 'numlicencia', None),
        'licencia_tipo_id': (
            licencia.tipo_licencia_id if licencia else None
        ),
        'licencia_tipo': (
            licencia.tipo_licencia.nombre
            if licencia and licencia.tipo_licencia_id else None
        ),
        'licencia_vigencia': getattr(licencia, 'vigencia', None),
        'requiere_licencia': empleado.rol_id in ROLES_CON_LICENCIA,
    }


# ---------------------------------------------------------------------------
# RF56 + RF57 - Alta de usuario con rol
# ---------------------------------------------------------------------------

class AltaUsuarioSerializer(serializers.Serializer):
    """RF56 y RF57 - Crea EMPLEADO y USUARIO en una sola operacion."""

    # Datos personales (EMPLEADO)
    nombre_de_pila = serializers.CharField(max_length=25)
    apellido_paterno = serializers.CharField(max_length=25)
    apellido_materno = serializers.CharField(
        max_length=25, required=False, allow_blank=True, allow_null=True,
    )
    fecha_nacimiento = serializers.DateField()
    telefono = serializers.CharField(max_length=15)
    email = serializers.EmailField(max_length=50)

    # Rol (RF57)
    rol = serializers.CharField(max_length=10)

    # Credenciales (RF56)
    usuario = serializers.CharField(max_length=20)
    contrasena = serializers.CharField(
        max_length=128, min_length=8, write_only=True,
    )

    # Licencia opcional al momento del alta (RF58 la gestiona aparte)
    licencia = serializers.CharField(
        max_length=10, required=False, allow_blank=True, allow_null=True,
    )

    def validate_rol(self, valor):
        if not Rol.objects.filter(pk=valor).exists():
            raise serializers.ValidationError(
                'El rol indicado no existe en el catalogo.'
            )
        return valor

    def validate_usuario(self, valor):
        valor = valor.strip()
        if Usuario.objects.filter(usuario=valor).exists():
            raise serializers.ValidationError(
                'Ese nombre de usuario ya esta ocupado.'
            )
        return valor

    def validate_email(self, valor):
        valor = valor.strip().lower()
        if Empleado.objects.filter(email=valor).exists():
            raise serializers.ValidationError(
                'Ya existe un empleado registrado con ese correo.'
            )
        return valor

    def validate_telefono(self, valor):
        return validar_telefono(valor)

    def validate_licencia(self, valor):
        if not valor:
            return None
        if not Licencia.objects.filter(pk=valor).exists():
            raise serializers.ValidationError('La licencia indicada no existe.')
        if Empleado.objects.filter(licencia_id=valor).exists():
            raise serializers.ValidationError(
                'Esa licencia ya esta asignada a otro empleado.'
            )
        return valor

    def validate(self, datos):
        # El repartidor necesita licencia; se avisa pero no se bloquea el
        # alta, porque el RF58 permite registrarla despues.
        datos['advertencia'] = None
        if datos['rol'] in ROLES_CON_LICENCIA and not datos.get('licencia'):
            datos['advertencia'] = (
                'El rol requiere licencia. La cuenta se creo sin ella; '
                'registrala antes de asignar rutas.'
            )
        return datos

    @transaction.atomic
    def create(self, validated_data):
        """Crea EMPLEADO y luego USUARIO.

        El orden importa: USUARIO.empleado es NOT NULL, asi que el empleado
        debe existir primero. Todo va en una transaccion para que no quede
        un empleado huerfano si la creacion de la cuenta falla.
        """
        validated_data.pop('advertencia', None)
        contrasena = validated_data.pop('contrasena')
        usuario_nombre = validated_data.pop('usuario')
        rol = validated_data.pop('rol')
        licencia = validated_data.pop('licencia', None)

        llave_empleado = Empleado._meta.pk.attname
        empleado = Empleado(**{
            llave_empleado: siguiente_id(Empleado),
            'nombre_de_pila': validated_data['nombre_de_pila'].strip(),
            'apellido_paterno': validated_data['apellido_paterno'].strip(),
            'apellido_materno': (
                validated_data.get('apellido_materno') or ''
            ).strip() or None,
            'fecha_nacimiento': validated_data['fecha_nacimiento'],
            'telefono': validated_data['telefono'],
            'email': validated_data['email'],
            'rol_id': rol,
            'edo_empleado_id': EMPLEADO_ACTIVO,
            'licencia_id': licencia,
        })
        empleado.save(force_insert=True)

        llave_usuario = Usuario._meta.pk.attname
        cuenta = Usuario(**{
            llave_usuario: siguiente_id(Usuario),
            'usuario': usuario_nombre,
            # RFN-03: PBKDF2 mediante el hasher de Django. Nunca texto plano.
            'contrasena': make_password(contrasena),
            'edo_usuario_id': USUARIO_ACTIVO,
            'empleado': empleado,
        })
        cuenta.save(force_insert=True)

        return cuenta


# ---------------------------------------------------------------------------
# RF58 - Registro de licencia
# ---------------------------------------------------------------------------

def siguiente_codigo_licencia():
    """Genera el consecutivo de LICENCIA.codigo, que es VARCHAR sin secuencia.

    Se toma el mayor sufijo numerico existente y se incrementa. Si la tabla
    esta vacia o los codigos no siguen el patron, arranca en LIC0001.
    Debe llamarse dentro de transaction.atomic().
    """
    import re

    mayor = 0
    for codigo in Licencia.objects.values_list('codigo', flat=True):
        encontrado = re.search(r'(\d+)$', codigo or '')
        if encontrado:
            mayor = max(mayor, int(encontrado.group(1)))

    for intento in range(mayor + 1, mayor + 1000):
        candidato = 'LIC{:04d}'.format(intento)
        if not Licencia.objects.filter(pk=candidato).exists():
            return candidato

    raise serializers.ValidationError(
        'No se pudo generar un codigo de licencia disponible.'
    )


class LicenciaSerializer(serializers.Serializer):
    """RF58 - Alta o renovacion de la licencia de un empleado."""

    numlicencia = serializers.CharField(max_length=20)
    tipo_licencia = serializers.CharField(max_length=10)
    vigencia = serializers.DateField()

    def __init__(self, *args, **kwargs):
        self.empleado = kwargs.pop('empleado', None)
        super().__init__(*args, **kwargs)

    def validate_tipo_licencia(self, valor):
        if not TipoLicencia.objects.filter(pk=valor).exists():
            raise serializers.ValidationError(
                'El tipo de licencia indicado no existe.'
            )
        return valor

    def validate_numlicencia(self, valor):
        valor = valor.strip().upper()

        # RF58: la licencia debe seguir el formato de Baja California:
        # 'BC' + exactamente 7 digitos numericos (ej. BC2071357).
        if not re.match(r'^BC\d{7}$', valor):
            raise serializers.ValidationError(
                'El numero de licencia debe iniciar con "BC" seguido de '
                'exactamente 7 digitos (ejemplo: BC1234567).'
            )

        existentes = Licencia.objects.filter(numlicencia=valor)
        # Al renovar, la propia licencia del empleado no cuenta como choque.
        if self.empleado is not None and self.empleado.licencia_id:
            existentes = existentes.exclude(pk=self.empleado.licencia_id)
        if existentes.exists():
            raise serializers.ValidationError(
                'Ese numero de licencia ya esta registrado.'
            )
        return valor

    def validate_vigencia(self, valor):
        if valor <= date.today():
            raise serializers.ValidationError(
                'La vigencia debe ser una fecha futura.'
            )
        return valor

    @transaction.atomic
    def guardar(self):
        datos = self.validated_data
        empleado = self.empleado

        if empleado.licencia_id:
            # Renovacion: se actualiza la licencia ya ligada.
            licencia = Licencia.objects.get(pk=empleado.licencia_id)
            licencia.numlicencia = datos['numlicencia']
            licencia.tipo_licencia_id = datos['tipo_licencia']
            licencia.vigencia = datos['vigencia']
            licencia.save()
        else:
            licencia = Licencia(
                codigo=siguiente_codigo_licencia(),
                numlicencia=datos['numlicencia'],
                tipo_licencia_id=datos['tipo_licencia'],
                vigencia=datos['vigencia'],
            )
            licencia.save(force_insert=True)
            empleado.licencia_id = licencia.pk
            empleado.save(update_fields=['licencia'])

        return licencia


# ---------------------------------------------------------------------------
# RF59 - Edicion de datos personales
# ---------------------------------------------------------------------------

class EditarDatosSerializer(serializers.Serializer):
    """RF59 - Modifica los datos personales del EMPLEADO."""

    nombre_de_pila = serializers.CharField(max_length=25)
    apellido_paterno = serializers.CharField(max_length=25)
    apellido_materno = serializers.CharField(
        max_length=25, required=False, allow_blank=True, allow_null=True,
    )
    fecha_nacimiento = serializers.DateField()
    telefono = serializers.CharField(max_length=15)
    email = serializers.EmailField(max_length=50)
    rol = serializers.CharField(max_length=10)

    def __init__(self, *args, **kwargs):
        self.empleado = kwargs.pop('empleado')
        super().__init__(*args, **kwargs)

    def validate_rol(self, valor):
        if not Rol.objects.filter(pk=valor).exists():
            raise serializers.ValidationError('El rol indicado no existe.')
        return valor

    def validate_email(self, valor):
        valor = valor.strip().lower()
        if (
            Empleado.objects
            .filter(email=valor)
            .exclude(pk=self.empleado.pk)
            .exists()
        ):
            raise serializers.ValidationError(
                'Ya existe otro empleado con ese correo.'
            )
        return valor

    def validate_telefono(self, valor):
        return validar_telefono(valor)

    @transaction.atomic
    def guardar(self):
        datos = self.validated_data
        empleado = self.empleado
        empleado.nombre_de_pila = datos['nombre_de_pila'].strip()
        empleado.apellido_paterno = datos['apellido_paterno'].strip()
        empleado.apellido_materno = (
            datos.get('apellido_materno') or ''
        ).strip() or None
        empleado.fecha_nacimiento = datos['fecha_nacimiento']
        empleado.telefono = datos['telefono']
        empleado.email = datos['email']
        empleado.rol_id = datos['rol']
        empleado.save()
        return empleado


# ---------------------------------------------------------------------------
# RF60 - Edicion de credenciales
# ---------------------------------------------------------------------------

class EditarCredencialesSerializer(serializers.Serializer):
    """RF60 - Cambia el nombre de usuario o la contrasena."""

    usuario = serializers.CharField(
        max_length=20, required=False, allow_blank=True,
    )
    contrasena = serializers.CharField(
        max_length=128, min_length=8, required=False,
        allow_blank=True, write_only=True,
    )

    def __init__(self, *args, **kwargs):
        self.cuenta = kwargs.pop('cuenta')
        super().__init__(*args, **kwargs)

    def validate_usuario(self, valor):
        valor = (valor or '').strip()
        if not valor:
            return None
        if (
            Usuario.objects
            .filter(usuario=valor)
            .exclude(pk=self.cuenta.pk)
            .exists()
        ):
            raise serializers.ValidationError(
                'Ese nombre de usuario ya esta ocupado.'
            )
        return valor

    def validate(self, datos):
        if not datos.get('usuario') and not datos.get('contrasena'):
            raise serializers.ValidationError(
                'Indica al menos un dato a modificar: usuario o contrasena.'
            )
        return datos

    @transaction.atomic
    def guardar(self):
        datos = self.validated_data
        cuenta = self.cuenta
        campos = []

        if datos.get('usuario'):
            cuenta.usuario = datos['usuario']
            campos.append('usuario')

        if datos.get('contrasena'):
            # RFN-03: siempre se rehashea, nunca se guarda en texto plano.
            cuenta.contrasena = make_password(datos['contrasena'])
            campos.append('contrasena')

        cuenta.save(update_fields=campos)
        return cuenta


# ---------------------------------------------------------------------------
# RF61 - Desactivacion de usuario (borrado logico)
# ---------------------------------------------------------------------------

class CambiarEstadoSerializer(serializers.Serializer):
    """RF61 - Activa o desactiva una cuenta sin borrar registros.

    Queda prohibido el DELETE fisico: la trazabilidad de pedidos, cobros y
    entregas depende de que el empleado siga existiendo.
    """

    activo = serializers.BooleanField()

    def __init__(self, *args, **kwargs):
        self.cuenta = kwargs.pop('cuenta')
        self.solicitante = kwargs.pop('solicitante', None)
        super().__init__(*args, **kwargs)

    def validate_activo(self, valor):
        # Un administrador no puede dejarse a si mismo sin acceso.
        if (
            not valor
            and self.solicitante is not None
            and self.cuenta.empleado_id == self.solicitante.pk
        ):
            raise serializers.ValidationError(
                'No puedes desactivar tu propia cuenta.'
            )
        return valor

    @transaction.atomic
    def guardar(self):
        activo = self.validated_data['activo']
        cuenta = self.cuenta

        cuenta.edo_usuario_id = USUARIO_ACTIVO if activo else USUARIO_INACTIVO
        cuenta.save(update_fields=['edo_usuario'])

        # El empleado sigue el mismo estado que su cuenta.
        empleado = cuenta.empleado
        empleado.edo_empleado_id = (
            EMPLEADO_ACTIVO if activo else EMPLEADO_INACTIVO
        )
        empleado.save(update_fields=['edo_empleado'])

        return cuenta