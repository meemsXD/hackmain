import uuid
from django.db import models


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    inn = models.CharField(max_length=12)
    kpp = models.CharField(max_length=9)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'organization'
        unique_together = ('inn', 'kpp')

    def __str__(self):
        return f'{self.name} ({self.inn})'


class EducatorProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='educator_profile')
    license_number = models.CharField(max_length=128, verbose_name='Номер лицензии')
    pickup_address = models.CharField(max_length=500, verbose_name='Адрес вывоза')

    class Meta:
        db_table = 'educator_profile'

    def __str__(self):
        return f'Образователь: {self.organization.name}'


class ProcessorProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='processor_profile')
    license_number = models.CharField(max_length=128, verbose_name='Номер лицензии')
    facility_address = models.CharField(max_length=500, verbose_name='Адрес площадки')
    drivers = models.ManyToManyField('users.User', blank=True, related_name='processor_orgs', verbose_name='Водители')

    class Meta:
        db_table = 'processor_profile'

    def __str__(self):
        return f'Переработчик: {self.organization.name}'
