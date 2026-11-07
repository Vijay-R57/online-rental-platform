from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class MaintenanceRequest(models.Model):
    """
    Repair, maintenance, and issue ticket submitted by a tenant for their rental unit.
    """
    class Category(models.TextChoices):
        PLUMBING = 'PLUMBING', _('Plumbing & Water Leak')
        ELECTRICAL = 'ELECTRICAL', _('Electrical & Lighting')
        APPLIANCE = 'APPLIANCE', _('Kitchen / Home Appliance')
        HVAC = 'HVAC', _('Air Conditioning & Heating')
        LOCKS_SECURITY = 'SECURITY', _('Doors, Locks & Security')
        STRUCTURAL = 'STRUCTURAL', _('Structural, Windows & Pest')
        OTHER = 'OTHER', _('General Repair / Other')

    class Priority(models.TextChoices):
        LOW = 'LOW', _('Low (Routine Maintenance)')
        MEDIUM = 'MEDIUM', _('Medium (Noticeable Inconvenience)')
        HIGH = 'HIGH', _('High (Urgent Attention)')
        EMERGENCY = 'EMERGENCY', _('Emergency (Immediate Safety Hazard)')

    class Status(models.TextChoices):
        SUBMITTED = 'SUBMITTED', _('Submitted / Awaiting Review')
        IN_PROGRESS = 'IN_PROGRESS', _('Technician Dispatched / In Progress')
        RESOLVED = 'RESOLVED', _('Resolved / Completed')
        CLOSED = 'CLOSED', _('Closed')

    property = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='maintenance_requests',
        verbose_name=_('Property')
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='maintenance_requests',
        verbose_name=_('Reporting Tenant')
    )

    ticket_number = models.CharField(max_length=50, unique=True, blank=True, verbose_name=_('Ticket #'))
    title = models.CharField(max_length=200, verbose_name=_('Issue Summary / Title'))
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.PLUMBING,
        verbose_name=_('Issue Category')
    )
    priority = models.CharField(
        max_length=30,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name=_('Priority Level')
    )
    description = models.TextField(verbose_name=_('Detailed Description of the Issue'))
    attachment = models.ImageField(
        upload_to='maintenance/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_('Photo / Evidence')
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.SUBMITTED,
        verbose_name=_('Ticket Status')
    )
    landlord_response = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Owner / Management Response & Contractor Notes')
    )
    resolved_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Resolved Date'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Reported At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Maintenance Request')
        verbose_name_plural = _('Maintenance Requests')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            import uuid
            self.ticket_number = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        if self.status == self.Status.RESOLVED and not self.resolved_at:
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_number}: {self.title} ({self.get_status_display()})"
