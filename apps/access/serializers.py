from rest_framework import serializers
from apps.users.models import DriverProfile, User
from apps.batches.serializers import WasteBatchSerializer

class DriverAccessOpenSerializer(serializers.Serializer):
    token = serializers.CharField(required=False)
    manual_code = serializers.CharField(required=False)

    def validate(self, attrs):
        if not attrs.get('token') and not attrs.get('manual_code'):
            raise serializers.ValidationError('Нужно передать token или manual_code')
        return attrs

class DriverListSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(source='driver_profile.vehicle_number', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'vehicle_number', 'is_active']
