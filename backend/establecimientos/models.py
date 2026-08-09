from django.db import models


class Zona(models.Model):
    num = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    empleado = models.ForeignKey(
        'usuarios.Empleado', on_delete=models.DO_NOTHING, db_column='empleado'
    )
    lat_min = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    lat_max = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    lon_min = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    lon_max = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'zona'

    def __str__(self):
        return self.nombre


class EdoEstablecimiento(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'edo_establecimiento'


class EdoRepEstablecimiento(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'edo_rep_establecimiento'


class RepEstablecimiento(models.Model):
    numero = models.AutoField(primary_key=True)
    rfc = models.CharField(max_length=13, unique=True)
    nombre_de_pila = models.CharField(max_length=20, db_column='repNombre')
    apellido_paterno = models.CharField(max_length=20, db_column='repApellPat')
    apellido_materno = models.CharField(max_length=20, db_column='repApellMa', blank=True, null=True)
    telefono = models.CharField(max_length=15)
    email = models.EmailField(max_length=60, unique=True)
    fecha_registro = models.DateField()
    empleado = models.ForeignKey(
        'usuarios.Empleado', on_delete=models.DO_NOTHING, db_column='empleado'
    )
    edo_rep_establecimiento = models.ForeignKey(
        EdoRepEstablecimiento, on_delete=models.DO_NOTHING,
        db_column='edo_rep_establecimiento'
    )

    class Meta:
        managed = False
        db_table = 'rep_establecimiento'


class Establecimiento(models.Model):
    numero = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)
    calle = models.CharField(max_length=40, db_column='estCalle')
    numero_ext = models.CharField(max_length=10, db_column='estNumero')
    colonia = models.CharField(max_length=40, db_column='estColonia')
    telefono = models.CharField(max_length=15)
    latitud = models.DecimalField(max_digits=10, decimal_places=6)
    longitud = models.DecimalField(max_digits=10, decimal_places=6)
    fecha_registro = models.DateField()
    zona = models.ForeignKey(Zona, on_delete=models.DO_NOTHING, db_column='zona')
    empleado = models.ForeignKey(
        'usuarios.Empleado', on_delete=models.DO_NOTHING, db_column='empleado'
    )
    entrega = models.IntegerField(db_column='entrega', blank=True, null=True)
    rep_establecimiento = models.ForeignKey(
        RepEstablecimiento, on_delete=models.DO_NOTHING, db_column='rep_establecimiento'
    )
    edo_establecimiento = models.ForeignKey(
        EdoEstablecimiento, on_delete=models.DO_NOTHING, db_column='edo_establecimiento'
    )

    class Meta:
        managed = False
        db_table = 'establecimiento'

    def __str__(self):
        return self.nombre