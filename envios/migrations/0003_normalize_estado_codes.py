from django.db import migrations


def actualizar_codigos_estado(apps, schema_editor):
    Encomienda = apps.get_model("envios", "Encomienda")
    HistorialEstado = apps.get_model("envios", "HistorialEstado")

    Encomienda.objects.filter(estado="DE").update(estado="DV")
    HistorialEstado.objects.filter(estado_anterior="DE").update(estado_anterior="DV")
    HistorialEstado.objects.filter(estado_nuevo="DE").update(estado_nuevo="DV")


class Migration(migrations.Migration):
    dependencies = [
        ("envios", "0002_expand_envios_models"),
    ]

    operations = [
        migrations.RunPython(
            actualizar_codigos_estado,
            migrations.RunPython.noop,
        ),
    ]
