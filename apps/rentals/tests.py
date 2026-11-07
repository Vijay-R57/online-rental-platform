from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
import datetime
from apps.accounts.models import CustomUser
from apps.properties.models import Property
from .models import RentalApplication, Booking, Lease


class RentalWorkflowTests(TestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            username='owner_mike',
            password='Password123!',
            role=CustomUser.Role.OWNER
        )
        self.tenant = CustomUser.objects.create_user(
            username='tenant_jenny',
            password='Password123!',
            role=CustomUser.Role.TENANT
        )
        self.property = Property.objects.create(
            owner=self.owner,
            title='Highland Garden Flat',
            property_type=Property.PropertyType.APARTMENT,
            status=Property.PropertyStatus.AVAILABLE,
            address='200 Highland Ave',
            city='Seattle',
            state='WA',
            postal_code='98101',
            rent_amount=2200.00,
            security_deposit=2200.00,
            bedrooms=2,
            bathrooms=1.0,
            area_sqft=950
        )

    def test_tenant_apply_and_owner_approval(self):
        self.client.login(username='tenant_jenny', password='Password123!')

        # Apply for property
        apply_url = reverse('rentals:apply', kwargs={'property_id': self.property.id})
        response = self.client.post(apply_url, {
            'employment_status': 'Consultant',
            'annual_income': 95000.00,
            'credit_score_range': 'GOOD',
            'occupants_count': 1,
            'proposed_move_in': timezone.now().date() + datetime.timedelta(days=7),
            'lease_term_months': 12,
            'message_to_landlord': 'Looking forward to moving in.'
        })
        self.assertEqual(response.status_code, 302)

        application = RentalApplication.objects.get(property=self.property, applicant=self.tenant)
        self.assertEqual(application.status, RentalApplication.ApplicationStatus.PENDING)

        # Owner login and approve
        self.client.login(username='owner_mike', password='Password123!')
        review_url = reverse('rentals:review_application', kwargs={'pk': application.id})
        review_response = self.client.post(review_url, {
            'status': RentalApplication.ApplicationStatus.APPROVED,
            'owner_notes': 'Application accepted!'
        })
        self.assertEqual(review_response.status_code, 302)

        application.refresh_from_db()
        self.assertEqual(application.status, RentalApplication.ApplicationStatus.APPROVED)

        # Verify automated booking and lease creation
        self.assertTrue(Booking.objects.filter(application=application).exists())
        self.assertTrue(Lease.objects.filter(tenant=self.tenant, property=self.property).exists())

        # Property status should be updated to RENTED
        self.property.refresh_from_db()
        self.assertEqual(self.property.status, Property.PropertyStatus.RENTED)

