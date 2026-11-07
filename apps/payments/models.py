from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid


class Payment(models.Model):
    """
    Financial transaction record for rent, security deposits, and maintenance charges.
    Includes simulated sandbox transaction tracking.
    """
    class PaymentType(models.TextChoices):
        RENT = 'RENT', _('Monthly Rent')
        SECURITY_DEPOSIT = 'SECURITY_DEPOSIT', _('Security Deposit')
        MAINTENANCE_FEE = 'MAINTENANCE_FEE', _('Maintenance / Repair Charge')
        LATE_FEE = 'LATE_FEE', _('Late Payment Penalty')
        OTHER = 'OTHER', _('Other Charge')

    class PaymentMethod(models.TextChoices):
        CARD = 'CARD', _('Credit / Debit Card (Simulated)')
        UPI = 'UPI', _('Instant UPI / QR (Simulated)')
        BANK_TRANSFER = 'BANK_TRANSFER', _('Direct Bank Wire')
        CASH = 'CASH', _('Cash / Offline Receipt')

    class PaymentStatus(models.TextChoices):
        PAID = 'PAID', _('Paid Successfully')
        PENDING = 'PENDING', _('Pending Payment')
        FAILED = 'FAILED', _('Payment Failed')
        REFUNDED = 'REFUNDED', _('Refunded')

    lease = models.ForeignKey(
        'rentals.Lease',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('Lease Agreement')
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('Payer (Tenant)')
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount ($)'))
    payment_type = models.CharField(
        max_length=30,
        choices=PaymentType.choices,
        default=PaymentType.RENT,
        verbose_name=_('Payment Type')
    )
    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CARD,
        verbose_name=_('Payment Method')
    )
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name=_('Transaction Reference ID')
    )
    status = models.CharField(
        max_length=30,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name=_('Payment Status')
    )
    description = models.CharField(max_length=255, verbose_name=_('Payment Description'))
    due_date = models.DateField(default=timezone.now, verbose_name=_('Due Date'))
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Settled Timestamp'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Invoice Created'))

    class Meta:
        verbose_name = _('Payment & Invoice')
        verbose_name_plural = _('Payments & Invoices')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def is_settled(self):
        return self.status == self.PaymentStatus.PAID

    def __str__(self):
        return f"{self.transaction_id}: ${self.amount} ({self.get_status_display()}) by {self.tenant.username}"
