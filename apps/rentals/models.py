from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid


class RentalApplication(models.Model):
    """
    Rental application submitted by a tenant for a specific property.
    """
    class ApplicationStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending Owner Review')
        APPROVED = 'APPROVED', _('Application Approved')
        REJECTED = 'REJECTED', _('Application Declined')
        WITHDRAWN = 'WITHDRAWN', _('Withdrawn by Applicant')

    property = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name=_('Property')
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rental_applications',
        verbose_name=_('Tenant Applicant')
    )

    # Financial & Tenancy Credentials
    employment_status = models.CharField(max_length=100, verbose_name=_('Employment Status'))
    employer_name = models.CharField(max_length=150, blank=True, null=True, verbose_name=_('Current Employer'))
    annual_income = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Annual Gross Income ($)'))
    credit_score_range = models.CharField(
        max_length=50,
        choices=[
            ('EXCELLENT', 'Excellent (750+)'),
            ('GOOD', 'Good (700 - 749)'),
            ('FAIR', 'Fair (650 - 699)'),
            ('POOR', 'Below 650'),
        ],
        default='GOOD',
        verbose_name=_('Credit Score Estimate')
    )
    occupants_count = models.PositiveSmallIntegerField(default=1, verbose_name=_('Total Occupants'))
    has_pets = models.BooleanField(default=False, verbose_name=_('Has Domestic Pets'))
    pets_description = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('Pet Details'))

    # Lease intent
    proposed_move_in = models.DateField(verbose_name=_('Proposed Move-in Date'))
    lease_term_months = models.PositiveSmallIntegerField(default=12, verbose_name=_('Lease Term (Months)'))
    message_to_landlord = models.TextField(blank=True, null=True, verbose_name=_('Message / Notes for Landlord'))

    # Workflow Status
    status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
        verbose_name=_('Review Status')
    )
    owner_notes = models.TextField(blank=True, null=True, verbose_name=_('Owner Review Notes'))
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Applied At'))
    reviewed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Reviewed At'))

    class Meta:
        verbose_name = _('Rental Application')
        verbose_name_plural = _('Rental Applications')
        ordering = ['-applied_at']
        unique_together = ('property', 'applicant')

    def __str__(self):
        return f"{self.applicant.username} -> {self.property.title} ({self.get_status_display()})"


class Booking(models.Model):
    """
    Confirmed booking generated when an application is approved.
    """
    class BookingStatus(models.TextChoices):
        CONFIRMED = 'CONFIRMED', _('Confirmed / Awaiting Lease')
        ACTIVE = 'ACTIVE', _('Active Tenancy')
        COMPLETED = 'COMPLETED', _('Completed Tenancy')
        CANCELLED = 'CANCELLED', _('Cancelled')

    application = models.OneToOneField(
        RentalApplication,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='booking',
        verbose_name=_('Originated Application')
    )
    property = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('Property')
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('Tenant')
    )

    booking_reference = models.CharField(max_length=50, unique=True, blank=True)
    check_in = models.DateField(verbose_name=_('Move-in / Check-in Date'))
    check_out = models.DateField(blank=True, null=True, verbose_name=_('Expected Move-out Date'))
    status = models.CharField(
        max_length=30,
        choices=BookingStatus.choices,
        default=BookingStatus.CONFIRMED,
        verbose_name=_('Booking Status')
    )
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_('Security Deposit ($)'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = f"BK-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_reference}: {self.tenant.username} @ {self.property.title}"


class Lease(models.Model):
    """
    Formal legal lease agreement establishing tenancy terms, rent obligation, and validity.
    """
    class LeaseStatus(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft / Under Review')
        ACTIVE = 'ACTIVE', _('Active Legally Binding Lease')
        EXPIRED = 'EXPIRED', _('Term Expired')
        TERMINATED = 'TERMINATED', _('Terminated Early')

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='lease',
        verbose_name=_('Associated Booking')
    )
    property = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='leases',
        verbose_name=_('Property')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leases_as_owner',
        verbose_name=_('Landlord')
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leases_as_tenant',
        verbose_name=_('Tenant')
    )

    lease_number = models.CharField(max_length=60, unique=True, blank=True)
    start_date = models.DateField(verbose_name=_('Lease Start Date'))
    end_date = models.DateField(verbose_name=_('Lease End Date'))
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Monthly Rent Obligation ($)'))
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Security Deposit ($)'))
    rent_due_day = models.PositiveSmallIntegerField(default=1, verbose_name=_('Monthly Rent Due Day (1-28)'))

    terms = models.TextField(
        verbose_name=_('Terms & Conditions'),
        default="1. Rent must be paid promptly on or before the due day of each calendar month.\n2. The tenant must maintain the premises in good, sanitary condition.\n3. Alterations to fixtures are strictly prohibited without written landlord consent.\n4. Subletting without landlord permission is forbidden."
    )

    signed_by_tenant = models.BooleanField(default=False, verbose_name=_('Signed by Tenant'))
    signed_by_owner = models.BooleanField(default=False, verbose_name=_('Signed by Landlord'))
    signed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Executed Timestamp'))

    status = models.CharField(
        max_length=30,
        choices=LeaseStatus.choices,
        default=LeaseStatus.ACTIVE,
        verbose_name=_('Lease Status')
    )
    lease_document = models.FileField(
        upload_to='leases/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_('Signed Lease Document')
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Lease Agreement')
        verbose_name_plural = _('Lease Agreements')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.lease_number:
            self.lease_number = f"LS-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def is_active(self):
        return self.status == self.LeaseStatus.ACTIVE

    def __str__(self):
        return f"Lease #{self.lease_number}: {self.tenant.username} @ {self.property.title}"
