from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView, FormView, CreateView, View
from apps.rentals.models import Lease
from .models import Payment
from .forms import PaymentInitiateForm, SimulatedCheckoutForm


class PaymentListView(LoginRequiredMixin, ListView):
    """
    Displays payment history, pending bills, and receipts.
    Strictly filters data to authorized participants (tenant, owner, or admin).
    """
    model = Payment
    template_name = 'payments/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.is_admin_role:
            return Payment.objects.all().select_related('lease', 'tenant', 'lease__property').order_by('-created_at')
        elif user.is_owner_role:
            return Payment.objects.filter(lease__owner=user).select_related('lease', 'tenant', 'lease__property').order_by('-created_at')
        return Payment.objects.filter(tenant=user).select_related('lease', 'lease__property').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context['total_paid'] = qs.filter(status=Payment.PaymentStatus.PAID).aggregate(Sum('amount'))['amount__sum'] or 0.00
        context['total_pending'] = qs.filter(status=Payment.PaymentStatus.PENDING).aggregate(Sum('amount'))['amount__sum'] or 0.00
        return context


class CreatePaymentForLeaseView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Generates an active invoice for the current month's rent on a lease.
    Guarded with database transaction locking to prevent duplicate pending invoices.
    """
    def test_func(self):
        lease = get_object_or_404(Lease, pk=self.kwargs['lease_id'])
        return lease.tenant == self.request.user or lease.owner == self.request.user or self.request.user.is_admin_role

    def get(self, request, lease_id):
        with transaction.atomic():
            lease = Lease.objects.select_for_update().get(pk=lease_id)
            if lease.status != Lease.LeaseStatus.ACTIVE:
                messages.error(request, f"Cannot generate rent invoices for inactive Lease #{lease.lease_number}.")
                return redirect('rentals:lease_detail', pk=lease.pk)

            # Check if unsettled invoice already exists to prevent duplicate billing
            pending_payment = Payment.objects.filter(
                lease=lease,
                status=Payment.PaymentStatus.PENDING,
                payment_type=Payment.PaymentType.RENT
            ).first()

            if not pending_payment:
                pending_payment = Payment.objects.create(
                    lease=lease,
                    tenant=lease.tenant,
                    amount=lease.monthly_rent,
                    payment_type=Payment.PaymentType.RENT,
                    description=f"Rent for {lease.property.title} ({timezone.now().strftime('%B %Y')})",
                    due_date=timezone.now().date(),
                    status=Payment.PaymentStatus.PENDING
                )

        return redirect('payments:checkout', payment_id=pending_payment.id)


class SimulatedCheckoutView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    """
    Realistic simulated payment sandbox checkout.
    Uses select_for_update within an atomic transaction to prevent double charges / race conditions.
    """
    template_name = 'payments/checkout.html'
    form_class = SimulatedCheckoutForm

    def test_func(self):
        payment = get_object_or_404(Payment, pk=self.kwargs['payment_id'])
        return payment.tenant == self.request.user or self.request.user.is_admin_role

    def get_payment(self):
        return get_object_or_404(Payment, pk=self.kwargs['payment_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment'] = self.get_payment()
        return context

    def form_valid(self, form):
        with transaction.atomic():
            payment = Payment.objects.select_for_update().get(pk=self.kwargs['payment_id'])
            
            # Idempotency / Double payment prevention
            if payment.status == Payment.PaymentStatus.PAID:
                messages.info(self.request, f"Invoice {payment.transaction_id} has already been paid and settled.")
                return redirect('payments:receipt', pk=payment.pk)

            method = form.cleaned_data.get('payment_method', 'CARD')
            payment.payment_method = method
            payment.status = Payment.PaymentStatus.PAID
            payment.paid_at = timezone.now()
            payment.save()

        messages.success(
            self.request,
            f"Payment of ${payment.amount} processed successfully via Simulated {method}! Transaction ID: {payment.transaction_id}"
        )
        return redirect('payments:receipt', pk=payment.pk)


class PaymentReceiptView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Detailed printable receipt for a settled transaction.
    Secured so only paying tenant, property owner, or admin can access.
    """
    model = Payment
    template_name = 'payments/receipt.html'
    context_object_name = 'payment'

    def test_func(self):
        payment = self.get_object()
        return (
            payment.tenant == self.request.user or
            payment.lease.owner == self.request.user or
            self.request.user.is_admin_role
        )
