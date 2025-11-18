from django.db import models

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    rol_id = models.IntegerField()  
    is_active = models.BooleanField(default=True)
    token_recuperacion = models.CharField(max_length=255, null=True, blank=True)
    fecha_token = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return self.email
