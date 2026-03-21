from django.contrib import admin
from .models import UserRole, RoleRequest

admin.site.register(UserRole)

@admin.register(RoleRequest)
class RoleRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'status', 'organization', 'created_at')
    list_filter = ('role', 'status')
    search_fields = ('user__email', 'organization__name')
