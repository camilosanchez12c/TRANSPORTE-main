from django.db import models
from django.utils import timezone

class Vehiculo(models.Model):
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='vehiculos')
    placa = models.CharField('placa', max_length=20, unique=True)
    tipo = models.CharField('tipo', max_length=50)
    capacidad = models.PositiveIntegerField('capacidad')
    soat_vencimiento = models.DateField('SOAT - vencimiento')
    tecnomecanica_vencimiento = models.DateField('Tecnomecánica - vencimiento')
    creado = models.DateTimeField('creado', auto_now_add=True)

    @property
    def disponible(self):
        hoy = timezone.now().date()
        return self.soat_vencimiento >= hoy and self.tecnomecanica_vencimiento >= hoy

    def __str__(self):
        return f"{self.placa} ({self.empresa.nombre})"

    class Meta:
        verbose_name = 'vehículo'
        verbose_name_plural = 'vehículos'
