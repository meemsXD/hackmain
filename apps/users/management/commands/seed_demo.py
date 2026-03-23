from decimal import Decimal
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.batches.models import QR, Status, Waste
from apps.organizations.models import Organization
from apps.users.models import User, DriverProfile, MedicalOrganization, Recycler


class Command(BaseCommand):
    help = 'Seed demo data'

    def handle(self, *args, **options):
        admin_user, created = User.objects.get_or_create(
            login='admin@example.com',
            defaults={
                'full_name': 'Администратор',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if created:
            admin_user.set_password('admin12345')
            admin_user.save(update_fields=['password'])
        else:
            update_fields = []
            if admin_user.role != 'ADMIN':
                admin_user.role = 'ADMIN'
                update_fields.append('role')
            if not admin_user.is_staff:
                admin_user.is_staff = True
                update_fields.append('is_staff')
            if not admin_user.is_superuser:
                admin_user.is_superuser = True
                update_fields.append('is_superuser')
            if update_fields:
                admin_user.save(update_fields=update_fields)

        edu_org, _ = Organization.objects.get_or_create(
            inn='1234567890',
            kpp='123456789',
            defaults={'name': 'Клиника №1'},
        )
        proc_org, _ = Organization.objects.get_or_create(
            inn='0987654321',
            kpp='987654321',
            defaults={'name': 'Переработчик ООО'},
        )

        edu_user, created = User.objects.get_or_create(login='educator1', defaults={
            'full_name': 'Иванов Иван Иванович', 'role': 'RECYCLER', 'organization': edu_org,
        })
        if created:
            edu_user.set_password('pass123')
            edu_user.save(update_fields=['password'])
        if not edu_user.medical_org_id:
            edu_profile = MedicalOrganization.objects.create(
                license_number='LIC-EDU-001',
                address='Москва, ул. Больничная, 10',
            )
            edu_user.medical_org = edu_profile
            edu_user.save(update_fields=['medical_org'])

        driver, created = User.objects.get_or_create(login='driver1', defaults={
            'full_name': 'Петров Пётр Петрович', 'role': 'DRIVER', 'organization': proc_org,
        })
        if created:
            driver.set_password('pass123')
            driver.save(update_fields=['password'])
        if not driver.driver_profile_id:
            driver_profile = DriverProfile.objects.create(vehicle_number='А123АА77')
            driver.driver_profile = driver_profile
            driver.save(update_fields=['driver_profile'])

        proc, created = User.objects.get_or_create(login='processor1', defaults={
            'full_name': 'Сидоров Сидор Сидорович', 'role': 'MEDICAL', 'organization': proc_org,
        })
        if created:
            proc.set_password('pass123')
            proc.save(update_fields=['password'])
        if not proc.recycler_profile_id:
            recycler_profile = Recycler.objects.create(
                license_number='LIC-PROC-001',
                facility_address='Москва, ул. Заводская, 2',
            )
            proc.recycler_profile = recycler_profile
            proc.save(update_fields=['recycler_profile'])

        proc.recycler_profile.drivers.add(driver.driver_profile)

        waste1, created = Waste.objects.get_or_create(
            medical_organization=edu_user.medical_org,
            waste_type='Просроченные лекарственные препараты',
            quantity=Decimal('12.50'),
            pickup_point='Москва, ул. Больничная, 10',
            delivery_point=proc.recycler_profile,
            defaults={'created_by': edu_user},
        )

        if created:
            Status.objects.create(waste=waste1, state='CREATED', changed_by=edu_user)
            QR.objects.create(
                waste=waste1,
                code=timezone.now().strftime('%Y%m%d%H%M%S'),
                expires_at=timezone.now() + timedelta(days=2),
                is_active=True,
                created_by=edu_user,
            )

        self.stdout.write(self.style.SUCCESS('Demo data seeded.'))
