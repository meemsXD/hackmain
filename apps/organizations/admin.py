from django.contrib import admin
from .models import Organization, EducatorOrgProfile, ProcessorOrgProfile

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'inn', 'kpp', 'status', 'created_at')
    search_fields = ('name', 'inn', 'kpp')
    list_filter = ('status',)

admin.site.register(EducatorOrgProfile)
admin.site.register(ProcessorOrgProfile)
