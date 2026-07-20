from django.db import models
from usuarios.models import Usuario
from productos.models import Producto

class TipoMovimiento(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

    class Meta:
        db_table = 'tipo_movimiento'

class Movimiento(models.Model):
    fecha = models.DateField(auto_now_add=True)
    observaciones = models.CharField(max_length=200, blank=True, null=True)
    tipo_movimiento = models.ForeignKey(TipoMovimiento, on_delete=models.PROTECT)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    devolucion = models.ForeignKey(
        'entregas.Devolucion',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'movimiento'

class DetalleMovimiento(models.Model):
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    movimiento = models.ForeignKey(Movimiento, on_delete=models.PROTECT)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)

    class Meta:
        db_table = 'detalle_movimiento'
        unique_together = ('movimiento', 'producto')