from django.db import models


class Producto(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=60)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    imagen = models.CharField(max_length=255, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_caducidad = models.DateField()
    stock = models.IntegerField(default=0)
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'producto'

    def __str__(self):
        return self.nombre