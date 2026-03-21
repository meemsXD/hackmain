import uuid
from django.db import models


class WasteBatch(models.Model):
    WASTE_TYPE_CHOICES = [
        ('medicines', 'Лекарственные препараты'),
        ('disinfectants', 'Дезинфектанты'),
        ('mercury', 'Ртутьсодержащие'),
        ('cytostatics', 'Цитостатики'),
        ('other', 'Иное'),
    ]
    UNIT_CHOICES = [
        ('kg', 'кг'),
        ('l', 'л'),
        ('pcs', 'шт'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    waste_type = models.CharField(max_length=32, choices=WASTE_TYPE_CHOICES, verbose_name='Тип отходов')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Количество')
    unit = models.CharField(max_length=8, choices=UNIT_CHOICES, verbose_name='Единица измерения')
    educator = models.ForeignKey(
        'organizations.Organization', on_delete=models.PROTECT,
        related_name='created_batches', verbose_name='Образователь'
    )
    pickup_address = models.CharField(max_length=500, verbose_name='Точка вывоза')
    delivery_address = models.CharField(max_length=500, verbose_name='Точка доставки')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'waste_batch'
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.waste_type} {self.quantity}{self.unit}'


class BatchStatus(models.Model):
    STATUS_CHOICES = [
        ('CREATED', 'Создана'),
        ('IN_TRANSIT', 'В пути'),
        ('ACCEPTED', 'Принята'),
        ('CANCELLED', 'Отменена'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(WasteBatch, on_delete=models.CASCADE, related_name='statuses')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, verbose_name='Состояние')
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name='Время')

    class Meta:
        db_table = 'batch_status'
        ordering = ('changed_at',)

    def __str__(self):
        return f'{self.batch} → {self.status}'


class QRToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.OneToOneField(WasteBatch, on_delete=models.CASCADE, related_name='qr_token')
    expires_at = models.DateTimeField(verbose_name='Время действия')
    code = models.CharField(max_length=32, unique=True, verbose_name='Код')
    is_active = models.BooleanField(default=True, verbose_name='Активность')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qr_token'

    def __str__(self):
        return f'QR {self.code} → {self.batch}'
