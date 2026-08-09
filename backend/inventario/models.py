from django.db import models
from productos.models import Producto


class TipoMovimiento(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=25, unique=True)
    descripcion = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_movimiento'

    def __str__(self):
        return self.nombre


class Movimiento(models.Model):
    codigo = models.AutoField(primary_key=True)
    observaciones = models.CharField(max_length=150, blank=True, null=True)
    fecha = models.DateTimeField()
    tipo_movimiento = models.ForeignKey(
        TipoMovimiento, on_delete=models.DO_NOTHING, db_column='tipo_movimiento'
    )
    devolucion = models.IntegerField(db_column='devolucion', blank=True, null=True)
    empleado = models.IntegerField(db_column='empleado')

    class Meta:
        managed = False
        db_table = 'movimientos'


class DetalleMovimiento(models.Model):
    cod_movimientos = models.OneToOneField(
        Movimiento, on_delete=models.DO_NOTHING,
        db_column='cod_movimientos', primary_key=True
    )
    cod_producto = models.ForeignKey(
        Producto, on_delete=models.DO_NOTHING, db_column='cod_producto'
    )
    cantidad = models.IntegerField()
    precioUnitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'detalle_movimiento'
        unique_together = (('cod_movimientos', 'cod_producto'),)