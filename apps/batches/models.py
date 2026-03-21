from django.db import models
from apps.common.models import BaseModel
from apps.common.enums import UnitChoices, BatchStatusChoices

class WasteBatch(BaseModel):
    batch_number = models.CharField(max_length=64, unique=True)
    waste_type = models.ForeignKey('directory.WasteType', on_delete=models.PROTECT, related_name='batches')
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit = models.CharField(max_length=8, choices=UnitChoices.choices)
    creator_org = models.ForeignKey('organizations.Organization', on_delete=models.PROTECT, related_name='created_batches')
    created_by = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='created_batches')
    pickup_address = models.CharField(max_length=500)
    processor_org = models.ForeignKey('organizations.Organization', on_delete=models.PROTECT, related_name='incoming_batches')
    delivery_address_snapshot = models.CharField(max_length=500)
    current_driver = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_batches')
    status = models.CharField(max_length=16, choices=BatchStatusChoices.choices, default=BatchStatusChoices.CREATED)
    comment = models.TextField(blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.batch_number

class BatchStatusHistory(BaseModel):
    batch = models.ForeignKey(WasteBatch, on_delete=models.CASCADE, related_name='status_history')
    from_status = models.CharField(max_length=16, blank=True)
    to_status = models.CharField(max_length=16)
    changed_by = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='batch_status_changes')
    signature_user = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='signed_status_changes')
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f'{self.batch.batch_number}: {self.from_status}->{self.to_status}'
