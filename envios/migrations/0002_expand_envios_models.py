import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import envios.validators


class Migration(migrations.Migration):
    dependencies = [
        ("clientes", "0002_update_cliente_model"),
        ("rutas", "0002_update_ruta_model"),
        ("envios", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Empleado",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("codigo", models.CharField(max_length=10, unique=True)),
                ("nombres", models.CharField(max_length=100)),
                ("apellidos", models.CharField(max_length=100)),
                ("cargo", models.CharField(max_length=80)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("telefono", models.CharField(blank=True, max_length=15, null=True)),
                (
                    "estado",
                    models.IntegerField(
                        choices=[(1, "Activo"), (9, "De baja")],
                        default=1,
                    ),
                ),
                ("fecha_ingreso", models.DateField()),
                (
                    "rutas_asignadas",
                    models.ManyToManyField(
                        blank=True,
                        related_name="empleados_asignados",
                        to="rutas.ruta",
                    ),
                ),
            ],
            options={
                "db_table": "empleados",
                "ordering": ["apellidos"],
                "verbose_name": "Empleado",
                "verbose_name_plural": "Empleados",
            },
        ),
        migrations.RenameField(
            model_name="encomienda",
            old_name="fecha_envio",
            new_name="fecha_registro",
        ),
        migrations.RenameField(
            model_name="encomienda",
            old_name="fecha_entrega",
            new_name="fecha_entrega_real",
        ),
        migrations.AddField(
            model_name="encomienda",
            name="volumen_cm3",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=12,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="encomienda",
            name="remitente",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="envios_como_remitente",
                to="clientes.cliente",
            ),
        ),
        migrations.AddField(
            model_name="encomienda",
            name="destinatario",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="envios_como_destinatario",
                to="clientes.cliente",
            ),
        ),
        migrations.AddField(
            model_name="encomienda",
            name="ruta",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="encomiendas",
                to="rutas.ruta",
            ),
        ),
        migrations.AddField(
            model_name="encomienda",
            name="empleado_registro",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="encomiendas_registradas",
                to="envios.empleado",
            ),
        ),
        migrations.AddField(
            model_name="encomienda",
            name="costo_envio",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
        migrations.AddField(
            model_name="encomienda",
            name="fecha_entrega_est",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="encomienda",
            name="observaciones",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="codigo",
            field=models.CharField(
                max_length=20,
                unique=True,
                validators=[envios.validators.validar_codigo_encomienda],
            ),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="peso_kg",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=8,
                validators=[
                    envios.validators.validar_peso_positivo,
                    django.core.validators.MinValueValidator(
                        0.01,
                        message="El peso minimo es 0.01 kg",
                    ),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="estado",
            field=models.CharField(
                choices=[
                    ("PE", "Pendiente"),
                    ("TR", "En transito"),
                    ("DE", "En destino"),
                    ("EN", "Entregado"),
                    ("DV", "Devuelto"),
                ],
                default="PE",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="encomienda",
            name="fecha_entrega_real",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterModelTable(
            name="encomienda",
            table="encomiendas",
        ),
        migrations.AlterModelOptions(
            name="encomienda",
            options={
                "ordering": ["-fecha_registro"],
                "verbose_name": "Encomienda",
                "verbose_name_plural": "Encomiendas",
            },
        ),
        migrations.CreateModel(
            name="HistorialEstado",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "estado_anterior",
                    models.CharField(
                        choices=[
                            ("PE", "Pendiente"),
                            ("TR", "En transito"),
                            ("DE", "En destino"),
                            ("EN", "Entregado"),
                            ("DV", "Devuelto"),
                        ],
                        max_length=2,
                    ),
                ),
                (
                    "estado_nuevo",
                    models.CharField(
                        choices=[
                            ("PE", "Pendiente"),
                            ("TR", "En transito"),
                            ("DE", "En destino"),
                            ("EN", "Entregado"),
                            ("DV", "Devuelto"),
                        ],
                        max_length=2,
                    ),
                ),
                ("observacion", models.TextField(blank=True, null=True)),
                ("fecha_cambio", models.DateTimeField(auto_now_add=True)),
                (
                    "empleado",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="cambios_estado",
                        to="envios.empleado",
                    ),
                ),
                (
                    "encomienda",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="historial",
                        to="envios.encomienda",
                    ),
                ),
            ],
            options={
                "db_table": "historial_estados",
                "ordering": ["-fecha_cambio"],
                "verbose_name": "Historial de estado",
                "verbose_name_plural": "Historial de estados",
            },
        ),
    ]
