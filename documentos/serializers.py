from rest_framework import serializers
from .models import Documento

MAX_SIZE = 10 * 1024 * 1024  # 10 MB

class DocumentoSerializer(serializers.ModelSerializer):
    archivo = serializers.FileField(write_only=True)

    class Meta:
        model = Documento
        fields = ['id', 'archivo', 'nombre', 'tamano', 'subido_por', 'estado', 'creado']
        read_only_fields = ['id', 'nombre', 'tamano', 'subido_por', 'estado', 'creado']

    def create(self, validated_data):
        f = validated_data.pop('archivo')
        if f.size > MAX_SIZE:
            raise serializers.ValidationError("El archivo supera 10 MB.")
        usuario = self.context['request'].user
        doc = Documento.objects.create(
            archivo=f,
            nombre=f.name,
            tamano=f.size,
            subido_por=usuario,
            **validated_data
        )
        return doc
