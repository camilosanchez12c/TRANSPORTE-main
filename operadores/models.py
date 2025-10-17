from django.db import models
from django.conf import settings
from django.utils import timezone

class Operador(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='operadores')
    numero_licencia = models.CharField('número de licencia', max_length=100)
    categoria_licencia = models.CharField('categoría licencia', max_length=50)
    vencimiento_licencia = models.DateField('vencimiento licencia')
    autorizado = models.BooleanField('autorizado', default=True)

    def save(self, *args, **kwargs):
        self.autorizado = self.vencimiento_licencia >= timezone.now().date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.empresa.nombre}"

    class Meta:
        verbose_name = 'operador'
        verbose_name_plural = 'operadores'
