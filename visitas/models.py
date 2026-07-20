from django.db import models
from usuarios.models import Usuario
from establecimientos.models import Establecimiento

class EdoVisita(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

    class Meta:
        db_table = 'edo_visita'

class Visita(models.Model):
    fecha = models.DateField()
    observaciones = models.CharField(max_length=200, blank=True, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.PROTECT)
    edo_visita = models.ForeignKey(EdoVisita, on_delete=models.PROTECT)

    class Meta:
        db_table = 'visita'

class EdoPedido(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

    class Meta:
        db_table = 'edo_pedido'

class Pedido(models.Model):
    fecha = models.DateField(auto_now_add=True)
    observaciones = models.CharField(max_length=200, blank=True, null=True)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    visita = models.OneToOneField(Visita, on_delete=models.PROTECT)
    edo_pedido = models.ForeignKey(EdoPedido, on_delete=models.PROTECT)

    class Meta:
        db_table = 'pedido'

class DetallePedido(models.Model):
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    importe = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT)
    producto = models.ForeignKey('productos.Producto', on_delete=models.PROTECT)

    class Meta:
        db_table = 'detalle_pedido'
        unique_together = ('pedido', 'producto')