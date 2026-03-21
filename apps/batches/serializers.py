from rest_framework import serializers
from .models import Waste, Status, QR


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Status
        fields = ['id', 'state', 'time', 'waste']


class QRSerializer(serializers.ModelSerializer):
    class Meta:
        model  = QR
        fields = ['id', 'time', 'waste', 'code', 'is_active']


class WasteSerializer(serializers.ModelSerializer):
    statuses = StatusSerializer(many=True, read_only=True)
    qr  = QRSerializer(read_only=True)

    class Meta:
        model  = Waste
        fields = ['id', 'waste_type', 'quantity', 'medical_organization',
                  'pickup_point', 'delivery_point', 'statuses', 'qr']


class WasteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Waste
        fields = ['waste_type', 'quantity', 'medical_organization', 'pickup_point', 'delivery_point']

    def create(self, validated_data):
        waste = Waste.objects.create(**validated_data)
        Status.objects.create(waste=waste, state='CREATED')
        return waste


class StatusUpdateSerializer(serializers.Serializer):
    state = serializers.CharField(max_length=64)
