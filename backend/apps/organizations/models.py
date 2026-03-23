from django.db import models


class Organization(models.Model):
    """ОРГ: id, ИНН, КПП, назв"""
    inn = models.CharField(max_length=12, verbose_name='ИНН')
    kpp = models.CharField(max_length=9,  verbose_name='КПП')
    name = models.CharField(max_length=255, verbose_name='Название')

    class Meta:
        db_table = 'org'
        unique_together = ('inn', 'kpp')

    def __str__(self):
        return f'{self.name} ({self.inn})'
