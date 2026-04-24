from django.db import migrations, models


def migrar_nombre_completo(apps, schema_editor):
    Cliente = apps.get_model("clientes", "Cliente")

    for cliente in Cliente.objects.all():
        nombre_completo = (getattr(cliente, "nombre_completo", "") or "").strip()
        partes = nombre_completo.split()

        if len(partes) >= 3:
            cliente.nombres = " ".join(partes[:-2])
            cliente.apellidos = " ".join(partes[-2:])
        elif len(partes) == 2:
            cliente.nombres = partes[0]
            cliente.apellidos = partes[1]
        elif len(partes) == 1:
            cliente.nombres = partes[0]
            cliente.apellidos = ""
        else:
            cliente.nombres = ""
            cliente.apellidos = ""

        cliente.save(update_fields=["nombres", "apellidos"])


class Migration(migrations.Migration):
    dependencies = [
        ("clientes", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="cliente",
            old_name="documento",
            new_name="nro_doc",
        ),
        migrations.AddField(
            model_name="cliente",
            name="tipo_doc",
            field=models.CharField(
                choices=[("DNI", "DNI"), ("RUC", "RUC"), ("PAS", "Pasaporte")],
                default="DNI",
                max_length=3,
            ),
        ),
        migrations.AddField(
            model_name="cliente",
            name="nombres",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="cliente",
            name="apellidos",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="cliente",
            name="estado",
            field=models.IntegerField(
                choices=[(1, "Activo"), (9, "De baja")],
                default=1,
            ),
        ),
        migrations.AlterField(
            model_name="cliente",
            name="nro_doc",
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name="cliente",
            name="telefono",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name="cliente",
            name="email",
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name="cliente",
            name="direccion",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.RunPython(
            migrar_nombre_completo,
            migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name="cliente",
            name="nombre_completo",
        ),
        migrations.AlterModelTable(
            name="cliente",
            table="clientes",
        ),
        migrations.AlterModelOptions(
            name="cliente",
            options={
                "ordering": ["apellidos", "nombres"],
                "verbose_name": "Cliente",
                "verbose_name_plural": "Clientes",
            },
        ),
    ]
