from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'action', 'object_type', 'object_id', 'user', 'created_at']
    list_filter = ['action', 'object_type', 'created_at']
    search_fields = ['action', 'object_type', 'object_id', 'user__login']
    date_hierarchy = 'created_at'
    readonly_fields = ['user', 'action', 'object_type', 'object_id', 'before', 'after', 'created_at']
    ordering = ['-created_at']
