from django.db import models

class Zona(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)

    class Meta:
        db_table = 'zona'

class EdoEstablecimiento(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

    class Meta:
        db_table = 'edo_establecimiento'

class Establecimiento(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    calle = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    colonia = models.CharField(max_length=100)
    latitud = models.DecimalField(max_digits=10, decimal_places=6)
    longitud = models.DecimalField(max_digits=10, decimal_places=6)
    fecha_registro = models.DateField(auto_now_add=True)
    zona = models.ForeignKey(Zona, on_delete=models.PROTECT)
    edo_establecimiento = models.ForeignKey(EdoEstablecimiento, on_delete=models.PROTECT)

    class Meta:
        db_table = 'establecimiento'

class EdoRepEstablecimiento(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

    class Meta:
        db_table = 'edo_rep_establecimiento'

class RepEstablecimiento(models.Model):
    nombre_de_pila = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    fecha_registro = models.DateField(auto_now_add=True)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.PROTECT)
    edo_rep_establecimiento = models.ForeignKey(EdoRepEstablecimiento, on_delete=models.PROTECT)

    class Meta:
        db_table = 'rep_establecimiento'