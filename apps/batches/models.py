from django.db import models

from apps.users.models import MedicalOrganization, Recycler


class Waste(models.Model):
    """ОТХОДЫ: id, тип, кол-во, образователь, точка вывоза, точка доставки"""
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
        verbose_name='Образователь',
    )

    class Meta:
        db_table = 'othody'

    def __str__(self):
        return f'{self.waste_type} {self.quantity}'


class Status(models.Model):
    """СТАТУС: id, сост., время, id_отходов"""
    state = models.CharField(max_length=64, verbose_name='Состояние')
    time = models.DateTimeField(auto_now_add=True, verbose_name='Время')
    waste = models.ForeignKey(
        Waste,
        on_delete=models.CASCADE,
        related_name='statuses',
        verbose_name='id_отходов',
    )

    class Meta:
        db_table = 'status'
        ordering = ('time',)

    def __str__(self):
        return f'{self.waste} → {self.state}'


class QR(models.Model):
    """QR: id, время, id_отходов, код, активность"""
    time = models.DateTimeField(verbose_name='Время (срок действия)')
    waste = models.OneToOneField(
        Waste,
        on_delete=models.CASCADE,
        related_name='qr',
        verbose_name='id_отходов',
    )
    code = models.CharField(max_length=32, unique=True, verbose_name='Код')
    is_active = models.BooleanField(default=True, verbose_name='Активность')

    class Meta:
        db_table = 'qr'

    def __str__(self):
        return f'QR {self.code} → {self.waste}'
