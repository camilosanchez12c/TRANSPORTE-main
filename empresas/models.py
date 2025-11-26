from django.db import models
from usuarios.models import Usuario  # tu modelo existente

class Empresa(models.Model):
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    nit = models.CharField(max_length=50, unique=True)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    actividad_economica = models.CharField(max_length=255, blank=True, null=True)
    tamano_flota = models.IntegerField(blank=True, null=True)
    sitio_web = models.CharField(max_length=255, blank=True, null=True)
    region_operacion = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=20, default='pendiente')

    # Archivos
    rut = models.FileField(upload_to='documentos/', blank=True, null=True)
    camara_comercio = models.FileField(upload_to='documentos/', blank=True, null=True)
    licencia_operacion = models.FileField(upload_to='documentos/', blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
