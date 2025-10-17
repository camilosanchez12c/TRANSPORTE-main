from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Solicitud, Oferta, Contrato
from .serializers import SolicitudSerializer, OfertaSerializer, ContratoSerializer
from operaciones.models import RegistroOperacion

class SolicitudViewSet(viewsets.ModelViewSet):
    queryset = Solicitud.objects.all().order_by('-creado')
    serializer_class = SolicitudSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)
        RegistroOperacion.objects.create(
            usuario=self.request.user,
            accion='crear_solicitud',
            tipo_objeto='Solicitud',
            objeto_id=str(serializer.instance.pk),
            datos={'origen': serializer.instance.origen, 'destino': serializer.instance.destino}
        )

class OfertaViewSet(viewsets.ModelViewSet):
    queryset = Oferta.objects.all().order_by('-creado')
    serializer_class = OfertaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Si es empresa, mostrar ofertas de su empresa; admin ve todo
        user = self.request.user
        if user.role == 'empresa':
            # asumimos que el usuario de empresa tiene relación a Empresa o similar
            return Oferta.objects.filter(empresa__nombre__icontains=user.username).order_by('-creado')
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        # recibiendo solicitud por id en payload: {"solicitud": 1, "precio": ...}
        data = request.data.copy()
        # validación: si user es empresa o operador
        if request.user.role not in ('empresa', 'operador'):
            return Response({'detail': 'Solo empresas u operadores pueden crear ofertas.'}, status=status.HTTP_403_FORBIDDEN)
        # Si es operador, obtener su empresa automáticamente si no mandan empresa
        # (aquí asumimos que la relación entre usuario y empresa existe; ajusta según tu modelo)
        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        instancia = serializer.save()
        RegistroOperacion.objects.create(usuario=request.user, accion='crear_oferta', tipo_objeto='Oferta', objeto_id=str(instancia.pk), datos={'solicitud': instancia.solicitud.pk, 'precio': str(instancia.precio)})
        return Response(self.get_serializer(instancia).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def aceptar(self, request, pk=None):
        # Acción que acepta una oferta: atomic transaction -> crear contrato, actualizar estados y logs
        oferta = get_object_or_404(Oferta, pk=pk)
        # Validar estado
        if oferta.estado != 'activa':
            return Response({'detail': 'La oferta no está activa.'}, status=status.HTTP_400_BAD_REQUEST)
        # Solo el cliente dueño de la solicitud puede aceptar
        if request.user.id != oferta.solicitud.cliente_id:
            return Response({'detail': 'Solo el cliente dueño de la solicitud puede aceptar la oferta.'}, status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            contrato = Contrato.objects.create(oferta=oferta)
            oferta.estado = 'aceptada'
            oferta.save()
            solicitud = oferta.solicitud
            solicitud.estado = 'confirmado'
            solicitud.save()
            # bloquear otras ofertas
            Oferta.objects.filter(solicitud=solicitud).exclude(pk=oferta.pk).update(estado='bloqueada')
            RegistroOperacion.objects.create(usuario=request.user, accion='aceptar_oferta', tipo_objeto='Oferta', objeto_id=str(oferta.pk), datos={'contrato': contrato.pk})
        return Response({'contrato_id': contrato.pk, 'solicitud_estado': solicitud.estado}, status=status.HTTP_200_OK)
