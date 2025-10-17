from django.db import models
from django.conf import settings

class RegistroOperacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    accion = models.CharField('acción', max_length=255)
    tipo_objeto = models.CharField('tipo_objeto', max_length=100, blank=True)
    objeto_id = models.CharField('objeto_id', max_length=100, blank=True)
    datos = models.JSONField('datos', null=True, blank=True)
    creado = models.DateTimeField('creado', auto_now_add=True)

    class Meta:
        verbose_name = 'registro de operación'
        verbose_name_plural = 'registros de operación'

    def __str__(self):
        return f"{self.accion} - {self.creado}"
