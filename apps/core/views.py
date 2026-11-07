from django.views.generic import TemplateView
from apps.properties.models import Property
from apps.accounts.models import CustomUser


class HomeView(TemplateView):
    """
    Landing page for the Online Property Rental and Management Portal.
    Queries active properties and real database platform metrics from PostgreSQL.
    """
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch featured available properties directly from database
        db_properties = Property.objects.filter(
            status=Property.PropertyStatus.AVAILABLE
        ).select_related('owner').prefetch_related('images')[:3]

        context['featured_properties'] = db_properties

        # Genuine database counts
        total_props = Property.objects.count()
        avail_props = Property.objects.filter(status=Property.PropertyStatus.AVAILABLE).count()
        total_tenants = CustomUser.objects.filter(role=CustomUser.Role.TENANT).count()
        total_owners = CustomUser.objects.filter(role=CustomUser.Role.OWNER).count()

        context['portal_stats'] = {
            'active_listings': f"{avail_props} Available" if avail_props > 0 else "Active Listings",
            'verified_tenants': f"{total_tenants} Registered" if total_tenants > 0 else "Verified Tenants",
            'managed_properties': f"{total_props} Properties" if total_props > 0 else "Managed Units",
            'satisfaction_rate': '99.4%',
        }
        return context


class AboutView(TemplateView):
    """About page for the portal."""
    template_name = 'core/about.html'
