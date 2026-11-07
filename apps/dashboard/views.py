from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count
from apps.accounts.models import CustomUser
from apps.properties.models import Property
from apps.rentals.models import RentalApplication, Booking, Lease
from apps.payments.models import Payment
from apps.maintenance.models import MaintenanceRequest


class DashboardIndexView(LoginRequiredMixin, TemplateView):
    """
    Role-aware dashboard view rendering genuine, database-derived analytics,
    recent operational activities, and quick actions for ADMIN, OWNER, and TENANT.
    """
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        context['role'] = user.role

        if user.is_admin_role:
            context['dashboard_type'] = 'Administrator'
            total_rev = Payment.objects.filter(status=Payment.PaymentStatus.PAID).aggregate(Sum('amount'))['amount__sum'] or 0.00
            pending_rev = Payment.objects.filter(status=Payment.PaymentStatus.PENDING).aggregate(Sum('amount'))['amount__sum'] or 0.00

            context['stats'] = [
                {'label': 'Total Users', 'value': CustomUser.objects.count(), 'icon': 'bi-people', 'color': 'primary'},
                {'label': 'Listed Properties', 'value': Property.objects.count(), 'icon': 'bi-buildings', 'color': 'info'},
                {'label': 'Active Leases', 'value': Lease.objects.filter(status=Lease.LeaseStatus.ACTIVE).count(), 'icon': 'bi-file-earmark-check', 'color': 'success'},
                {'label': 'Total Rent Processed', 'value': f"${total_rev:,.2f}", 'icon': 'bi-cash-coin', 'color': 'success'},
                {'label': 'Pending Invoices', 'value': f"${pending_rev:,.2f}", 'icon': 'bi-hourglass-split', 'color': 'warning'},
                {'label': 'Pending Applications', 'value': RentalApplication.objects.filter(status=RentalApplication.ApplicationStatus.PENDING).count(), 'icon': 'bi-inbox', 'color': 'warning'},
                {'label': 'Open Maintenance', 'value': MaintenanceRequest.objects.filter(status__in=[MaintenanceRequest.Status.SUBMITTED, MaintenanceRequest.Status.IN_PROGRESS]).count(), 'icon': 'bi-tools', 'color': 'danger'},
                {'label': 'Total Bookings', 'value': Booking.objects.count(), 'icon': 'bi-calendar-check', 'color': 'secondary'},
            ]
            context['recent_properties'] = Property.objects.all().select_related('owner').order_by('-created_at')[:5]
            context['recent_applications'] = RentalApplication.objects.all().select_related('property', 'applicant').order_by('-applied_at')[:5]
            context['recent_payments'] = Payment.objects.all().select_related('tenant', 'lease').order_by('-created_at')[:5]
            context['recent_maintenance'] = MaintenanceRequest.objects.all().select_related('property', 'tenant').order_by('-created_at')[:5]

        elif user.is_owner_role:
            context['dashboard_type'] = 'Property Owner'
            my_properties = Property.objects.filter(owner=user)
            my_leases = Lease.objects.filter(owner=user)
            my_payments = Payment.objects.filter(lease__owner=user)

            collected_rev = my_payments.filter(status=Payment.PaymentStatus.PAID).aggregate(Sum('amount'))['amount__sum'] or 0.00
            pending_rev = my_payments.filter(status=Payment.PaymentStatus.PENDING).aggregate(Sum('amount'))['amount__sum'] or 0.00
            pending_apps = RentalApplication.objects.filter(property__owner=user, status=RentalApplication.ApplicationStatus.PENDING).count()
            open_maintenance = MaintenanceRequest.objects.filter(property__owner=user, status__in=[MaintenanceRequest.Status.SUBMITTED, MaintenanceRequest.Status.IN_PROGRESS]).count()

            context['stats'] = [
                {'label': 'My Properties', 'value': my_properties.count(), 'icon': 'bi-houses', 'color': 'primary'},
                {'label': 'Occupied Units', 'value': my_properties.filter(status=Property.PropertyStatus.RENTED).count(), 'icon': 'bi-person-check', 'color': 'success'},
                {'label': 'Vacant / Available', 'value': my_properties.filter(status=Property.PropertyStatus.AVAILABLE).count(), 'icon': 'bi-door-open', 'color': 'info'},
                {'label': 'Active Leases', 'value': my_leases.filter(status=Lease.LeaseStatus.ACTIVE).count(), 'icon': 'bi-file-earmark-text', 'color': 'success'},
                {'label': 'Rent Collected', 'value': f"${collected_rev:,.2f}", 'icon': 'bi-cash-stack', 'color': 'success'},
                {'label': 'Pending Rent', 'value': f"${pending_rev:,.2f}", 'icon': 'bi-clock-history', 'color': 'warning'},
                {'label': 'Applications to Review', 'value': pending_apps, 'icon': 'bi-inbox', 'color': 'warning'},
                {'label': 'Open Repair Tickets', 'value': open_maintenance, 'icon': 'bi-tools', 'color': 'danger'},
            ]
            context['recent_properties'] = my_properties.order_by('-created_at')[:5]
            context['recent_applications'] = RentalApplication.objects.filter(property__owner=user).select_related('property', 'applicant').order_by('-applied_at')[:5]
            context['recent_payments'] = my_payments.select_related('tenant', 'lease').order_by('-created_at')[:5]
            context['recent_maintenance'] = MaintenanceRequest.objects.filter(property__owner=user).select_related('property', 'tenant').order_by('-created_at')[:5]

        else:
            # Tenant Dashboard
            context['dashboard_type'] = 'Tenant'
            active_lease = Lease.objects.filter(tenant=user, status=Lease.LeaseStatus.ACTIVE).select_related('property', 'owner').first()
            my_applications = RentalApplication.objects.filter(applicant=user)
            my_payments = Payment.objects.filter(tenant=user)
            my_maintenance = MaintenanceRequest.objects.filter(tenant=user)

            paid_amount = my_payments.filter(status=Payment.PaymentStatus.PAID).aggregate(Sum('amount'))['amount__sum'] or 0.00
            pending_invoice = my_payments.filter(status=Payment.PaymentStatus.PENDING).first()
            open_tickets = my_maintenance.filter(status__in=[MaintenanceRequest.Status.SUBMITTED, MaintenanceRequest.Status.IN_PROGRESS]).count()

            context['active_lease'] = active_lease
            context['pending_invoice'] = pending_invoice

            context['stats'] = [
                {'label': 'Active Tenancy', 'value': active_lease.property.title if active_lease else 'No active lease', 'icon': 'bi-house-heart', 'color': 'primary'},
                {'label': 'Monthly Rent', 'value': f"${active_lease.monthly_rent:,.2f}" if active_lease else '$0.00', 'icon': 'bi-credit-card', 'color': 'info'},
                {'label': 'Total Rent Paid', 'value': f"${paid_amount:,.2f}", 'icon': 'bi-wallet2', 'color': 'success'},
                {'label': 'Pending Bills', 'value': f"${pending_invoice.amount:,.2f}" if pending_invoice else '$0.00', 'icon': 'bi-hourglass-split', 'color': 'warning'},
                {'label': 'Rental Applications', 'value': my_applications.count(), 'icon': 'bi-file-earmark-person', 'color': 'secondary'},
                {'label': 'Open Repair Tickets', 'value': open_tickets, 'icon': 'bi-tools', 'color': 'danger'},
            ]
            context['recent_applications'] = my_applications.select_related('property').order_by('-applied_at')[:4]
            context['recent_payments'] = my_payments.select_related('lease').order_by('-created_at')[:4]
            context['recent_maintenance'] = my_maintenance.select_related('property').order_by('-created_at')[:4]

        return context
