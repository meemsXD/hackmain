from rest_framework import serializers
from apps.common.enums import BatchStatusChoices, UnitChoices
from apps.organizations.models import Organization
from apps.directory.models import WasteType
from apps.access.models import QRAccessToken, TokenAccessAttempt
from apps.chat.models import ChatThread
from .models import WasteBatch, BatchStatusHistory

class BatchStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.full_name', read_only=True)
    class Meta:
        model = BatchStatusHistory
        fields = ['id', 'from_status', 'to_status', 'changed_by_name', 'reason', 'created_at']

class WasteBatchSerializer(serializers.ModelSerializer):
    waste_type_name = serializers.CharField(source='waste_type.name', read_only=True)
    creator_organization_name = serializers.CharField(source='creator_org.name', read_only=True)
    processor_organization_name = serializers.CharField(source='processor_org.name', read_only=True)
    current_driver_name = serializers.CharField(source='current_driver.full_name', read_only=True)
    token_expires_at = serializers.SerializerMethodField()
    manual_code = serializers.SerializerMethodField()
    raw_token = serializers.SerializerMethodField()

    class Meta:
        model = WasteBatch
        fields = [
            'id', 'batch_number', 'waste_type', 'waste_type_name', 'quantity', 'unit', 'creator_org',
            'creator_organization_name', 'pickup_address', 'processor_org', 'processor_organization_name',
            'delivery_address_snapshot', 'current_driver', 'current_driver_name', 'status', 'comment',
            'created_at', 'picked_up_at', 'delivered_at', 'accepted_at', 'cancelled_at', 'token_expires_at', 'manual_code', 'raw_token'
        ]
        read_only_fields = ['id', 'batch_number', 'creator_org', 'status', 'created_at', 'picked_up_at', 'delivered_at', 'accepted_at', 'cancelled_at']

    def get_token_expires_at(self, obj):
        token = getattr(obj, 'access_token', None)
        return token.expires_at if token else None

    def get_manual_code(self, obj):
        token = getattr(obj, 'access_token', None)
        return token.manual_code if token else None

    def get_raw_token(self, obj):
        token = getattr(obj, 'access_token', None)
        return getattr(obj, 'raw_token', None) or getattr(token, 'raw_token', None)

class EducatorBatchCreateSerializer(serializers.Serializer):
    waste_type = serializers.PrimaryKeyRelatedField(queryset=WasteType.objects.filter(is_active=True))
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    unit = serializers.ChoiceField(choices=UnitChoices.choices)
    pickup_address = serializers.CharField(max_length=500)
    processor_org = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())
    comment = serializers.CharField(required=False, allow_blank=True)
    token_expires_at = serializers.DateTimeField()
    signature_token = serializers.CharField(write_only=True)

class EducatorBatchUpdateSerializer(serializers.ModelSerializer):
    token_expires_at = serializers.DateTimeField(required=False, write_only=True)
    signature_token = serializers.CharField(write_only=True)

    class Meta:
        model = WasteBatch
        fields = ['waste_type', 'quantity', 'unit', 'pickup_address', 'processor_org', 'comment', 'current_driver', 'token_expires_at', 'signature_token']

class ExtendTokenSerializer(serializers.Serializer):
    expires_at = serializers.DateTimeField()
    signature_token = serializers.CharField()

class BlockedAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenAccessAttempt
        fields = ['id', 'success', 'failure_reason', 'ip', 'user_agent', 'created_at']
