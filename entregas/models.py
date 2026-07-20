from django.db import models
from usuarios.models import Usuario
from establecimientos.models import Establecimiento
from visitas.models import Pedido
from rutas.models import RutaEntrega

class Marca(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'marca'

class Modelo(models.Model):
    nombre = models.CharField(max_length=100)
    anio = models.IntegerField()
    capacidad = models.DecimalField(max_digits=10, decimal_places=2)
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT)

    class Meta:
        db_table = 'modelo'

class TipoVehiculo(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

    class Meta:
        db_table = 'tipo_vehiculo'

class EdoVehiculo(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

    class Meta:
        db_table = 'edo_vehiculo'

class Vehiculo(models.Model):
    serie_vin = models.CharField(max_length=100, unique=True)
    placas = models.CharField(max_length=20, unique=True)
    modelo = models.ForeignKey(Modelo, on_delete=models.PROTECT)
    tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.PROTECT)
    edo_vehiculo = models.ForeignKey(EdoVehiculo, on_delete=models.PROTECT)

    class Meta:
        db_table = 'vehiculo'

class CargaVehiculo(models.Model):
    fecha_carga = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT)

    class Meta:
        db_table = 'carga_vehiculo'

class EdoEntrega(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

    class Meta:
        db_table = 'edo_entrega'

class Entrega(models.Model):
    fecha_creacion = models.DateField(auto_now_add=True)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT)
    ruta_entrega = models.ForeignKey(RutaEntrega, on_delete=models.PROTECT, blank=True, null=True)
    edo_entrega = models.ForeignKey(EdoEntrega, on_delete=models.PROTECT)

    class Meta:
        db_table = 'entrega'

class EntregaEstablecimiento(models.Model):
    fecha_entrega = models.DateField()
    hora_entrega = models.TimeField()
    entrega = models.ForeignKey(Entrega, on_delete=models.PROTECT)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.PROTECT)

    class Meta:
        db_table = 'entrega_establecimiento'
        unique_together = ('entrega', 'establecimiento')

class TipoPago(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

    class Meta:
        db_table = 'tipo_pago'

class Pago(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    pedido = models.OneToOneField(Pedido, on_delete=models.PROTECT)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.PROTECT)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    tipo_pago = models.ForeignKey(TipoPago, on_delete=models.PROTECT)

    class Meta:
        db_table = 'pago'

class Devolucion(models.Model):
    cantidad = models.IntegerField()
    motivo = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    fecha = models.DateField(auto_now_add=True)
    entrega = models.ForeignKey(Entrega, on_delete=models.PROTECT)

    class Meta:
        db_table = 'devolucion'