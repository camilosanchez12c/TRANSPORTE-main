from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('cliente', 'Cliente'),
        ('empresa', 'Empresa'),
        ('operador', 'Operador'),
    )
    role = models.CharField('rol', max_length=20, choices=ROLES, default='cliente')
    telefono = models.CharField('teléfono', max_length=30, blank=True, null=True)

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
