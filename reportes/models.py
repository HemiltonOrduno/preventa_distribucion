"""
Modelos de solo lectura para el Modulo de Administrador (RF44 - RF55).

IMPORTANTE:
- Todos los modelos usan managed = False. El esquema lo manda database/*.sql,
  Django NUNCA debe crear ni alterar estas tablas.
- Todos los FK usan related_name='+' para no generar accesores inversos que
  choquen con los modelos que declaran otras apps sobre las mismas tablas.
- Los nombres de columna reales se mapean con db_column. No confiar en el SDD.
"""

from django.db import models


# ---------------------------------------------------------------------------
# Catalogos de estado y tipo
# ---------------------------------------------------------------------------

class EdoPedido(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'edo_pedido'

    def __str__(self):
        return self.nombre


class EdoEntrega(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'edo_entrega'

    def __str__(self):
        return self.nombre


class TipoPago(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_pago'

    def __str__(self):
        return self.nombre


class TipoMovimiento(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=25)
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_movimiento'

    def __str__(self):
        return self.nombre


# ---------------------------------------------------------------------------
# Geografia y clientes
# ---------------------------------------------------------------------------

class Zona(models.Model):
    num = models.IntegerField(primary_key=True, db_column='num')
    nombre = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    empleado = models.ForeignKey(
        'usuarios.Empleado', models.DO_NOTHING,
        db_column='empleado', related_name='+', blank=True, null=True,
    )

    class Meta:
        managed = False
        db_table = 'zona'

    def __str__(self):
        return self.nombre


class Establecimiento(models.Model):
    numero = models.IntegerField(primary_key=True, db_column='numero')
    nombre = models.CharField(max_length=100)
    calle = models.CharField(max_length=100, db_column='estCalle', blank=True, null=True)
    numero_ext = models.CharField(max_length=20, db_column='estNumero', blank=True, null=True)
    colonia = models.CharField(max_length=100, db_column='estColonia', blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    latitud = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    fecha_registro = models.DateField(blank=True, null=True)
    zona = models.ForeignKey(
        Zona, models.DO_NOTHING, db_column='zona',
        related_name='+', blank=True, null=True,
    )
    empleado = models.ForeignKey(
        'usuarios.Empleado', models.DO_NOTHING,
        db_column='empleado', related_name='+', blank=True, null=True,
    )
    # Columnas presentes en la tabla que el modulo de reportes no necesita
    # como relacion. Se declaran como enteros para no acoplarse a otras apps.
    entrega_id = models.IntegerField(db_column='entrega', blank=True, null=True)
    rep_establecimiento_id = models.IntegerField(
        db_column='rep_establecimiento', blank=True, null=True,
    )
    edo_establecimiento_id = models.CharField(
        db_column='edo_establecimiento', max_length=10, blank=True, null=True,
    )

    class Meta:
        managed = False
        db_table = 'establecimiento'

    def __str__(self):
        return self.nombre


# ---------------------------------------------------------------------------
# Productos
# ---------------------------------------------------------------------------

class Producto(models.Model):
    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=60)
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    imagen = models.CharField(max_length=255, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_caducidad = models.DateField(blank=True, null=True)
    stock = models.IntegerField(default=0)
    peso = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'producto'

    def __str__(self):
        return self.nombre


# ---------------------------------------------------------------------------
# Visitas y pedidos
# ---------------------------------------------------------------------------

class Visita(models.Model):
    numero = models.IntegerField(primary_key=True, db_column='numero')
    observaciones = models.CharField(max_length=200, blank=True, null=True)
    fecha = models.DateTimeField()
    establecimiento = models.ForeignKey(
        Establecimiento, models.DO_NOTHING,
        db_column='establecimiento', related_name='+',
    )
    empleado = models.ForeignKey(
        'usuarios.Empleado', models.DO_NOTHING,
        db_column='empleado', related_name='+',
    )
    ruta_visita_id = models.IntegerField(db_column='ruta_visita', blank=True, null=True)
    edo_visita_id = models.CharField(
        db_column='edo_visita', max_length=10, blank=True, null=True,
    )

    class Meta:
        managed = False
        db_table = 'visita'

    def __str__(self):
        return f'Visita {self.numero} - {self.fecha}'


class Entrega(models.Model):
    numero = models.IntegerField(primary_key=True, db_column='numero')
    fecha_creacion = models.DateField(blank=True, null=True)
    fecha_entrega = models.DateTimeField(blank=True, null=True)
    empleado = models.ForeignKey(
        'usuarios.Empleado', models.DO_NOTHING,
        db_column='empleado', related_name='+', blank=True, null=True,
    )
    edo_entrega = models.ForeignKey(
        EdoEntrega, models.DO_NOTHING,
        db_column='edo_entrega', related_name='+', blank=True, null=True,
    )

    class Meta:
        managed = False
        db_table = 'entrega'

    def __str__(self):
        return f'Entrega {self.numero}'


class Pedido(models.Model):
    num = models.IntegerField(primary_key=True, db_column='num')
    observaciones = models.CharField(max_length=200, blank=True, null=True)
    fecha = models.DateTimeField()
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, db_column='subtotal',
        blank=True, null=True,
    )
    iva = models.DecimalField(
        max_digits=10, decimal_places=2, db_column='iva',
        blank=True, null=True,
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
    )
    visita = models.ForeignKey(
        Visita, models.DO_NOTHING, db_column='visita', related_name='+',
    )
    entrega = models.ForeignKey(
        Entrega, models.DO_NOTHING, db_column='entrega',
        related_name='pedidos', blank=True, null=True,
    )
    edo_pedido = models.ForeignKey(
        EdoPedido, models.DO_NOTHING, db_column='edo_pedido', related_name='+',
    )

    class Meta:
        managed = False
        db_table = 'pedido'

    def __str__(self):
        return f'Pedido {self.num}'


class DetallePedido(models.Model):
    # Django no soporta PK compuestas: se declara num_pedido como PK y la
    # combinacion real se documenta en unique_together. Valido para lectura.
    num_pedido = models.ForeignKey(
        Pedido, models.DO_NOTHING, db_column='num_pedido',
        primary_key=True, related_name='detalles',
    )
    cod_producto = models.ForeignKey(
        Producto, models.DO_NOTHING, db_column='cod_producto', related_name='+',
    )
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2, db_column='precioUnitario',
    )
    importe = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'detalle_pedido'
        unique_together = (('num_pedido', 'cod_producto'),)


class EntregaEstablecimiento(models.Model):
    entrega = models.ForeignKey(
        Entrega, models.DO_NOTHING, db_column='entrega',
        primary_key=True, related_name='paradas',
    )
    establecimiento = models.ForeignKey(
        Establecimiento, models.DO_NOTHING,
        db_column='establecimiento', related_name='+',
    )
    fecha_entrega = models.DateField(blank=True, null=True)
    hora_entrega = models.TimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'entrega_estable'
        unique_together = (('entrega', 'establecimiento'),)


class RutaEntrega(models.Model):
    numero = models.IntegerField(primary_key=True, db_column='numero')
    nombre = models.CharField(max_length=40)
    descripcion = models.CharField(max_length=150, blank=True, null=True)
    empleado = models.ForeignKey(
        'usuarios.Empleado', models.DO_NOTHING,
        db_column='empleado', related_name='+', blank=True, null=True,
    )
    entrega = models.ForeignKey(
        Entrega, models.DO_NOTHING, db_column='entrega',
        related_name='rutas', blank=True, null=True,
    )
    edo_ruta_entrega_id = models.CharField(
        db_column='edo_ruta_entrega', max_length=10, blank=True, null=True,
    )

    class Meta:
        managed = False
        db_table = 'ruta_entrega'

    def __str__(self):
        return self.nombre


# ---------------------------------------------------------------------------
# Cobranza y devoluciones
# ---------------------------------------------------------------------------

class Pago(models.Model):
    codigo = models.AutoField(primary_key=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField()
    tipo_pago = models.ForeignKey(
        TipoPago, models.DO_NOTHING, db_column='tipo_pago', related_name='+',
    )
    empleado = models.ForeignKey(
        'usuarios.Empleado', models.DO_NOTHING,
        db_column='empleado', related_name='+',
    )
    establecimiento = models.ForeignKey(
        Establecimiento, models.DO_NOTHING,
        db_column='establecimiento', related_name='+',
    )
    pedido = models.ForeignKey(
        Pedido, models.DO_NOTHING, db_column='pedido', related_name='pagos',
    )

    class Meta:
        managed = False
        db_table = 'pago'

    def __str__(self):
        return f'Pago {self.codigo} - ${self.monto}'


class Devolucion(models.Model):
    codigo = models.AutoField(primary_key=True)
    fecha = models.DateField()
    cantidad = models.IntegerField()
    motivo = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    entrega = models.ForeignKey(
        Entrega, models.DO_NOTHING, db_column='entrega',
        related_name='devoluciones', blank=True, null=True,
    )

    class Meta:
        managed = False
        db_table = 'devolucion'

    def __str__(self):
        return f'Devolucion {self.codigo}'


# ---------------------------------------------------------------------------
# Inventario
# ---------------------------------------------------------------------------

class Movimiento(models.Model):
    codigo = models.AutoField(primary_key=True)
    observaciones = models.CharField(max_length=150, blank=True, null=True)
    fecha = models.DateTimeField()
    tipo_movimiento = models.ForeignKey(
        TipoMovimiento, models.DO_NOTHING,
        db_column='tipo_movimiento', related_name='+',
    )
    devolucion = models.ForeignKey(
        Devolucion, models.DO_NOTHING, db_column='devolucion',
        related_name='movimientos', blank=True, null=True,
    )
    empleado = models.ForeignKey(
        'usuarios.Empleado', models.DO_NOTHING,
        db_column='empleado', related_name='+',
    )

    class Meta:
        managed = False
        db_table = 'movimientos'

    def __str__(self):
        return f'Movimiento {self.codigo}'


class DetalleMovimiento(models.Model):
    # Ojo: la columna real es 'cod_movimientos', en plural.
    cod_movimiento = models.ForeignKey(
        Movimiento, models.DO_NOTHING, db_column='cod_movimientos',
        primary_key=True, related_name='detalles',
    )
    cod_producto = models.ForeignKey(
        Producto, models.DO_NOTHING, db_column='cod_producto', related_name='+',
    )
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2, db_column='precioUnitario',
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'detalle_movimiento'
        unique_together = (('cod_movimiento', 'cod_producto'),)


# ---------------------------------------------------------------------------
# Vista SQL para reportes agregados (RF50 / RF51)
# ---------------------------------------------------------------------------

class VistaReporteVentasAdmin(models.Model):
    """Mapea la vista SQL vta_reporte_ventas_admin (solo lectura).

    Las vistas no tienen PK real: se marca zona_id como primary_key para
    satisfacer al ORM. Usar siempre con .values() o .filter(), nunca con
    .get(pk=...), porque zona_id se repite entre periodos y vendedores.
    """

    zona_id = models.IntegerField(primary_key=True)
    zona_nombre = models.CharField(max_length=20)
    periodo = models.CharField(max_length=7, blank=True, null=True)
    total_pedidos = models.BigIntegerField()
    total_subtotal = models.DecimalField(
        max_digits=32, decimal_places=2, blank=True, null=True,
    )
    total_iva = models.DecimalField(
        max_digits=32, decimal_places=2, blank=True, null=True,
    )
    total_ventas = models.DecimalField(
        max_digits=32, decimal_places=2, blank=True, null=True,
    )
    pedidos_entregados = models.BigIntegerField()
    pedidos_cancelados = models.BigIntegerField()
    vendedor = models.CharField(max_length=51)

    class Meta:
        managed = False
        db_table = 'vta_reporte_ventas_admin'


# ---------------------------------------------------------------------------
# Catalogos y tablas de personal (Modulo 9 - Gestion de usuarios)
# ---------------------------------------------------------------------------

class Rol(models.Model):
    """R001 Administrador, R002 Coordinador, R003 Vendedor,
    R004 Almacenista, R005 Repartidor."""

    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rol'

    def __str__(self):
        return self.nombre


class EdoUsuario(models.Model):
    """EU001 Activo, EU002 Inactivo."""

    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'edo_usuario'

    def __str__(self):
        return self.nombre


class EdoEmpleado(models.Model):
    """EE001 Activo, EE002 Inactivo."""

    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'edo_empleado'

    def __str__(self):
        return self.nombre


class TipoLicencia(models.Model):
    """A1 Automovilista, B1 Tipo B, C1 Tipo C, DC1 Montacarguista."""

    codigo = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_licencia'

    def __str__(self):
        return self.nombre


class Licencia(models.Model):
    """Licencia de conducir u operacion.

    OJO: la tabla real NO tiene columna 'usuario'. La relacion va en
    sentido contrario: EMPLEADO.licencia apunta aqui. El modelo de la app
    usuarios declara un FK 'usuario' que no existe en la base y fallara al
    consultarse; por eso se declara aqui la version correcta.
    """

    codigo = models.CharField(primary_key=True, max_length=10)
    numlicencia = models.CharField(max_length=20, unique=True)
    vigencia = models.DateField()
    tipo_licencia = models.ForeignKey(
        TipoLicencia, models.DO_NOTHING,
        db_column='tipo_licencia', related_name='+',
    )

    class Meta:
        managed = False
        db_table = 'licencia'

    def __str__(self):
        return self.numlicencia