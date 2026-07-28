

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Rol',
            fields=[
                ('codigo', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=20, unique=True)),
                ('descripcion', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'rol',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EdoUsuario',
            fields=[
                ('codigo', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=20, unique=True)),
                ('descripcion', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'edo_usuario',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EdoEmpleado',
            fields=[
                ('codigo', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=20, unique=True)),
                ('descripcion', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'edo_empleado',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TipoLicencia',
            fields=[
                ('codigo', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=20, unique=True)),
                ('descripcion', models.CharField(blank=True, max_length=150, null=True)),
            ],
            options={
                'db_table': 'tipo_licencia',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Licencia',
            fields=[
                ('codigo', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('numlicencia', models.CharField(max_length=20, unique=True)),
                ('vigencia', models.DateField()),
                ('tipo_licencia', models.ForeignKey(db_column='tipo_licencia', on_delete=django.db.models.deletion.DO_NOTHING, to='usuarios.tipolicencia')),
            ],
            options={
                'db_table': 'licencia',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Empleado',
            fields=[
                ('num', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre_de_pila', models.CharField(db_column='empNombre', max_length=25)),
                ('apellido_paterno', models.CharField(db_column='empApellPat', max_length=25)),
                ('apellido_materno', models.CharField(blank=True, db_column='empApellMa', max_length=25, null=True)),
                ('fecha_nacimiento', models.DateField()),
                ('telefono', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=50, unique=True)),
                ('edo_empleado', models.ForeignKey(db_column='edo_empleado', on_delete=django.db.models.deletion.DO_NOTHING, to='usuarios.edoempleado')),
                ('rol', models.ForeignKey(db_column='rol', on_delete=django.db.models.deletion.DO_NOTHING, to='usuarios.rol')),
                ('licencia', models.ForeignKey(blank=True, db_column='licencia', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='usuarios.licencia')),
            ],
            options={
                'db_table': 'empleado',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('num', models.IntegerField(primary_key=True, serialize=False)),
                ('usuario', models.CharField(max_length=20, unique=True)),
                ('contrasena', models.CharField(db_column='contraseña', max_length=255)),
                ('edo_usuario', models.ForeignKey(db_column='edo_usuario', on_delete=django.db.models.deletion.DO_NOTHING, to='usuarios.edousuario')),
                ('empleado', models.ForeignKey(db_column='empleado', on_delete=django.db.models.deletion.DO_NOTHING, to='usuarios.empleado')),
            ],
            options={
                'db_table': 'usuario',
                'managed': False,
            },
        ),
    ]