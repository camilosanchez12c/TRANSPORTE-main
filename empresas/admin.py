from django.contrib import admin
from .models import Empresa

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre','nit','estado','creado')
    list_filter = ('estado',)
    search_fields = ('nombre','nit','representante')
