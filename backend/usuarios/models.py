from django.db import models


class Rol(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rol'

    def __str__(self):
        return self.nombre


class EdoUsuario(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'edo_usuario'

    def __str__(self):
        return self.nombre


class EdoEmpleado(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'edo_empleado'

    def __str__(self):
        return self.nombre


class TipoLicencia(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_licencia'

    def __str__(self):
        return self.nombre


class Licencia(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    numlicencia = models.CharField(max_length=20, unique=True)
    vigencia = models.DateField()
    tipo_licencia = models.ForeignKey(
        TipoLicencia, on_delete=models.DO_NOTHING, db_column='tipo_licencia'
    )

    class Meta:
        managed = False
        db_table = 'licencia'

    def __str__(self):
        return self.numlicencia


class Empleado(models.Model):
    num = models.AutoField(primary_key=True)
    nombre_de_pila = models.CharField(max_length=25, db_column='empNombre')
    apellido_paterno = models.CharField(max_length=25, db_column='empApellPat')
    apellido_materno = models.CharField(max_length=25, db_column='empApellMa', blank=True, null=True)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=15)
    email = models.EmailField(max_length=50, unique=True)
    edo_empleado = models.ForeignKey(
        EdoEmpleado, on_delete=models.DO_NOTHING, db_column='edo_empleado'
    )
    rol = models.ForeignKey(
        Rol, on_delete=models.DO_NOTHING, db_column='rol'
    )
    licencia = models.ForeignKey(
        Licencia, on_delete=models.DO_NOTHING, db_column='licencia', blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = 'empleado'

    def __str__(self):
        return f"{self.nombre_de_pila} {self.apellido_paterno}"


class Usuario(models.Model):
    num = models.AutoField(primary_key=True)
    usuario = models.CharField(max_length=20, unique=True)
    contrasena = models.CharField(max_length=255, db_column='contraseña')
    edo_usuario = models.ForeignKey(
        EdoUsuario, on_delete=models.DO_NOTHING, db_column='edo_usuario'
    )
    empleado = models.ForeignKey(
        Empleado, on_delete=models.DO_NOTHING, db_column='empleado'
    )

    class Meta:
        managed = False
        db_table = 'usuario'

    def __str__(self):
        return self.usuario