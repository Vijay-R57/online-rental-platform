from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Custom user model for Online Property Rental and Management Portal.
    Extends AbstractUser to support role-based access control (ADMIN, OWNER, TENANT)
    and common user profile fields.
    """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        OWNER = 'OWNER', _('Property Owner')
        TENANT = 'TENANT', _('Tenant')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.TENANT,
        verbose_name=_('Role'),
        help_text=_('Designates the primary role of this user in the rental portal.')
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Phone Number'),
        help_text=_('Primary contact phone number')
    )
    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name=_('Profile Picture'),
        help_text=_('Avatar image for user profile')
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Verified User'),
        help_text=_('Designates whether this user has been verified.')
    )
    # Extended Profile Information
    bio = models.TextField(blank=True, null=True, verbose_name=_('Biography / About Me'))
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Current Address'))
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('City'))
    state = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('State / Province'))
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Postal Code'))
    
    # Employment & Rental Context (for Tenants & Owners)
    occupation = models.CharField(max_length=150, blank=True, null=True, verbose_name=_('Occupation / Title'))
    company_name = models.CharField(max_length=150, blank=True, null=True, verbose_name=_('Company / Employer'))
    emergency_contact_name = models.CharField(max_length=150, blank=True, null=True, verbose_name=_('Emergency Contact Name'))
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Emergency Contact Phone'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_owner_role(self):
        return self.role == self.Role.OWNER

    @property
    def is_tenant_role(self):
        return self.role == self.Role.TENANT

    def save(self, *args, **kwargs):
        # Automatically assign ADMIN role to superusers
        if self.is_superuser and self.role != self.Role.ADMIN:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    def __str__(self):
        role_label = self.get_role_display()
        full_name = self.get_full_name()
        if full_name:
            return f"{full_name} ({self.username}) - {role_label}"
        return f"{self.username} - {role_label}"


class TenantDocument(models.Model):
    """
    Verification and identification documents uploaded by tenants for leasing and KYC.
    """
    class DocumentType(models.TextChoices):
        GOVERNMENT_ID = 'GOVT_ID', _('Government Issued Photo ID')
        PAYSLIP = 'PAYSLIP', _('Proof of Income / Payslip')
        EMPLOYMENT_LETTER = 'EMPLOYMENT_LETTER', _('Employment Offer / Verification')
        RENTAL_REFERENCE = 'REFERENCE', _('Previous Landlord Reference')
        TAX_RETURN = 'TAX_RETURN', _('Tax Return / W-2')
        OTHER = 'OTHER', _('Other Supporting Document')

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('Tenant User')
    )
    document_type = models.CharField(
        max_length=30,
        choices=DocumentType.choices,
        default=DocumentType.GOVERNMENT_ID,
        verbose_name=_('Document Type')
    )
    title = models.CharField(max_length=200, verbose_name=_('Document Title / Description'))
    document_file = models.FileField(
        upload_to='tenant_documents/%Y/%m/',
        verbose_name=_('Document File')
    )
    is_verified = models.BooleanField(default=False, verbose_name=_('Verified by Management'))
    verification_notes = models.TextField(blank=True, null=True, verbose_name=_('Verification Notes'))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Uploaded At'))

    class Meta:
        verbose_name = _('Tenant Document')
        verbose_name_plural = _('Tenant Documents')
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_document_type_display()} ({self.title})"
