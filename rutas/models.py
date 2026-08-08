from django.db import models
from establecimientos.models import Zona


class EdoRutaVisita(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'edo_ruta_visita'

    def __str__(self):
        return self.nombre


class RutaVisita(models.Model):
    numero = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=150, blank=True, null=True)
    dia = models.CharField(max_length=10, default='Lunes')
    zona = models.ForeignKey(Zona, on_delete=models.DO_NOTHING, db_column='zona')
    empleado = models.ForeignKey(
        'usuarios.Empleado', on_delete=models.DO_NOTHING,
        db_column='empleado', blank=True, null=True
    )
    edo_ruta_visita = models.ForeignKey(
        EdoRutaVisita, on_delete=models.DO_NOTHING, db_column='edo_ruta_visita'
    )

    class Meta:
        managed = False
        db_table = 'ruta_visita'

    def __str__(self):
        return self.nombre


class RutaVisitaOrden(models.Model):
    ruta_visita = models.OneToOneField(
        RutaVisita, on_delete=models.DO_NOTHING,
        db_column='ruta_visita', primary_key=True
    )
    establecimiento = models.ForeignKey(
        'establecimientos.Establecimiento', on_delete=models.DO_NOTHING,
        db_column='establecimiento'
    )
    orden = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ruta_visita_orden'
        unique_together = (('ruta_visita', 'establecimiento'),)


class EdoRutaEntrega(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'edo_ruta_entrega'

    def __str__(self):
        return self.nombre


class RutaEntrega(models.Model):
    numero = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=40)
    descripcion = models.CharField(max_length=150, blank=True, null=True)
    empleado = models.ForeignKey(
        'usuarios.Empleado', on_delete=models.DO_NOTHING,
        db_column='empleado', blank=True, null=True
    )
    entrega = models.IntegerField(db_column='entrega', blank=True, null=True)
    edo_ruta_entrega = models.ForeignKey(
        EdoRutaEntrega, on_delete=models.DO_NOTHING, db_column='edo_ruta_entrega'
    )

    class Meta:
        managed = False
        db_table = 'ruta_entrega'

    def __str__(self):
        return self.nombre


class RutaEntregaOrden(models.Model):
    ruta_entrega = models.OneToOneField(
        RutaEntrega, on_delete=models.DO_NOTHING,
        db_column='ruta_entrega', primary_key=True
    )
    establecimiento = models.ForeignKey(
        'establecimientos.Establecimiento', on_delete=models.DO_NOTHING,
        db_column='establecimiento'
    )
    orden = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ruta_entrega_orden'
        unique_together = (('ruta_entrega', 'establecimiento'),)