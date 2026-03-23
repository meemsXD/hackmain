from django.core.management.base import BaseCommand

from apps.users.models import User


class Command(BaseCommand):
    help = 'Гарантирует доступ в Django admin для пользователей с ролью ADMIN.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--set-superuser',
            action='store_true',
            help='Также включить is_superuser для администраторов.',
        )

    def handle(self, *args, **options):
        set_superuser = bool(options.get('set_superuser'))
        fixed = 0

        for user in User.objects.filter(role='ADMIN'):
            update_fields = []
            if not user.is_staff:
                user.is_staff = True
                update_fields.append('is_staff')
            if set_superuser and not user.is_superuser:
                user.is_superuser = True
                update_fields.append('is_superuser')
            if update_fields:
                user.save(update_fields=update_fields)
                fixed += 1

        self.stdout.write(self.style.SUCCESS(f'Updated admin users: {fixed}'))
