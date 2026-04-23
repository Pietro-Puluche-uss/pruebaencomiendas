from django.db import models


class Ruta(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    origen = models.CharField(max_length=120)
    destino = models.CharField(max_length=120)
    distancia_km = models.DecimalField(max_digits=8, decimal_places=2)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.codigo}: {self.origen} - {self.destino}"

    class Meta:
        verbose_name = "Ruta"
        verbose_name_plural = "Rutas"
        ordering = ["codigo"]
