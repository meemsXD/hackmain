import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('EDUCATOR', 'Образователь'),
        ('DRIVER', 'Водитель'),
        ('PROCESSOR', 'Переработчик'),
        ('INSPECTOR', 'Инспектор'),
        ('ADMIN', 'Администратор'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    organization = models.ForeignKey(
        'organizations.Organization', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='users'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        db_table = 'user'

    def __str__(self):
        return f'{self.email} ({self.role})'


class DriverProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    vehicle_number = models.CharField(max_length=64)

    class Meta:
        db_table = 'driver_profile'

    def __str__(self):
        return f'{self.user.full_name} - {self.vehicle_number}'
