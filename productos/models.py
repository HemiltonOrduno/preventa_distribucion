from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    fecha_caducidad = models.DateField()
    stock = models.IntegerField(default=0)
    peso = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'producto'