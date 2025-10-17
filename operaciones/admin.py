from django.contrib import admin
from .models import RegistroOperacion

@admin.register(RegistroOperacion)
class RegistroOperacionAdmin(admin.ModelAdmin):
    list_display = ('accion','usuario','tipo_objeto','objeto_id','creado')
    list_filter = ('accion','tipo_objeto')
    search_fields = ('usuario__username','objeto_id','accion')
