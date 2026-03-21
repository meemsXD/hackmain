from django.contrib import admin
from .models import WasteBatch, BatchStatus, QRToken

@admin.register(WasteBatch)
class WasteBatchAdmin(admin.ModelAdmin):
    list_display = ['waste_type', 'quantity', 'unit', 'educator', 'created_at']
    list_filter = ['waste_type']

@admin.register(BatchStatus)
class BatchStatusAdmin(admin.ModelAdmin):
    list_display = ['batch', 'status', 'changed_at']

@admin.register(QRToken)
class QRTokenAdmin(admin.ModelAdmin):
    list_display = ['batch', 'code', 'expires_at', 'is_active']
