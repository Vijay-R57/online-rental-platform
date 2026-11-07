from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id', 'tenant', 'amount', 'payment_type',
        'payment_method', 'status', 'due_date', 'paid_at', 'created_at'
    )
    list_filter = ('status', 'payment_type', 'payment_method', 'due_date', 'paid_at')
    search_fields = ('transaction_id', 'tenant__username', 'description', 'lease__property__title')
    readonly_fields = ('transaction_id', 'created_at')
    date_hierarchy = 'created_at'
