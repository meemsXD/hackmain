from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'object_type', 'object_id', 'user', 'created_at']
    list_filter = ['action', 'object_type']
    readonly_fields = ['user', 'action', 'object_type', 'object_id', 'before', 'after', 'created_at']
