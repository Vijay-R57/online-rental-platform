from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from apps.rentals.models import Lease, Booking
from .models import MaintenanceRequest
from .forms import MaintenanceRequestCreateForm, MaintenanceRequestUpdateForm


class MaintenanceListView(LoginRequiredMixin, ListView):
    """
    Lists maintenance requests and complaints.
    Strictly isolated: tenants only see their tickets, owners only see tickets on their properties.
    """
    model = MaintenanceRequest
    template_name = 'maintenance/maintenance_list.html'
    context_object_name = 'tickets'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.is_admin_role:
            return MaintenanceRequest.objects.all().select_related('property', 'tenant').order_by('-created_at')
        elif user.is_owner_role:
            return MaintenanceRequest.objects.filter(property__owner=user).select_related('property', 'tenant').order_by('-created_at')
        return MaintenanceRequest.objects.filter(tenant=user).select_related('property').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context['open_count'] = qs.filter(status__in=[MaintenanceRequest.Status.SUBMITTED, MaintenanceRequest.Status.IN_PROGRESS]).count()
        context['resolved_count'] = qs.filter(status__in=[MaintenanceRequest.Status.RESOLVED, MaintenanceRequest.Status.CLOSED]).count()
        return context


class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    """
    Allows a tenant to report a maintenance issue or defect.
    Strictly verifies the tenant has an active tenancy on the target property.
    """
    model = MaintenanceRequest
    form_class = MaintenanceRequestCreateForm
    template_name = 'maintenance/maintenance_form.html'
    success_url = reverse_lazy('maintenance:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        target_property = form.cleaned_data.get('property')

        # Authorization guard: Non-admin users must hold an active lease or booking
        if not user.is_admin_role:
            has_lease = Lease.objects.filter(property=target_property, tenant=user, status=Lease.LeaseStatus.ACTIVE).exists()
            has_booking = Booking.objects.filter(property=target_property, tenant=user).exists()
            if not (has_lease or has_booking):
                form.add_error('property', "Access Denied: You do not hold an active lease or confirmed booking for this property.")
                return self.form_invalid(form)

        form.instance.tenant = self.request.user
        messages.success(
            self.request,
            f"Maintenance ticket '{form.instance.title}' has been logged and sent to your property owner."
        )
        return super().form_valid(form)


class MaintenanceDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Detailed ticket view showing complaint history, photos, and landlord responses.
    Restricted strictly to the reporting tenant, property owner, or admin.
    """
    model = MaintenanceRequest
    template_name = 'maintenance/maintenance_detail.html'
    context_object_name = 'ticket'

    def test_func(self):
        ticket = self.get_object()
        return (
            ticket.tenant == self.request.user or
            ticket.property.owner == self.request.user or
            self.request.user.is_admin_role
        )


class MaintenanceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Allows landlord or admin to update status, dispatch contractors, and reply.
    """
    model = MaintenanceRequest
    form_class = MaintenanceRequestUpdateForm
    template_name = 'maintenance/maintenance_update.html'

    def test_func(self):
        ticket = self.get_object()
        return ticket.property.owner == self.request.user or self.request.user.is_admin_role

    def form_valid(self, form):
        ticket = form.save(commit=False)
        if ticket.status == MaintenanceRequest.Status.RESOLVED and not ticket.resolved_at:
            ticket.resolved_at = timezone.now()
        ticket.save()
        messages.success(self.request, f"Maintenance ticket #{ticket.ticket_number} updated to {ticket.get_status_display()}.")
        return redirect('maintenance:detail', pk=ticket.pk)
