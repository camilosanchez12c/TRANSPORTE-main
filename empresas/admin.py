from django.contrib import admin
from .models import Empresa

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'nit', 'fecha_creacion', 'estado')  # usar id
    list_filter = ('estado', 'ciudad')
    search_fields = ('nombre', 'nit', 'razon_social')
