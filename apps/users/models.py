from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from apps.organizations.models import Organization


class UserManager(BaseUserManager):
    def create_user(self, login, password=None, **extra_fields):
        if not login:
            raise ValueError('Логин обязателен')
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        return self.create_user(login, password, **extra_fields)


class DriverProfile(models.Model):
    """ВОД: id, номер ТС"""
    vehicle_number = models.CharField(max_length=64, verbose_name='Номер ТС')

    class Meta:
        db_table = 'vod'

    def __str__(self):
        return self.vehicle_number


class MedicalOrganization(models.Model):
    """ОБР: id, лицензия, адрес"""
    license_number = models.CharField(max_length=128, verbose_name='Лицензия')
    address = models.CharField(max_length=500, verbose_name='Адрес')

    class Meta:
        db_table = 'obr'

    def __str__(self):
        return f'Образователь: {self.license_number}'


class Recycler(models.Model):
    """ПЕРЕРАБОТЧИК: id, номер лиц., адр. пл., сп. водит."""
    license_number = models.CharField(max_length=128, verbose_name='Номер лицензии')
    facility_address = models.CharField(max_length=500, verbose_name='Адрес площадки')
    drivers = models.ManyToManyField(
        DriverProfile,
        blank=True,
        related_name='recyclers',
        verbose_name='Список водителей',
    )

    class Meta:
        db_table = 'pererabotchik'

    def __str__(self):
        return f'Переработчик: {self.license_number}'


class User(AbstractBaseUser, PermissionsMixin):
    """USER: id, full_name, role, password, org_id, login + профили ролей"""

    ROLE_CHOICES = [
        ('RECYCLER',  'Образователь'),
        ('DRIVER',    'Водитель'),
        ('MEDICAL',   'Переработчик'),
        ('INSPECTOR', 'Инспектор'),
        ('ADMIN',     'Администратор'),
    ]

    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, verbose_name='Роль')
    # password хранится в AbstractBaseUser
    organization = models.ForeignKey(
        Organization,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='users',
        verbose_name='Организация',
    )
    login = models.CharField(max_length=150, unique=True, verbose_name='Логин')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # доступ к Django admin

    # Профили ролей (заполняется только нужное в зависимости от role)
    driver_profile = models.OneToOneField(
        DriverProfile,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='user',
        verbose_name='Профиль водителя',
    )
    medical_org = models.OneToOneField(
        MedicalOrganization,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='user',
        verbose_name='Профиль образователя',
    )
    recycler_profile = models.OneToOneField(
        Recycler,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='user',
        verbose_name='Профиль переработчика',
    )

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        db_table = 'user'

    def __str__(self):
        return f'{self.login} ({self.role})'

    @property
    def profile(self):
        """Возвращает профиль роли пользователя."""
        if self.role == 'DRIVER':
            return self.driver_profile
        if self.role == 'RECYCLER':
            return self.medical_org
        if self.role == 'MEDICAL':
            return self.recycler_profile
        return None
