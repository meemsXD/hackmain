from django.db import models
from apps.common.models import BaseModel

class WasteType(BaseModel):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name
