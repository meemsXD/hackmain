from django.contrib import admin
from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'inn', 'kpp']
    search_fields = ['name', 'inn', 'kpp']
    ordering = ['name']
