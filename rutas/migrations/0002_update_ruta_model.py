from django.db import migrations, models


def migrar_estado_ruta(apps, schema_editor):
    Ruta = apps.get_model("rutas", "Ruta")

    for ruta in Ruta.objects.all():
        ruta.estado = 1 if ruta.activa else 9
        ruta.save(update_fields=["estado"])


class Migration(migrations.Migration):
    dependencies = [
        ("rutas", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="ruta",
            name="descripcion",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="ruta",
            name="precio_base",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="ruta",
            name="dias_entrega",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="ruta",
            name="estado",
            field=models.IntegerField(
                choices=[(1, "Activo"), (9, "De baja")],
                default=1,
            ),
        ),
        migrations.AlterField(
            model_name="ruta",
            name="codigo",
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name="ruta",
            name="origen",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="ruta",
            name="destino",
            field=models.CharField(max_length=100),
        ),
        migrations.RunPython(
            migrar_estado_ruta,
            migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name="ruta",
            name="distancia_km",
        ),
        migrations.RemoveField(
            model_name="ruta",
            name="activa",
        ),
        migrations.RemoveField(
            model_name="ruta",
            name="fecha_creacion",
        ),
        migrations.AlterModelTable(
            name="ruta",
            table="rutas",
        ),
        migrations.AlterModelOptions(
            name="ruta",
            options={
                "ordering": ["origen", "destino"],
                "verbose_name": "Ruta",
                "verbose_name_plural": "Rutas",
            },
        ),
    ]
