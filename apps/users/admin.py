from django.contrib import admin
from .models import User, DriverProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'role', 'organization', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['email', 'full_name']

@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'vehicle_number']
