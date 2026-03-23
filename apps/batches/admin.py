from django.contrib import admin
from .models import Waste, Status, QR, QRScanLog

@admin.register(Waste)
class WasteAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'waste_type',
        'quantity',
        'medical_organization',
        'delivery_point',
        'current_status',
        'created_by',
    ]
    list_filter = ['current_status', 'waste_type', 'medical_organization', 'delivery_point']
    search_fields = ['waste_type', 'pickup_point', 'id']
    readonly_fields = ['current_status', 'created_by']
    autocomplete_fields = ['medical_organization', 'delivery_point', 'created_by']
    list_select_related = ['medical_organization', 'delivery_point', 'created_by']
    ordering = ['-id']

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'waste', 'state', 'time', 'changed_by']
    list_filter = ['state', 'time']
    search_fields = ['waste__id', 'state']
    autocomplete_fields = ['waste', 'changed_by']
    list_select_related = ['waste', 'changed_by']
    ordering = ['-time']

@admin.register(QR)
class QRAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'waste', 'expires_at', 'is_active', 'created_by']
    list_filter = ['is_active', 'expires_at']
    search_fields = ['code', 'waste__id']
    autocomplete_fields = ['waste', 'created_by']
    list_select_related = ['waste', 'created_by']
    ordering = ['-id']

@admin.register(QRScanLog)
class QRScanLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'raw_code', 'qr', 'scanned_by', 'scanned_at', 'success', 'fail_reason']
    list_filter = ['success', 'fail_reason', 'scanned_at']
    search_fields = ['raw_code', 'fail_reason', 'qr__code']
    autocomplete_fields = ['qr', 'scanned_by']
    list_select_related = ['qr', 'scanned_by']
    ordering = ['-scanned_at']
