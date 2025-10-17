from django.db import models
from django.conf import settings

class Documento(models.Model):
    archivo = models.FileField('archivo', upload_to='documentos/')
    nombre = models.CharField('nombre', max_length=255)
    tamano = models.PositiveIntegerField('tamaño_bytes')
    subido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='documentos')
    estado = models.CharField('estado', max_length=20, choices=(('pendiente','Pendiente'),('aceptado','Aceptado'),('rechazado','Rechazado')), default='pendiente')
    creado = models.DateTimeField('creado', auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'documento'
        verbose_name_plural = 'documentos'
