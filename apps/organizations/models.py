from django.db import models
from apps.common.models import BaseModel
from apps.common.enums import OrgStatusChoices

class Organization(BaseModel):
    name = models.CharField(max_length=255)
    inn = models.CharField(max_length=12)
    kpp = models.CharField(max_length=9)
    legal_address = models.CharField(max_length=500)
    status = models.CharField(max_length=20, choices=OrgStatusChoices.choices, default=OrgStatusChoices.PENDING)

    class Meta:
        unique_together = ('inn', 'kpp')
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.inn})'

class EducatorOrgProfile(BaseModel):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='educator_profile')
    waste_license_number = models.CharField(max_length=128)
    default_pickup_address = models.CharField(max_length=500)

    def __str__(self):
        return f'Образователь: {self.organization.name}'

class ProcessorOrgProfile(BaseModel):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='processor_profile')
    recycling_license_number = models.CharField(max_length=128)
    facility_address = models.CharField(max_length=500)

    def __str__(self):
        return f'Переработчик: {self.organization.name}'
