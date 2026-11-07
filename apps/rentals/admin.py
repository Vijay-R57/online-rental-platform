from django.contrib import admin
from .models import RentalApplication, Booking, Lease


@admin.register(RentalApplication)
class RentalApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'property', 'employment_status', 'annual_income', 'status', 'applied_at')
    list_filter = ('status', 'credit_score_range', 'applied_at')
    search_fields = ('applicant__username', 'applicant__email', 'property__title')
    date_hierarchy = 'applied_at'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'tenant', 'property', 'check_in', 'status', 'deposit_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('booking_reference', 'tenant__username', 'property__title')


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = (
        'lease_number', 'property', 'owner', 'tenant',
        'monthly_rent', 'start_date', 'end_date', 'status',
        'signed_by_tenant', 'signed_by_owner'
    )
    list_filter = ('status', 'signed_by_tenant', 'signed_by_owner', 'start_date')
    search_fields = ('lease_number', 'property__title', 'owner__username', 'tenant__username')
