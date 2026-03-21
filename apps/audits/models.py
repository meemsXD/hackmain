from django.db import models
from apps.common.models import BaseModel

class AuditEvent(BaseModel):
    actor_user = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='audit_events')
    actor_org = models.ForeignKey('organizations.Organization', null=True, blank=True, on_delete=models.SET_NULL, related_name='audit_events')
    action = models.CharField(max_length=128)
    object_type = models.CharField(max_length=128)
    object_id = models.CharField(max_length=128)
    before_data = models.JSONField(null=True, blank=True)
    after_data = models.JSONField(null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.action} {self.object_type}:{self.object_id}'
