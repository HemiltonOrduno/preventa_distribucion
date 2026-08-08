from django.db import models
from establecimientos.models import Establecimiento


class EdoVehiculo(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'edo_vehiculo'

    def __str__(self):
        return self.nombre


class Marca(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)

    class Meta:
        managed = False
        db_table = 'marca'

    def __str__(self):
        return self.nombre


class TipoVehiculo(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_vehiculo'

    def __str__(self):
        return self.nombre


class Modelo(models.Model):
    numero = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)
    ano = models.IntegerField()
    capacidad = models.DecimalField(max_digits=10, decimal_places=2)
    marca = models.ForeignKey(Marca, on_delete=models.DO_NOTHING, db_column='marca')

    class Meta:
        managed = False
        db_table = 'modelo'

    def __str__(self):
        return self.nombre


class EdoEntrega(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'edo_entrega'

    def __str__(self):
        return self.nombre


class Entrega(models.Model):
    numero = models.AutoField(primary_key=True)
    fecha_creacion = models.DateField()
    fecha_entrega = models.DateTimeField(blank=True, null=True)
    empleado = models.ForeignKey(
        'usuarios.Empleado', on_delete=models.DO_NOTHING, db_column='empleado'
    )
    edo_entrega = models.ForeignKey(
        EdoEntrega, on_delete=models.DO_NOTHING, db_column='edo_entrega'
    )

    class Meta:
        managed = False
        db_table = 'entrega'


class Vehiculo(models.Model):
    numero = models.AutoField(primary_key=True)
    serie_vin = models.CharField(max_length=20, unique=True)
    placas = models.CharField(max_length=10, unique=True)
    tipo_vehiculo = models.ForeignKey(
        TipoVehiculo, on_delete=models.DO_NOTHING, db_column='tipo_vehiculo'
    )
    modelo = models.ForeignKey(Modelo, on_delete=models.DO_NOTHING, db_column='modelo')
    edo_vehiculo = models.ForeignKey(
        EdoVehiculo, on_delete=models.DO_NOTHING, db_column='edo_vehiculo'
    )
    empleado = models.ForeignKey(
        'usuarios.Empleado', on_delete=models.DO_NOTHING, db_column='empleado'
    )
    entrega = models.ForeignKey(
        Entrega, on_delete=models.DO_NOTHING,
        db_column='entrega', blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = 'vehiculo'

    def __str__(self):
        return self.placas


class EmpVehiculo(models.Model):
    empleado = models.OneToOneField(
        'usuarios.Empleado', on_delete=models.DO_NOTHING,
        db_column='empleado', primary_key=True
    )
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.DO_NOTHING, db_column='vehiculo'
    )
    fecha_cargo = models.DateField()

    class Meta:
        managed = False
        db_table = 'emp_vehiculo'
        unique_together = (('empleado', 'vehiculo', 'fecha_cargo'),)


class EntregaEstable(models.Model):
    entrega = models.OneToOneField(
        Entrega, on_delete=models.DO_NOTHING,
        db_column='entrega', primary_key=True
    )
    establecimiento = models.ForeignKey(
        Establecimiento, on_delete=models.DO_NOTHING, db_column='establecimiento'
    )
    fecha_entrega = models.DateField()
    hora_entrega = models.TimeField()

    class Meta:
        managed = False
        db_table = 'entrega_estable'
        unique_together = (('entrega', 'establecimiento'),)


class TipoPago(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_pago'

    def __str__(self):
        return self.nombre


class Pago(models.Model):
    codigo = models.AutoField(primary_key=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField()
    tipo_pago = models.ForeignKey(
        TipoPago, on_delete=models.DO_NOTHING, db_column='tipo_pago'
    )
    empleado = models.ForeignKey(
        'usuarios.Empleado', on_delete=models.DO_NOTHING, db_column='empleado'
    )
    establecimiento = models.ForeignKey(
        Establecimiento, on_delete=models.DO_NOTHING, db_column='establecimiento'
    )
    pedido = models.ForeignKey(
        'visitas.Pedido', on_delete=models.DO_NOTHING, db_column='pedido'
    )

    class Meta:
        managed = False
        db_table = 'pago'


class Devolucion(models.Model):
    codigo = models.AutoField(primary_key=True)
    fecha = models.DateField()
    cantidad = models.IntegerField()
    motivo = models.CharField(max_length=40)
    descripcion = models.CharField(max_length=150, blank=True, null=True)
    entrega = models.ForeignKey(
        Entrega, on_delete=models.DO_NOTHING, db_column='entrega'
    )
    cod_producto = models.ForeignKey(
        'productos.Producto', on_delete=models.DO_NOTHING,
        db_column='cod_producto', blank=True, null=True
    )
    pedido = models.ForeignKey(
        'visitas.Pedido', on_delete=models.DO_NOTHING,
        db_column='pedido', blank=True, null=True
    )
    importe = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = 'devolucion'