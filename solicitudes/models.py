from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Solicitud(models.Model):
    ESTADOS = (
        ('pendiente','Pendiente'),
        ('confirmado','Confirmado'),
        ('en_curso','En curso'),
        ('finalizado','Finalizado'),
        ('cancelado','Cancelado'),
    )
    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solicitudes')
    origen = models.CharField('origen', max_length=255)
    destino = models.CharField('destino', max_length=255)
    fecha_hora = models.DateTimeField('fecha y hora')
    pasajeros = models.PositiveIntegerField('pasajeros')
    region = models.CharField('región', max_length=100)
    descripcion = models.TextField('descripción', blank=True)
    estado = models.CharField('estado', max_length=30, choices=ESTADOS, default='pendiente')
    creado = models.DateTimeField('creado', auto_now_add=True)

    def __str__(self):
        return f"Solicitud #{self.pk} - {self.origen} → {self.destino}"

    class Meta:
        verbose_name = 'solicitud'
        verbose_name_plural = 'solicitudes'

class Oferta(models.Model):
    ESTADOS_OFERTA = (('activa','Activa'),('expirada','Expirada'),('aceptada','Aceptada'),('bloqueada','Bloqueada'))
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='ofertas')
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE)
    operador = models.ForeignKey('operadores.Operador', on_delete=models.SET_NULL, null=True, blank=True)
    vehiculo = models.ForeignKey('vehiculos.Vehiculo', on_delete=models.SET_NULL, null=True, blank=True)
    precio = models.DecimalField('precio', max_digits=12, decimal_places=2)
    mensaje = models.TextField('mensaje', blank=True)
    segundos_validez = models.IntegerField('segundos validez', default=86400)
    creado = models.DateTimeField('creado', auto_now_add=True)
    expira_en = models.DateTimeField('expira en', null=True, blank=True)
    estado = models.CharField('estado', max_length=20, choices=ESTADOS_OFERTA, default='activa')

    def save(self, *args, **kwargs):
        if not self.expira_en:
            self.expira_en = timezone.now() + timedelta(seconds=self.segundos_validez)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Oferta #{self.pk} - {self.empresa.nombre} - {self.precio}"

    class Meta:
        verbose_name = 'oferta'
        verbose_name_plural = 'ofertas'

class Contrato(models.Model):
    oferta = models.OneToOneField(Oferta, on_delete=models.CASCADE, related_name='contrato')
    creado = models.DateTimeField('creado', auto_now_add=True)
    firmado = models.BooleanField('firmado', default=False)

    def __str__(self):
        return f"Contrato #{self.pk} - Oferta {self.oferta.pk}"

    class Meta:
        verbose_name = 'contrato'
        verbose_name_plural = 'contratos'
