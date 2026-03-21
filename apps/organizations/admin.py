from django.contrib import admin
from .models import Organization, EducatorProfile, ProcessorProfile

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'inn', 'kpp']
    search_fields = ['name', 'inn']

@admin.register(EducatorProfile)
class EducatorProfileAdmin(admin.ModelAdmin):
    list_display = ['organization', 'license_number', 'pickup_address']

@admin.register(ProcessorProfile)
class ProcessorProfileAdmin(admin.ModelAdmin):
    list_display = ['organization', 'license_number', 'facility_address']
