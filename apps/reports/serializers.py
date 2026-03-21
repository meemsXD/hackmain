from rest_framework import serializers
from apps.batches.serializers import WasteBatchSerializer
from apps.audits.models import AuditEvent

class AuditEventSerializer(serializers.ModelSerializer):
    actor_email = serializers.CharField(source='actor_user.email', read_only=True)
    class Meta:
        model = AuditEvent
        fields = ['id', 'actor_email', 'action', 'object_type', 'object_id', 'before_data', 'after_data', 'created_at']
