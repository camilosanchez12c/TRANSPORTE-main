from django.contrib import admin
from .models import Documento

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre','subido_por','estado','creado')
    list_filter = ('estado',)
    search_fields = ('nombre','subido_por__username')
