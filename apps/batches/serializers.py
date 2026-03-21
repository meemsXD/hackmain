import secrets
import string
from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers
from .models import WasteBatch, BatchStatus, QRToken


class BatchStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchStatus
        fields = ['id', 'status', 'changed_at']


class QRTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRToken
        fields = ['id', 'code', 'expires_at', 'is_active']


class WasteBatchSerializer(serializers.ModelSerializer):
    statuses = BatchStatusSerializer(many=True, read_only=True)
    qr_token = QRTokenSerializer(read_only=True)
    educator_name = serializers.CharField(source='educator.name', read_only=True)

    class Meta:
        model = WasteBatch
        fields = ['id', 'waste_type', 'quantity', 'unit', 'educator', 'educator_name',
                  'pickup_address', 'delivery_address', 'created_at', 'statuses', 'qr_token']
        read_only_fields = ['id', 'created_at']


class WasteBatchCreateSerializer(serializers.ModelSerializer):
    token_expires_hours = serializers.IntegerField(write_only=True, default=24, min_value=1, max_value=168)

    class Meta:
        model = WasteBatch
        fields = ['waste_type', 'quantity', 'unit', 'educator', 'pickup_address', 'delivery_address', 'token_expires_hours']

    def create(self, validated_data):
        from apps.audit.models import log
        hours = validated_data.pop('token_expires_hours', 24)
        batch = WasteBatch.objects.create(**validated_data)
        BatchStatus.objects.create(batch=batch, status='CREATED')
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        code = f'{code[:3]}-{code[3:6]}-{code[6:]}'
        QRToken.objects.create(
            batch=batch,
            code=code,
            expires_at=timezone.now() + timedelta(hours=hours),
        )
        request = self.context.get('request')
        if request:
            log(request.user, 'batch_created', 'waste_batch', str(batch.id), after={'waste_type': batch.waste_type})
        return batch


class BatchStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['IN_TRANSIT', 'ACCEPTED', 'CANCELLED'])
