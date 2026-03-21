from django.db import models

class RoleChoices(models.TextChoices):
    EDUCATOR = 'EDUCATOR', 'Образователь'
    DRIVER = 'DRIVER', 'Водитель'
    PROCESSOR = 'PROCESSOR', 'Переработчик'
    INSPECTOR = 'INSPECTOR', 'Инспектор'
    ADMIN = 'ADMIN', 'Администратор'

class OrgStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'На модерации'
    ACTIVE = 'ACTIVE', 'Активна'
    BLOCKED = 'BLOCKED', 'Заблокирована'

class RequestStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'На рассмотрении'
    APPROVED = 'APPROVED', 'Одобрена'
    REJECTED = 'REJECTED', 'Отклонена'

class UnitChoices(models.TextChoices):
    KG = 'kg', 'кг'
    L = 'l', 'л'
    PCS = 'pcs', 'шт'

class BatchStatusChoices(models.TextChoices):
    CREATED = 'CREATED', 'Создана'
    IN_TRANSIT = 'IN_TRANSIT', 'В пути'
    ACCEPTED = 'ACCEPTED', 'Принята'
    CANCELLED = 'CANCELLED', 'Отменена'
