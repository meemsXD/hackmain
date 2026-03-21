from django.contrib import admin
from .models import AuditEvent

@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ('action', 'object_type', 'object_id', 'actor_user', 'created_at')
    search_fields = ('action', 'object_type', 'object_id', 'actor_user__email')
    list_filter = ('action', 'object_type')
    readonly_fields = ('before_data', 'after_data', 'ip', 'user_agent', 'created_at', 'updated_at')
