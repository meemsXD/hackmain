from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization, EducatorProfile, ProcessorProfile
from apps.batches.models import WasteBatch, BatchStatus, QRToken
import secrets

User = get_user_model()

class Command(BaseCommand):
    help = 'Создать демо-данные'

    def handle(self, *args, **kwargs):
        edu_org, _ = Organization.objects.get_or_create(inn='7700000001', kpp='770001001', defaults={'name': 'Клиника Демо'})
        proc_org, _ = Organization.objects.get_or_create(inn='7700000002', kpp='770002002', defaults={'name': 'Переработчик Демо'})
        EducatorProfile.objects.get_or_create(organization=edu_org, defaults={'license_number': 'LIC-EDU-001', 'pickup_address': 'Москва, ул. Больничная, 10'})
        ProcessorProfile.objects.get_or_create(organization=proc_org, defaults={'license_number': 'LIC-PROC-001', 'facility_address': 'Москва, ул. Заводская, 2'})

        admin, _ = User.objects.get_or_create(email='admin@example.com', defaults={'full_name': 'Администратор', 'role': 'ADMIN', 'is_staff': True, 'is_superuser': True})
        if not admin.check_password('admin12345'):
            admin.set_password('admin12345'); admin.save()

        educator, _ = User.objects.get_or_create(email='educator@example.com', defaults={'full_name': 'Образователь Демо', 'role': 'EDUCATOR', 'organization': edu_org})
        if not educator.check_password('educator12345'):
            educator.set_password('educator12345'); educator.save()

        processor, _ = User.objects.get_or_create(email='processor@example.com', defaults={'full_name': 'Переработчик Демо', 'role': 'PROCESSOR', 'organization': proc_org})
        if not processor.check_password('processor12345'):
            processor.set_password('processor12345'); processor.save()

        driver, _ = User.objects.get_or_create(email='driver@example.com', defaults={'full_name': 'Водитель Демо', 'role': 'DRIVER', 'organization': proc_org})
        if not driver.check_password('driver12345'):
            driver.set_password('driver12345'); driver.save()
        from apps.users.models import DriverProfile
        DriverProfile.objects.get_or_create(user=driver, defaults={'vehicle_number': 'А123АА77'})

        batch1, created = WasteBatch.objects.get_or_create(
            educator=edu_org, waste_type='medicines',
            defaults={'quantity': 12.5, 'unit': 'kg', 'pickup_address': 'Москва, ул. Больничная, 10', 'delivery_address': 'Москва, ул. Заводская, 2', 'status': 'CREATED'}
        )
        if created:
            BatchStatus.objects.create(batch=batch1, status='CREATED')
            token = QRToken.objects.create(batch=batch1, code=secrets.token_urlsafe(16), expires_at=timezone.now() + timedelta(days=2), is_active=True)
            self.stdout.write(self.style.SUCCESS(f'Партия 1: QR={token.code}'))

        batch2, created = WasteBatch.objects.get_or_create(
            educator=edu_org, waste_type='disinfectants',
            defaults={'quantity': 7.25, 'unit': 'l', 'pickup_address': 'Москва, ул. Больничная, 10', 'delivery_address': 'Москва, ул. Заводская, 2', 'status': 'IN_TRANSIT'}
        )
        if created:
            BatchStatus.objects.create(batch=batch2, status='CREATED')
            BatchStatus.objects.create(batch=batch2, status='IN_TRANSIT')
            self.stdout.write(self.style.SUCCESS('Партия 2: в пути'))

        self.stdout.write(self.style.SUCCESS('Демо-данные созданы.'))
