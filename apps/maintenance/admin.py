from django.contrib import admin
from .models import MaintenanceRequest


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = (
        'ticket_number', 'title', 'property', 'tenant',
        'category', 'priority', 'status', 'created_at', 'resolved_at'
    )
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('ticket_number', 'title', 'description', 'property__title', 'tenant__username')
    readonly_fields = ('ticket_number', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
