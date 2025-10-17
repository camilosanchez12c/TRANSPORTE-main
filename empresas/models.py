from django.db import models

class Empresa(models.Model):
    nit = models.CharField('NIT', max_length=50, unique=True)
    nombre = models.CharField('nombre', max_length=200)
    representante = models.CharField('representante', max_length=200)
    estado = models.CharField('estado', max_length=20, choices=(('pendiente','Pendiente'),('validada','Validada'),('rechazada','Rechazada')), default='pendiente')
    creado = models.DateTimeField('creado', auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'empresa'
        verbose_name_plural = 'empresas'
