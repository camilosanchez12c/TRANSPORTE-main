from django.contrib import admin
from .models import Operador

@admin.register(Operador)
class OperadorAdmin(admin.ModelAdmin):
    list_display = ('user','empresa','numero_licencia','vencimiento_licencia','autorizado')
    list_filter = ('autorizado','empresa')
    search_fields = ('user__username','numero_licencia')
