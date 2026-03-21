from django.contrib import admin
from .models import Waste, Status, QR

@admin.register(Waste)
class WasteAdmin(admin.ModelAdmin):
    list_display = ['waste_type', 'quantity', 'medical_organization', 'pickup_point', 'delivery_point']
    list_filter  = ['waste_type']

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['waste', 'state', 'time']

@admin.register(QR)
class QRAdmin(admin.ModelAdmin):
    list_display = ['code', 'waste', 'time', 'is_active']
