from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
import datetime
from apps.accounts.models import CustomUser
from apps.properties.models import Property
from apps.rentals.models import Booking, Lease
from .models import Payment


class PaymentCheckoutTests(TestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(username='own1', password='Password123!', role=CustomUser.Role.OWNER)
        self.tenant = CustomUser.objects.create_user(username='ten1', password='Password123!', role=CustomUser.Role.TENANT)
        self.property = Property.objects.create(
            owner=self.owner, title='Sample House', address='1 St', city='Austin', state='TX', postal_code='78701',
            rent_amount=1800.00, security_deposit=1800.00, area_sqft=900
        )
        self.booking = Booking.objects.create(
            property=self.property, tenant=self.tenant, check_in=timezone.now().date(), deposit_amount=1800.00
        )
        self.lease = Lease.objects.create(
            booking=self.booking, property=self.property, owner=self.owner, tenant=self.tenant,
            start_date=timezone.now().date(), end_date=timezone.now().date() + datetime.timedelta(days=365),
            monthly_rent=1800.00, security_deposit=1800.00, status=Lease.LeaseStatus.ACTIVE
        )
        self.payment = Payment.objects.create(
            lease=self.lease, tenant=self.tenant, amount=1800.00,
            payment_type=Payment.PaymentType.RENT, description='Current Month Rent', status=Payment.PaymentStatus.PENDING
        )

    def test_simulated_checkout_processing(self):
        self.client.login(username='ten1', password='Password123!')
        checkout_url = reverse('payments:checkout', kwargs={'payment_id': self.payment.id})

        response = self.client.post(checkout_url, {
            'payment_method': 'CARD',
            'card_number': '4242 4242 4242 4242',
            'card_expiry': '12/28',
            'card_cvv': '123'
        })
        self.assertEqual(response.status_code, 302)

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.PaymentStatus.PAID)
        self.assertIsNotNone(self.payment.paid_at)

        # Verify receipt page renders
        receipt_url = reverse('payments:receipt', kwargs={'pk': self.payment.id})
        receipt_res = self.client.get(receipt_url)
        self.assertEqual(receipt_res.status_code, 200)
        self.assertContains(receipt_res, 'Official Payment Receipt')

