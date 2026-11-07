from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
import datetime
from apps.accounts.models import CustomUser
from apps.properties.models import Property
from apps.rentals.models import Booking, Lease
from .models import MaintenanceRequest


class MaintenanceWorkflowTests(TestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(username='own_maint', password='Password123!', role=CustomUser.Role.OWNER)
        self.tenant = CustomUser.objects.create_user(username='ten_maint', password='Password123!', role=CustomUser.Role.TENANT)
        self.property = Property.objects.create(
            owner=self.owner, title='Urban Condo', address='500 Pine', city='Denver', state='CO', postal_code='80202',
            rent_amount=2100.00, security_deposit=2100.00, area_sqft=850
        )
        self.booking = Booking.objects.create(
            property=self.property, tenant=self.tenant, check_in=timezone.now().date()
        )
        self.lease = Lease.objects.create(
            booking=self.booking, property=self.property, owner=self.owner, tenant=self.tenant,
            start_date=timezone.now().date(), end_date=timezone.now().date() + datetime.timedelta(days=365),
            monthly_rent=2100.00, security_deposit=2100.00, status=Lease.LeaseStatus.ACTIVE
        )

    def test_tenant_create_maintenance_and_owner_update(self):
        self.client.login(username='ten_maint', password='Password123!')
        create_url = reverse('maintenance:create')

        response = self.client.post(create_url, {
            'property': self.property.id,
            'title': 'Washing machine water inlet error',
            'category': MaintenanceRequest.Category.APPLIANCE,
            'priority': MaintenanceRequest.Priority.HIGH,
            'description': 'Error code E4 displayed on the wash cycle.'
        })
        self.assertEqual(response.status_code, 302)

        ticket = MaintenanceRequest.objects.get(tenant=self.tenant, property=self.property)
        self.assertEqual(ticket.status, MaintenanceRequest.Status.SUBMITTED)

        # Landlord updates ticket
        self.client.login(username='own_maint', password='Password123!')
        update_url = reverse('maintenance:update', kwargs={'pk': ticket.id})
        update_response = self.client.post(update_url, {
            'status': MaintenanceRequest.Status.IN_PROGRESS,
            'landlord_response': 'Technician scheduled for Thursday morning.'
        })
        self.assertEqual(update_response.status_code, 302)

        ticket.refresh_from_db()
        self.assertEqual(ticket.status, MaintenanceRequest.Status.IN_PROGRESS)
        self.assertIn('Technician scheduled', ticket.landlord_response)

