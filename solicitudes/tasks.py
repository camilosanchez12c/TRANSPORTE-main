from celery import shared_task
from django.utils import timezone
from .models import Oferta
from operaciones.models import RegistroOperacion

@shared_task
def expire_offers_task():
    now = timezone.now()
    expiradas = Oferta.objects.filter(estado='activa', expira_en__lte=now)
    for o in expiradas:
        o.estado = 'expirada'
        o.save()
        RegistroOperacion.objects.create(usuario=None, accion='oferta_expirada', tipo_objeto='Oferta', objeto_id=str(o.pk), datos={'solicitud': o.solicitud.pk})
