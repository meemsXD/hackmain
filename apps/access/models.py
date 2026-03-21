from django.db import models
from apps.common.models import BaseModel

class QRAccessToken(BaseModel):
    batch = models.OneToOneField('batches.WasteBatch', on_delete=models.CASCADE, related_name='access_token')
    token_hash = models.CharField(max_length=255)
    manual_code = models.CharField(max_length=32, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='created_access_tokens')

    def __str__(self):
        return f'{self.batch.batch_number} ({self.manual_code})'

class DriverBatchAccessGrant(BaseModel):
    batch = models.ForeignKey('batches.WasteBatch', on_delete=models.CASCADE, related_name='driver_grants')
    driver = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='driver_batch_grants')
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        unique_together = ('batch', 'driver')

class TokenAccessAttempt(BaseModel):
    batch = models.ForeignKey('batches.WasteBatch', null=True, blank=True, on_delete=models.SET_NULL, related_name='access_attempts')
    user = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='token_access_attempts')
    token_fragment = models.CharField(max_length=24, blank=True)
    manual_code = models.CharField(max_length=32, blank=True)
    success = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=64, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ('-created_at',)
