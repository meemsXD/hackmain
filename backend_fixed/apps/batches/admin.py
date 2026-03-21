from django.contrib import admin
from .models import WasteBatch, BatchStatusHistory

@admin.register(WasteBatch)
class WasteBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_number', 'status', 'creator_org', 'processor_org', 'created_at')
    list_filter = ('status', 'unit')
    search_fields = ('batch_number', 'creator_org__name', 'processor_org__name')

admin.site.register(BatchStatusHistory)
