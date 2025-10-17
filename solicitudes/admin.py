from django.contrib import admin
from .models import Solicitud, Oferta, Contrato

@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ('id','cliente','origen','destino','fecha_hora','estado','creado')
    list_filter = ('estado','region')
    search_fields = ('cliente__username','origen','destino')

@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ('id','solicitud','empresa','precio','estado','creado','expira_en')
    list_filter = ('estado','empresa')
    search_fields = ('empresa__nombre','solicitud__id')

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('id','oferta','creado','firmado')
