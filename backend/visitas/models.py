from django.db import models
from establecimientos.models import Establecimiento


class EdoVisita(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=25, unique=True)
    descripcion = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'edo_visita'


class Visita(models.Model):
    numero = models.AutoField(primary_key=True)
    observaciones = models.CharField(max_length=200, blank=True, null=True)
    fecha = models.DateTimeField()
    ruta_visita = models.IntegerField(db_column='ruta_visita')
    establecimiento = models.ForeignKey(
        Establecimiento, on_delete=models.DO_NOTHING, db_column='establecimiento'
    )
    empleado = models.ForeignKey(
        'usuarios.Empleado', on_delete=models.DO_NOTHING, db_column='empleado'
    )
    edo_visita = models.ForeignKey(
        EdoVisita, on_delete=models.DO_NOTHING, db_column='edo_visita',
        blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = 'visita'


class EdoPedido(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'edo_pedido'


class Pedido(models.Model):
    num = models.AutoField(primary_key=True)
    observaciones = models.CharField(max_length=200, blank=True, null=True)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha = models.DateTimeField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    visita = models.ForeignKey(Visita, on_delete=models.DO_NOTHING, db_column='visita')
    entrega = models.IntegerField(db_column='entrega', blank=True, null=True)
    edo_pedido = models.ForeignKey(
        EdoPedido, on_delete=models.DO_NOTHING, db_column='edo_pedido'
    )

    class Meta:
        managed = False
        db_table = 'pedido'


class DetallePedido(models.Model):
    num_pedido = models.OneToOneField(
        Pedido, on_delete=models.DO_NOTHING, db_column='num_pedido', primary_key=True
    )
    cod_producto = models.ForeignKey(
        'productos.Producto', on_delete=models.DO_NOTHING, db_column='cod_producto'
    )
    cantidad = models.IntegerField()
    precioUnitario = models.DecimalField(max_digits=10, decimal_places=2)
    importe = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        managed = False
        db_table = 'detalle_pedido'
        unique_together = (('num_pedido', 'cod_producto'),)