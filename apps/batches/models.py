from django.db import models
from django.utils import timezone

from apps.users.models import MedicalOrganization, Recycler


class Waste(models.Model):
    """Waste batch entity."""

    STATUS_CHOICES = [
        ('CREATED',    'Создана'),
        ('IN_TRANSIT', 'В пути'),
        ('DELIVERED',  'Доставлена'),
        ('ACCEPTED',   'Принята переработчиком'),
        ('CANCELLED',  'Отменена'),
    ]

    waste_type = models.CharField(max_length=128, verbose_name='Тип')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Кол-во')
    medical_organization = models.ForeignKey(
        MedicalOrganization,
        on_delete=models.PROTECT,
        related_name='wastes',
        verbose_name='Образователь',
    )
    pickup_point = models.CharField(max_length=500, verbose_name='Точка вывоза')
    delivery_point = models.ForeignKey(
        Recycler,
        on_delete=models.PROTECT,
        related_name='wastes',
        verbose_name='Переработчик',
    )
    created_by = models.ForeignKey(
        'users.User',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='created_wastes',
        verbose_name='Создатель',
    )
    current_status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default='CREATED',
        verbose_name='Текущий статус',
    )

    class Meta:
        db_table = 'othody'

    def __str__(self):
        return f'{self.waste_type} {self.quantity}'


class Status(models.Model):
    """СТАТУС: id, сост., время, id_отходов, кем изменён"""

    STATE_CHOICES = [
        ('CREATED',    'Создана'),
        ('IN_TRANSIT', 'В пути'),
        ('DELIVERED',  'Доставлена'),
        ('ACCEPTED',   'Принята переработчиком'),
        ('CANCELLED',  'Отменена'),
    ]

    state = models.CharField(max_length=16, choices=STATE_CHOICES, verbose_name='Состояние')
    time = models.DateTimeField(auto_now_add=True, verbose_name='Время')
    waste = models.ForeignKey(
        Waste,
        on_delete=models.CASCADE,
        related_name='statuses',
        verbose_name='Партия',
    )
    changed_by = models.ForeignKey(
        'users.User',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='status_changes',
        verbose_name='Кем изменён',
    )

    class Meta:
        db_table = 'status'
        ordering = ('time',)

    def __str__(self):
        return f'{self.waste} → {self.state}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Синхронизируем current_status на партии
        self.waste.current_status = self.state
        self.waste.save(update_fields=['current_status'])


class QR(models.Model):
    """QR: id, срок действия, id_отходов, код, активность, создатель"""

    waste = models.OneToOneField(
        Waste,
        on_delete=models.CASCADE,
        related_name='qr',
        verbose_name='Партия',
    )
    code = models.CharField(max_length=64, unique=True, verbose_name='Код')
    expires_at = models.DateTimeField(
        verbose_name='Срок действия',
        default=timezone.now
    )
    is_active = models.BooleanField(default=True, verbose_name='Активность')
    created_by = models.ForeignKey(
        'users.User',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='created_qrs',
        verbose_name='Создатель',
    )

    class Meta:
        db_table = 'qr'

    def __str__(self):
        return f'QR {self.code} → {self.waste}'

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def deactivate_if_expired(self):
        """Деактивирует QR если срок истёк."""
        if self.is_expired and self.is_active:
            self.is_active = False
            self.save(update_fields=['is_active'])
        return self.is_active


class QRScanLog(models.Model):
    """Log of QR scans, including blocked attempts."""

    qr = models.ForeignKey(
        QR,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='scan_logs',
        verbose_name='QR',
    )
    raw_code = models.CharField(max_length=64, verbose_name='Сканированный код')
    scanned_by = models.ForeignKey(
        'users.User',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='qr_scans',
        verbose_name='Кто сканировал',
    )
    scanned_at = models.DateTimeField(auto_now_add=True, verbose_name='Время')
    success = models.BooleanField(default=False, verbose_name='Успешно')
    fail_reason = models.CharField(max_length=128, blank=True, verbose_name='Причина отказа')

    class Meta:
        db_table = 'qr_scan_log'
        ordering = ('-scanned_at',)

    def __str__(self):
        status = 'OK' if self.success else f'FAIL: {self.fail_reason}'
        return f'{self.raw_code} [{status}] at {self.scanned_at}'
