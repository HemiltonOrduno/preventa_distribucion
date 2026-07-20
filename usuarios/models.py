from django.db import models

class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

    class Meta:
        db_table = 'rol'

class EdoUsuario(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

    class Meta:
        db_table = 'edo_usuario'

class Usuario(models.Model):
    usuario = models.CharField(max_length=50, unique=True)
    contrasena = models.CharField(max_length=255)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT)
    edo_usuario = models.ForeignKey(EdoUsuario, on_delete=models.PROTECT)

    class Meta:
        db_table = 'usuario'

class EdoEmpleado(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

    class Meta:
        db_table = 'edo_empleado'

class Empleado(models.Model):
    nombre_de_pila = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    fecha_nacimiento = models.DateField()
    usuario = models.OneToOneField(Usuario, on_delete=models.PROTECT)
    edo_empleado = models.ForeignKey(EdoEmpleado, on_delete=models.PROTECT)

    class Meta:
        db_table = 'empleado'

class TipoLicencia(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

    class Meta:
        db_table = 'tipo_licencia'

class Licencia(models.Model):
    num_licencia = models.CharField(max_length=50)
    vigencia = models.DateField()
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    tipo_licencia = models.ForeignKey(TipoLicencia, on_delete=models.PROTECT)

    class Meta:
        db_table = 'licencia'