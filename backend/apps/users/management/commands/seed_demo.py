from decimal import Decimal
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.batches.models import QR, Status, Waste
from apps.organizations.models import Organization
from apps.users.models import DriverProfile, MedicalOrganization, Recycler, User


class Command(BaseCommand):
    help = 'Seed demo data'

    @staticmethod
    def _ensure_user(
        *,
        login: str,
        password: str,
        full_name: str,
        role: str,
        organization: Organization | None = None,
        is_staff: bool = False,
        is_superuser: bool = False,
    ) -> User:
        user, _ = User.objects.get_or_create(
            login=login,
            defaults={
                'full_name': full_name,
                'role': role,
                'organization': organization,
                'is_staff': is_staff,
                'is_superuser': is_superuser,
            },
        )

        update_fields: list[str] = []
        if user.full_name != full_name:
            user.full_name = full_name
            update_fields.append('full_name')
        if user.role != role:
            user.role = role
            update_fields.append('role')
        if user.organization_id != (organization.id if organization else None):
            user.organization = organization
            update_fields.append('organization')
        if user.is_staff != is_staff:
            user.is_staff = is_staff
            update_fields.append('is_staff')
        if user.is_superuser != is_superuser:
            user.is_superuser = is_superuser
            update_fields.append('is_superuser')
        if update_fields:
            user.save(update_fields=update_fields)

        if not user.check_password(password):
            user.set_password(password)
            user.save(update_fields=['password'])

        return user

    @staticmethod
    def _ensure_organization(*, inn: str, kpp: str, name: str) -> Organization:
        organization, _ = Organization.objects.get_or_create(
            inn=inn,
            kpp=kpp,
            defaults={'name': name},
        )
        if organization.name != name:
            organization.name = name
            organization.save(update_fields=['name'])
        return organization

    def handle(self, *args, **options):
        self._ensure_user(
            login='admin@example.com',
            password='admin12345',
            full_name='Администратор',
            role='ADMIN',
            is_staff=True,
            is_superuser=True,
        )

        edu_org = self._ensure_organization(inn='1234567890', kpp='123456789', name='Клиника №1')
        proc_org = self._ensure_organization(inn='0987654321', kpp='987654321', name='Переработчик ООО')

        educator = self._ensure_user(
            login='educator@example.com',
            password='educator12345',
            full_name='Иванов Иван Иванович',
            role='RECYCLER',
            organization=edu_org,
        )
        if not educator.medical_org_id:
            profile = MedicalOrganization.objects.create(
                license_number='LIC-EDU-001',
                address='Москва, ул. Больничная, 10',
            )
            educator.medical_org = profile
            educator.save(update_fields=['medical_org'])
        else:
            profile = educator.medical_org
            update_fields: list[str] = []
            if profile.license_number != 'LIC-EDU-001':
                profile.license_number = 'LIC-EDU-001'
                update_fields.append('license_number')
            if profile.address != 'Москва, ул. Больничная, 10':
                profile.address = 'Москва, ул. Больничная, 10'
                update_fields.append('address')
            if update_fields:
                profile.save(update_fields=update_fields)

        driver = self._ensure_user(
            login='driver@example.com',
            password='driver12345',
            full_name='Петров Пётр Петрович',
            role='DRIVER',
            organization=proc_org,
        )
        if not driver.driver_profile_id:
            profile = DriverProfile.objects.create(vehicle_number='А123АА77')
            driver.driver_profile = profile
            driver.save(update_fields=['driver_profile'])
        elif driver.driver_profile.vehicle_number != 'А123АА77':
            driver.driver_profile.vehicle_number = 'А123АА77'
            driver.driver_profile.save(update_fields=['vehicle_number'])

        processor = self._ensure_user(
            login='processor@example.com',
            password='processor12345',
            full_name='Сидоров Сидор Сидорович',
            role='MEDICAL',
            organization=proc_org,
        )
        if not processor.recycler_profile_id:
            profile = Recycler.objects.create(
                license_number='LIC-PROC-001',
                facility_address='Москва, ул. Заводская, 2',
            )
            processor.recycler_profile = profile
            processor.save(update_fields=['recycler_profile'])
        else:
            profile = processor.recycler_profile
            update_fields: list[str] = []
            if profile.license_number != 'LIC-PROC-001':
                profile.license_number = 'LIC-PROC-001'
                update_fields.append('license_number')
            if profile.facility_address != 'Москва, ул. Заводская, 2':
                profile.facility_address = 'Москва, ул. Заводская, 2'
                update_fields.append('facility_address')
            if update_fields:
                profile.save(update_fields=update_fields)

        processor.recycler_profile.drivers.add(driver.driver_profile)

        waste, created = Waste.objects.get_or_create(
            medical_organization=educator.medical_org,
            waste_type='Просроченные лекарственные препараты',
            quantity=Decimal('12.50'),
            pickup_point='Москва, ул. Больничная, 10',
            delivery_point=processor.recycler_profile,
            defaults={'created_by': educator},
        )

        if created:
            Status.objects.create(waste=waste, state='CREATED', changed_by=educator)
            QR.objects.create(
                waste=waste,
                code=timezone.now().strftime('%Y%m%d%H%M%S'),
                expires_at=timezone.now() + timedelta(days=2),
                is_active=True,
                created_by=educator,
            )

        self.stdout.write(self.style.SUCCESS('Demo data seeded.'))
        self.stdout.write(
            'Users: admin@example.com/admin12345, '
            'educator@example.com/educator12345, '
            'processor@example.com/processor12345, '
            'driver@example.com/driver12345'
        )
