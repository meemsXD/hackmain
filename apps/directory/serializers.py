from rest_framework import serializers
from .models import WasteType

class WasteTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WasteType
        fields = ['id', 'code', 'name', 'is_active']
