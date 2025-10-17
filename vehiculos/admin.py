from django.contrib import admin
from .models import Vehiculo

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('placa','empresa','tipo','capacidad','soat_vencimiento','tecnomecanica_vencimiento','creado')
    search_fields = ('placa','empresa__nombre')
    list_filter = ('tipo','empresa')
