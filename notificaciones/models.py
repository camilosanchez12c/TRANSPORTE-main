from django.db import models
from django.conf import settings

class Notificacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones')
    titulo = models.CharField('título', max_length=200)
    cuerpo = models.TextField('cuerpo')
    leida = models.BooleanField('leída', default=False)
    creada = models.DateTimeField('creada', auto_now_add=True)

    class Meta:
        verbose_name = 'notificación'
        verbose_name_plural = 'notificaciones'

    def __str__(self):
        return self.titulo
