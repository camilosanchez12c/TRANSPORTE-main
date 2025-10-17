from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Documento
from .serializers import DocumentoSerializer
from operaciones.models import RegistroOperacion

class DocumentoViewSet(viewsets.ModelViewSet):
    queryset = Documento.objects.all().order_by('-creado')
    serializer_class = DocumentoSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        doc = serializer.save()
        RegistroOperacion.objects.create(usuario=request.user, accion='subir_documento', tipo_objeto='Documento', objeto_id=str(doc.pk), datos={'nombre': doc.nombre})
        return Response(self.get_serializer(doc).data, status=status.HTTP_201_CREATED)
