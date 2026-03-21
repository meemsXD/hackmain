from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from apps.common.enums import RoleChoices, OrgStatusChoices, BatchStatusChoices
from apps.organizations.models import Organization, EducatorOrgProfile, ProcessorOrgProfile
from apps.roles.models import UserRole
from apps.directory.models import WasteType
from apps.users.models import DriverProfile
from apps.batches.models import WasteBatch, BatchStatusHistory
from apps.access.services import ensure_batch_token, log_access_attempt
from apps.chat.services import ensure_chat_thread, send_message, create_system_message

User = get_user_model()

class Command(BaseCommand):
    help = 'Create demo data for local development'

    def handle(self, *args, **kwargs):
        admin, _ = User.objects.get_or_create(email='admin@example.com', defaults={'full_name': 'Platform Admin', 'is_staff': True, 'is_superuser': True})
        if not admin.check_password('admin12345'):
            admin.set_password('admin12345')
            admin.save()

        inspector, _ = User.objects.get_or_create(email='inspector@example.com', defaults={'full_name': 'System Inspector'})
        if not inspector.password:
            inspector.set_password('inspector12345')
            inspector.save()
        UserRole.objects.get_or_create(user=inspector, role=RoleChoices.INSPECTOR)

        edu_org, _ = Organization.objects.get_or_create(inn='7700000001', kpp='770001001', defaults={'name': 'Demo Clinic', 'legal_address': 'Москва, ул. Тестовая, 1', 'status': OrgStatusChoices.ACTIVE})
        proc_org, _ = Organization.objects.get_or_create(inn='7700000002', kpp='770002002', defaults={'name': 'Demo Recycler', 'legal_address': 'Москва, ул. Заводская, 2', 'status': OrgStatusChoices.ACTIVE})
        edu_org.status = OrgStatusChoices.ACTIVE; edu_org.save()
        proc_org.status = OrgStatusChoices.ACTIVE; proc_org.save()
        EducatorOrgProfile.objects.get_or_create(organization=edu_org, defaults={'waste_license_number': 'LIC-EDU-001', 'default_pickup_address': 'Москва, ул. Больничная, 10'})
        ProcessorOrgProfile.objects.get_or_create(organization=proc_org, defaults={'recycling_license_number': 'LIC-PROC-001', 'facility_address': 'Москва, ул. Заводская, 2'})

        educator, _ = User.objects.get_or_create(email='educator@example.com', defaults={'full_name': 'Demo Educator', 'organization': edu_org})
        if not educator.password:
            educator.set_password('educator12345'); educator.save()
        educator.organization = edu_org; educator.save()
        UserRole.objects.get_or_create(user=educator, role=RoleChoices.EDUCATOR)
        if not educator.signature_token_hash:
            educator.signature_token_hash = make_password('educator-sign')
            educator.save(update_fields=['signature_token_hash'])

        processor, _ = User.objects.get_or_create(email='processor@example.com', defaults={'full_name': 'Demo Processor', 'organization': proc_org})
        if not processor.password:
            processor.set_password('processor12345'); processor.save()
        processor.organization = proc_org; processor.save()
        UserRole.objects.get_or_create(user=processor, role=RoleChoices.PROCESSOR)
        if not processor.signature_token_hash:
            processor.signature_token_hash = make_password('processor-sign')
            processor.save(update_fields=['signature_token_hash'])

        driver, _ = User.objects.get_or_create(email='driver@example.com', defaults={'full_name': 'Demo Driver', 'organization': proc_org})
        if not driver.password:
            driver.set_password('driver12345'); driver.save()
        driver.organization = proc_org; driver.save()
        UserRole.objects.get_or_create(user=driver, role=RoleChoices.DRIVER)
        DriverProfile.objects.get_or_create(user=driver, defaults={'vehicle_number': 'А123АА77'})
        if not driver.signature_token_hash:
            driver.signature_token_hash = make_password('driver-sign')
            driver.save(update_fields=['signature_token_hash'])

        wt1, _ = WasteType.objects.get_or_create(code='medicines', defaults={'name': 'Лекарственные препараты'})
        wt2, _ = WasteType.objects.get_or_create(code='disinfectants', defaults={'name': 'Дезинфектанты'})
        WasteType.objects.get_or_create(code='mercury', defaults={'name': 'Ртутьсодержащие'})
        WasteType.objects.get_or_create(code='cytostatics', defaults={'name': 'Цитостатики'})
        WasteType.objects.get_or_create(code='other', defaults={'name': 'Иное'})

        created, _ = WasteBatch.objects.get_or_create(
            batch_number='WG-DEMO-00001',
            defaults={
                'waste_type': wt1, 'quantity': 12.5, 'unit': 'kg', 'creator_org': edu_org, 'created_by': educator,
                'pickup_address': 'Москва, ул. Больничная, 10', 'processor_org': proc_org, 'delivery_address_snapshot': 'Москва, ул. Заводская, 2',
                'comment': 'Demo created batch', 'status': BatchStatusChoices.CREATED,
            }
        )
        BatchStatusHistory.objects.get_or_create(batch=created, to_status=created.status, defaults={'from_status': '', 'changed_by': educator, 'signature_user': educator})
        if not hasattr(created, 'access_token'):
            token = ensure_batch_token(batch=created, created_by=educator, expires_at=timezone.now() + timedelta(days=2))
            self.stdout.write(self.style.SUCCESS(f'CREATED batch manual_code={token.manual_code}, raw_token={token.raw_token}'))
        ensure_chat_thread(created)
        create_system_message(created, 'Демо-партия создана')

        transit, _ = WasteBatch.objects.get_or_create(
            batch_number='WG-DEMO-00002',
            defaults={
                'waste_type': wt2, 'quantity': 7.25, 'unit': 'l', 'creator_org': edu_org, 'created_by': educator,
                'pickup_address': 'Москва, ул. Больничная, 10', 'processor_org': proc_org, 'delivery_address_snapshot': 'Москва, ул. Заводская, 2',
                'comment': 'Demo transit batch', 'status': BatchStatusChoices.IN_TRANSIT, 'current_driver': driver,
                'picked_up_at': timezone.now() - timedelta(hours=2),
            }
        )
        BatchStatusHistory.objects.get_or_create(batch=transit, to_status=BatchStatusChoices.CREATED, defaults={'from_status': '', 'changed_by': educator, 'signature_user': educator})
        BatchStatusHistory.objects.get_or_create(batch=transit, to_status=BatchStatusChoices.IN_TRANSIT, defaults={'from_status': BatchStatusChoices.CREATED, 'changed_by': driver, 'signature_user': driver})
        if not hasattr(transit, 'access_token'):
            token = ensure_batch_token(batch=transit, created_by=educator, expires_at=timezone.now() + timedelta(days=1))
            self.stdout.write(self.style.SUCCESS(f'TRANSIT batch manual_code={token.manual_code}, raw_token={token.raw_token}'))
        ensure_chat_thread(transit)
        create_system_message(transit, 'Партия в пути')
        send_message(transit, educator, 'Добрый день, партию подготовили к отгрузке.')

        accepted, _ = WasteBatch.objects.get_or_create(
            batch_number='WG-DEMO-00003',
            defaults={
                'waste_type': wt1, 'quantity': 3.00, 'unit': 'pcs', 'creator_org': edu_org, 'created_by': educator,
                'pickup_address': 'Москва, ул. Больничная, 10', 'processor_org': proc_org, 'delivery_address_snapshot': 'Москва, ул. Заводская, 2',
                'comment': 'Demo accepted batch', 'status': BatchStatusChoices.ACCEPTED, 'current_driver': driver,
                'picked_up_at': timezone.now() - timedelta(days=1), 'delivered_at': timezone.now() - timedelta(hours=20), 'accepted_at': timezone.now() - timedelta(hours=18),
            }
        )
        BatchStatusHistory.objects.get_or_create(batch=accepted, to_status=BatchStatusChoices.CREATED, defaults={'from_status': '', 'changed_by': educator, 'signature_user': educator})
        BatchStatusHistory.objects.get_or_create(batch=accepted, to_status=BatchStatusChoices.IN_TRANSIT, defaults={'from_status': BatchStatusChoices.CREATED, 'changed_by': driver, 'signature_user': driver})
        BatchStatusHistory.objects.get_or_create(batch=accepted, to_status=BatchStatusChoices.ACCEPTED, defaults={'from_status': BatchStatusChoices.IN_TRANSIT, 'changed_by': processor, 'signature_user': processor})
        if not hasattr(accepted, 'access_token'):
            token = ensure_batch_token(batch=accepted, created_by=educator, expires_at=timezone.now() + timedelta(hours=4))
            self.stdout.write(self.style.SUCCESS(f'ACCEPTED batch manual_code={token.manual_code}, raw_token={token.raw_token}'))
        ensure_chat_thread(accepted)
        create_system_message(accepted, 'Партия принята переработчиком')

        log_access_attempt(batch=created, user=driver, manual_code='EXPIRED-111', success=False, failure_reason='expired_token', ip='127.0.0.1', user_agent='seed-demo')
        self.stdout.write(self.style.SUCCESS('Demo data created.'))
