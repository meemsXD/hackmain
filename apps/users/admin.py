from django.contrib import admin
from .models import User, DriverProfile, MedicalOrganization, Recycler

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['login', 'full_name', 'role', 'organization']
    list_filter  = ['role']

@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ['vehicle_number']

@admin.register(MedicalOrganization)
class MedicalOrganizationAdmin(admin.ModelAdmin):
    list_display = ['license_number', 'address']

@admin.register(Recycler)
class RecyclerAdmin(admin.ModelAdmin):
    list_display = ['license_number', 'facility_address']
