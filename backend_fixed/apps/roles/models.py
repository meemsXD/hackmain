from django.db import models
from apps.common.models import BaseModel
from apps.common.enums import RoleChoices, RequestStatusChoices

class UserRole(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='user_roles')
    role = models.CharField(max_length=32, choices=RoleChoices.choices)
    granted_by = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='granted_roles')
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'role')

    def __str__(self):
        return f'{self.user.email}: {self.role}'

class RoleRequest(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='role_requests')
    organization = models.ForeignKey('organizations.Organization', null=True, blank=True, on_delete=models.SET_NULL, related_name='role_requests')
    role = models.CharField(max_length=32, choices=RoleChoices.choices)
    status = models.CharField(max_length=16, choices=RequestStatusChoices.choices, default=RequestStatusChoices.PENDING)
    payload = models.JSONField(default=dict, blank=True)
    comment = models.TextField(blank=True)
    reviewed_by = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_role_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.user.email}: {self.role} ({self.status})'
