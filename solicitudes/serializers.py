from rest_framework import serializers
from .models import Solicitud, Oferta, Contrato
from vehiculos.models import Vehiculo
from operadores.models import Operador

class SolicitudSerializer(serializers.ModelSerializer):
    cliente = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Solicitud
        fields = ['id','cliente','origen','destino','fecha_hora','pasajeros','region','descripcion','estado','creado']
        read_only_fields = ['id','cliente','estado','creado']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['cliente'] = user
        return super().create(validated_data)

class OfertaSerializer(serializers.ModelSerializer):
    empresa = serializers.StringRelatedField(read_only=True)
    operador = serializers.PrimaryKeyRelatedField(queryset=Operador.objects.all(), required=False, allow_null=True)
    vehiculo = serializers.PrimaryKeyRelatedField(queryset=Vehiculo.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Oferta
        fields = ['id','solicitud','empresa','operador','vehiculo','precio','mensaje','segundos_validez','expira_en','estado','creado']
        read_only_fields = ['id','empresa','expira_en','estado','creado']

    def validate(self, data):
        request_obj = data.get('solicitud') or self.context.get('solicitud_obj')
        user = self.context['request'].user

        # RB-01: Un cliente no puede crear oferta sobre su propia solicitud
        if hasattr(request_obj, 'cliente') and request_obj.cliente_id == getattr(user, 'id', None):
            raise serializers.ValidationError("Un cliente no puede crear oferta sobre su propia solicitud.")

        # Validar vehículo disponible
        vehiculo = data.get('vehiculo')
        if vehiculo and not vehiculo.disponible:
            raise serializers.ValidationError("El vehículo seleccionado tiene documentos vencidos o no está disponible.")

        # Validar operador autorizado
        operador = data.get('operador')
        if operador and not operador.autorizado:
            raise serializers.ValidationError("El operador no está autorizado (licencia vencida).")

        return data

    def create(self, validated_data):
        # Si la empresa viene del usuario (usuario role empresa), lo asignamos
        user = self.context['request'].user
        empresa_obj = getattr(user, 'empresa', None)
        if user.role == 'empresa':
            validated_data['empresa'] = empresa_obj
        # calcular expira_en en save del modelo ya lo hace, pero aseguramos el campo
        instancia = super().create(validated_data)
        return instancia

class ContratoSerializer(serializers.ModelSerializer):
    oferta = OfertaSerializer(read_only=True)

    class Meta:
        model = Contrato
        fields = ['id','oferta','creado','firmado']
        read_only_fields = ['id','oferta','creado','firmado']
