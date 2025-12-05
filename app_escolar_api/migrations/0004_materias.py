

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_escolar_api', '0003_alumnos_maestros'),
    ]

    operations = [
        migrations.CreateModel(
            name='Materias',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('nrc', models.CharField(max_length=6, unique=True)),
                ('nombre', models.CharField(max_length=255)),
                ('seccion', models.CharField(max_length=3)),
                ('dias', models.TextField(blank=True, null=True)),
                ('hora_inicio', models.TimeField(blank=True, null=True)),
                ('hora_fin', models.TimeField(blank=True, null=True)),
                ('salon', models.CharField(blank=True, max_length=15, null=True)),
                ('programa_educativo', models.CharField(blank=True, max_length=255, null=True)),
                ('creditos', models.IntegerField(blank=True, null=True)),
                ('creation', models.DateTimeField(auto_now_add=True, null=True)),
                ('update', models.DateTimeField(blank=True, null=True)),
                ('profesor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app_escolar_api.maestros')),
            ],
        ),
    ]
