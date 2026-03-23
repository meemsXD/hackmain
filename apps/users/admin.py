from django.contrib import admin
from .models import User, DriverProfile, MedicalOrganization, Recycler

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'login', 'full_name', 'role', 'organization', 'is_active', 'is_staff']
    list_filter = ['role', 'is_active', 'is_staff', 'organization']
    search_fields = ['login', 'full_name']
    autocomplete_fields = ['organization', 'driver_profile', 'medical_org', 'recycler_profile']
    list_select_related = ['organization', 'driver_profile', 'medical_org', 'recycler_profile']
    ordering = ['-id']

@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle_number']
    search_fields = ['vehicle_number']
    ordering = ['-id']

@admin.register(MedicalOrganization)
class MedicalOrganizationAdmin(admin.ModelAdmin):
    list_display = ['id', 'license_number', 'address']
    search_fields = ['license_number', 'address']
    ordering = ['-id']

@admin.register(Recycler)
class RecyclerAdmin(admin.ModelAdmin):
    list_display = ['id', 'license_number', 'facility_address']
    search_fields = ['license_number', 'facility_address']
    filter_horizontal = ['drivers']
    ordering = ['-id']
