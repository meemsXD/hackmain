import secrets
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.users.models import User, DriverProfile, MedicalOrganization, Recycler
from apps.organizations.models import Organization
from apps.batches.models import Waste, Status, QR


class Command(BaseCommand):
    help = 'Seed demo data'

    def handle(self, *args, **options):
        edu_org,  _ = Organization.objects.get_or_create(inn='1234567890', kpp='123456789', defaults={'name': 'Клиника №1'})
        proc_org, _ = Organization.objects.get_or_create(inn='0987654321', kpp='987654321', defaults={'name': 'Переработчик ООО'})

        edu_user, created = User.objects.get_or_create(login='educator1', defaults={
            'full_name': 'Иванов Иван Иванович', 'role': 'EDUCATOR', 'organization': edu_org,
        })
        if created:
            edu_user.set_password('pass123')
            edu_user.save()
            MedicalOrganization.objects.create(user=edu_user, license_number='LIC-EDU-001', address='Москва, ул. Больничная, 10')

        driver, created = User.objects.get_or_create(login='driver1', defaults={
            'full_name': 'Петров Пётр Петрович', 'role': 'DRIVER', 'organization': proc_org,
        })
        if created:
            driver.set_password('pass123')
            driver.save()
            DriverProfile.objects.create(user=driver, vehicle_number='А123АА77')

        proc, created = User.objects.get_or_create(login='processor1', defaults={
            'full_name': 'Сидоров Сидор Сидорович', 'role': 'PROCESSOR', 'organization': proc_org,
        })
        if created:
            proc.set_password('pass123')
            proc.save()
            pp = Recycler.objects.create(user=proc, license_number='LIC-PROC-001', facility_address='Москва, ул. Заводская, 2')
            pp.drivers.add(driver)

        waste1, created = Waste.objects.get_or_create(
            educator=edu_user, waste_type='medicines',
            defaults={'quantity': 12.5, 'pickup_point': 'Москва, ул. Больничная, 10', 'delivery_point': 'Москва, ул. Заводская, 2'}
        )
        if created:
            Status.objects.create(waste=waste1, state='CREATED')
            QR.objects.create(waste=waste1, code=secrets.token_urlsafe(16),
                              time=timezone.now() + timedelta(days=2), is_active=True)

        self.stdout.write(self.style.SUCCESS('Demo data seeded.'))
