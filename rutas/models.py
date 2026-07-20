from django.db import models
from usuarios.models import Usuario
from establecimientos.models import Zona

class EdoRutaVisita(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

    class Meta:
        db_table = 'edo_ruta_visita'

class RutaVisita(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    zona = models.ForeignKey(Zona, on_delete=models.PROTECT)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='rutas_visita_vendedor'
    )
    coordinador = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='rutas_visita_coordinador'
    )
    edo_ruta_visita = models.ForeignKey(EdoRutaVisita, on_delete=models.PROTECT)

    class Meta:
        db_table = 'ruta_visita'

class EdoRutaEntrega(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

    class Meta:
        db_table = 'edo_ruta_entrega'

class RutaEntrega(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='rutas_entrega_repartidor'
    )
    coordinador = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='rutas_entrega_coordinador'
    )
    edo_ruta_entrega = models.ForeignKey(EdoRutaEntrega, on_delete=models.PROTECT)

    class Meta:
        db_table = 'ruta_entrega'