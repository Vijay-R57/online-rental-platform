from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from apps.properties.models import Property
from .models import RentalApplication, Booking, Lease
from .forms import RentalApplicationForm, ApplicationReviewForm, LeaseCreationForm


class ApplyRentalView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Allows a tenant to submit a rental application for an available property.
    Guards against owner applying to own property and already occupied properties.
    """
    model = RentalApplication
    form_class = RentalApplicationForm
    template_name = 'rentals/apply_form.html'

    def test_func(self):
        return self.request.user.is_tenant_role or self.request.user.is_admin_role

    def get_property(self):
        return get_object_or_404(Property, pk=self.kwargs['property_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['property'] = self.get_property()
        context['existing_application'] = RentalApplication.objects.filter(
            property=context['property'],
            applicant=self.request.user
        ).first()
        return context

    def form_valid(self, form):
        property_obj = self.get_property()

        # Guard: Property status
        if not property_obj.is_available:
            messages.error(self.request, f"Property '{property_obj.title}' is currently {property_obj.get_status_display()} and not open for new applications.")
            return redirect('properties:detail', slug=property_obj.slug)

        # Guard: Owner cannot apply to their own listing
        if property_obj.owner == self.request.user:
            messages.error(self.request, "Property owners cannot submit rental applications for their own properties.")
            return redirect('properties:detail', slug=property_obj.slug)

        # Guard: Duplicate application check
        if RentalApplication.objects.filter(property=property_obj, applicant=self.request.user).exists():
            messages.warning(self.request, "You have already submitted an application for this property.")
            return redirect('rentals:my_applications')

        form.instance.property = property_obj
        form.instance.applicant = self.request.user
        messages.success(self.request, f"Application for '{property_obj.title}' submitted successfully! The owner will review your credentials.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('rentals:my_applications')


class TenantApplicationListView(LoginRequiredMixin, ListView):
    """
    Lists all rental applications submitted by the logged in tenant.
    """
    model = RentalApplication
    template_name = 'rentals/my_applications.html'
    context_object_name = 'applications'

    def get_queryset(self):
        return RentalApplication.objects.filter(applicant=self.request.user).select_related('property', 'property__owner').order_by('-applied_at')


class PropertyApplicationsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Lists applications for a specific property owned by the landlord.
    """
    model = RentalApplication
    template_name = 'rentals/property_applications.html'
    context_object_name = 'applications'

    def test_func(self):
        prop = get_object_or_404(Property, pk=self.kwargs['property_id'])
        return prop.owner == self.request.user or self.request.user.is_admin_role

    def get_queryset(self):
        return RentalApplication.objects.filter(property_id=self.kwargs['property_id']).select_related('applicant').order_by('-applied_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['property'] = get_object_or_404(Property, pk=self.kwargs['property_id'])
        return context


class OwnerAllApplicationsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Lists all applications across all properties belonging to the landlord.
    """
    model = RentalApplication
    template_name = 'rentals/owner_applications.html'
    context_object_name = 'applications'

    def test_func(self):
        return self.request.user.is_owner_role or self.request.user.is_admin_role

    def get_queryset(self):
        if self.request.user.is_admin_role:
            return RentalApplication.objects.all().select_related('property', 'applicant').order_by('-applied_at')
        return RentalApplication.objects.filter(property__owner=self.request.user).select_related('property', 'applicant').order_by('-applied_at')


class ApplicationReviewView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Allows a landlord to approve or reject a rental application.
    Protected with transaction.atomic and select_for_update against race conditions.
    """
    model = RentalApplication
    form_class = ApplicationReviewForm
    template_name = 'rentals/application_review.html'

    def test_func(self):
        app = self.get_object()
        return app.property.owner == self.request.user or self.request.user.is_admin_role

    def form_valid(self, form):
        with transaction.atomic():
            app = self.get_object()
            target_status = form.cleaned_data.get('status')
            owner_notes = form.cleaned_data.get('owner_notes', '')

            # Concurrency & Availability Guard
            if target_status == RentalApplication.ApplicationStatus.APPROVED:
                locked_prop = Property.objects.select_for_update().get(pk=app.property.pk)
                
                # Check if property is already leased to another applicant
                existing_approved = RentalApplication.objects.filter(
                    property=locked_prop,
                    status=RentalApplication.ApplicationStatus.APPROVED
                ).exclude(pk=app.pk).exists()

                if existing_approved or locked_prop.status == Property.PropertyStatus.RENTED:
                    messages.error(self.request, f"Property '{locked_prop.title}' is already leased/occupied. Cannot approve another tenant application.")
                    return redirect('rentals:owner_applications')

                app.status = RentalApplication.ApplicationStatus.APPROVED
                app.owner_notes = owner_notes
                app.reviewed_at = timezone.now()
                app.save()

                booking, _ = Booking.objects.get_or_create(
                    application=app,
                    property=locked_prop,
                    tenant=app.applicant,
                    defaults={
                        'check_in': app.proposed_move_in,
                        'deposit_amount': locked_prop.security_deposit,
                        'status': Booking.BookingStatus.CONFIRMED,
                    }
                )

                locked_prop.status = Property.PropertyStatus.RENTED
                locked_prop.save()

                # Close other competing pending applications
                competing_pending = RentalApplication.objects.filter(
                    property=locked_prop,
                    status=RentalApplication.ApplicationStatus.PENDING
                ).exclude(pk=app.pk)
                competing_pending.update(
                    status=RentalApplication.ApplicationStatus.REJECTED,
                    owner_notes="Application closed: Property has been leased to another approved applicant.",
                    reviewed_at=timezone.now()
                )

                end_date = app.proposed_move_in + timezone.timedelta(days=app.lease_term_months * 30)
                Lease.objects.get_or_create(
                    booking=booking,
                    property=locked_prop,
                    owner=locked_prop.owner,
                    tenant=app.applicant,
                    defaults={
                        'start_date': app.proposed_move_in,
                        'end_date': end_date,
                        'monthly_rent': locked_prop.rent_amount,
                        'security_deposit': locked_prop.security_deposit,
                        'rent_due_day': 1,
                        'signed_by_owner': True,
                        'signed_at': timezone.now(),
                        'status': Lease.LeaseStatus.ACTIVE,
                    }
                )
                messages.success(self.request, f"Application APPROVED! Booking #{booking.booking_reference} and active Lease have been created for {app.applicant.username}.")
            else:
                app.status = target_status
                app.owner_notes = owner_notes
                app.reviewed_at = timezone.now()
                app.save()
                messages.info(self.request, f"Application status updated to: {app.get_status_display()}.")

        return redirect('rentals:owner_applications')


class BookingListView(LoginRequiredMixin, ListView):
    """
    Lists confirmed bookings for tenant or landlord.
    """
    model = Booking
    template_name = 'rentals/booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        if self.request.user.is_admin_role:
            return Booking.objects.all().select_related('property', 'tenant', 'lease').order_by('-created_at')
        elif self.request.user.is_owner_role:
            return Booking.objects.filter(property__owner=self.request.user).select_related('property', 'tenant', 'lease').order_by('-created_at')
        return Booking.objects.filter(tenant=self.request.user).select_related('property', 'property__owner', 'lease').order_by('-created_at')


class LeaseListView(LoginRequiredMixin, ListView):
    """
    Lists all lease agreements for the logged in user.
    """
    model = Lease
    template_name = 'rentals/lease_list.html'
    context_object_name = 'leases'

    def get_queryset(self):
        if self.request.user.is_admin_role:
            return Lease.objects.all().select_related('property', 'owner', 'tenant', 'booking').order_by('-created_at')
        elif self.request.user.is_owner_role:
            return Lease.objects.filter(owner=self.request.user).select_related('property', 'tenant', 'booking').order_by('-created_at')
        return Lease.objects.filter(tenant=self.request.user).select_related('property', 'owner', 'booking').order_by('-created_at')


class LeaseDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Full digital view of a lease agreement with terms, dates, and signature status.
    """
    model = Lease
    template_name = 'rentals/lease_detail.html'
    context_object_name = 'lease'

    def test_func(self):
        lease = self.get_object()
        return lease.tenant == self.request.user or lease.owner == self.request.user or self.request.user.is_admin_role


class LeaseSignView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Digital execution endpoint for signing a lease agreement.
    Secured against signing expired leases and multiple double-signs.
    """
    def test_func(self):
        lease = get_object_or_404(Lease, pk=self.kwargs['pk'])
        return lease.tenant == self.request.user or lease.owner == self.request.user or self.request.user.is_admin_role

    def post(self, request, pk):
        with transaction.atomic():
            lease = Lease.objects.select_for_update().get(pk=pk)

            # Guard: Inactive lease status
            if lease.status not in [Lease.LeaseStatus.DRAFT, Lease.LeaseStatus.ACTIVE]:
                messages.error(request, f"Cannot sign Lease #{lease.lease_number} because its status is {lease.get_status_display()}.")
                return redirect('rentals:lease_detail', pk=pk)

            if request.user == lease.tenant:
                if lease.signed_by_tenant:
                    messages.info(request, "Your tenant digital signature is already recorded.")
                else:
                    lease.signed_by_tenant = True
                    lease.signed_at = timezone.now()
                    lease.save()
                    messages.success(request, f"Tenant signature successfully recorded on Lease #{lease.lease_number}!")
            elif request.user == lease.owner:
                if lease.signed_by_owner:
                    messages.info(request, "Landlord signature is already recorded.")
                else:
                    lease.signed_by_owner = True
                    lease.save()
                    messages.success(request, f"Landlord signature successfully recorded on Lease #{lease.lease_number}!")
            elif request.user.is_admin_role:
                lease.signed_by_owner = True
                lease.save()
                messages.success(request, f"Administrative signature verified on Lease #{lease.lease_number}.")

        return redirect('rentals:lease_detail', pk=pk)
