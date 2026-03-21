from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.login', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_email', 'action', 'object_type', 'object_id', 'before', 'after', 'created_at']
