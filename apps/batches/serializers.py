from datetime import timedelta
from uuid import uuid4

from django.utils import timezone
from rest_framework import serializers

from .models import Waste, Status, QR, QRScanLog


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'state', 'time', 'waste', 'changed_by']


class QRSerializer(serializers.ModelSerializer):
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = QR
        fields = ['id', 'waste', 'code', 'expires_at', 'is_active', 'created_by', 'is_expired']


class WasteSerializer(serializers.ModelSerializer):
    statuses = StatusSerializer(many=True, read_only=True)
    qr = QRSerializer(read_only=True)

    class Meta:
        model = Waste
        fields = ['id', 'waste_type', 'quantity', 'medical_organization',
                  'pickup_point', 'delivery_point', 'statuses', 'qr', 'current_status', 'created_by']


class WasteCreateSerializer(serializers.ModelSerializer):
    qr_expires_hours = serializers.IntegerField(
        min_value=1,
        max_value=168,
        required=False,
        default=24,
        write_only=True,
    )

    class Meta:
        model = Waste
        fields = [
            'waste_type',
            'quantity',
            'medical_organization',
            'pickup_point',
            'delivery_point',
            'qr_expires_hours',
        ]

    @staticmethod
    def _generate_qr_code() -> str:
        while True:
            code = uuid4().hex[:16]
            if not QR.objects.filter(code=code).exists():
                return code

    def create(self, validated_data):
        qr_expires_hours = validated_data.pop('qr_expires_hours', 24)
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None

        waste = Waste.objects.create(created_by=user, **validated_data)
        Status.objects.create(waste=waste, state='CREATED', changed_by=user)
        QR.objects.create(
            waste=waste,
            code=self._generate_qr_code(),
            expires_at=timezone.now() + timedelta(hours=qr_expires_hours),
            is_active=True,
            created_by=user,
        )
        return waste


class StatusUpdateSerializer(serializers.Serializer):
    state = serializers.ChoiceField(choices=[choice[0] for choice in Status.STATE_CHOICES])


class QRScanSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=64)


class QRExtendSerializer(serializers.Serializer):
    hours = serializers.IntegerField(min_value=1, max_value=168)


class QRScanLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRScanLog
        fields = ['id', 'qr', 'raw_code', 'scanned_by', 'scanned_at', 'success', 'fail_reason']
