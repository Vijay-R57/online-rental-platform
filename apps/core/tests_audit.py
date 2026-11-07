from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime
from apps.accounts.models import CustomUser, TenantDocument
from apps.properties.models import Property
from apps.rentals.models import RentalApplication, Booking, Lease
from apps.payments.models import Payment
from apps.maintenance.models import MaintenanceRequest


class SecurityAndBusinessLogicAuditTests(TestCase):
    def setUp(self):
        # 1. Users
        self.admin = CustomUser.objects.create_superuser('audit_admin', 'admin@test.com', 'Pass123!', role=CustomUser.Role.ADMIN)
        self.owner1 = CustomUser.objects.create_user('audit_owner1', 'owner1@test.com', 'Pass123!', role=CustomUser.Role.OWNER)
        self.owner2 = CustomUser.objects.create_user('audit_owner2', 'owner2@test.com', 'Pass123!', role=CustomUser.Role.OWNER)
        self.tenant1 = CustomUser.objects.create_user('audit_tenant1', 'tenant1@test.com', 'Pass123!', role=CustomUser.Role.TENANT)
        self.tenant2 = CustomUser.objects.create_user('audit_tenant2', 'tenant2@test.com', 'Pass123!', role=CustomUser.Role.TENANT)

        # 2. Properties
        self.prop1 = Property.objects.create(
            owner=self.owner1,
            title='Audit Property 1',
            status=Property.PropertyStatus.AVAILABLE,
            address='123 Audit Way',
            city='Boston',
            state='MA',
            postal_code='02108',
            rent_amount=2500.00,
            security_deposit=2500.00,
            area_sqft=1000
        )

        # 3. Tenant 1 document
        dummy_file = SimpleUploadedFile("id_proof.txt", b"Govt Photo ID Content", content_type="text/plain")
        self.doc1 = TenantDocument.objects.create(
            user=self.tenant1,
            title="Passport ID",
            document_type=TenantDocument.DocumentType.GOVERNMENT_ID,
            document_file=dummy_file
        )

    def test_tenant_document_access_control(self):
        # Unrelated tenant2 should receive 403 Forbidden
        self.client.login(username='audit_tenant2', password='Pass123!')
        res_forbidden = self.client.get(reverse('accounts:document_download', kwargs={'pk': self.doc1.pk}))
        self.assertEqual(res_forbidden.status_code, 403)

        # Document owner (tenant1) should receive 200 OK
        self.client.login(username='audit_tenant1', password='Pass123!')
        res_owner = self.client.get(reverse('accounts:document_download', kwargs={'pk': self.doc1.pk}))
        self.assertEqual(res_owner.status_code, 200)

        # Admin should receive 200 OK
        self.client.login(username='audit_admin', password='Pass123!')
        res_admin = self.client.get(reverse('accounts:document_download', kwargs={'pk': self.doc1.pk}))
        self.assertEqual(res_admin.status_code, 200)

    def test_concurrent_application_approval_protection(self):
        # Two tenants apply for the same available property
        app1 = RentalApplication.objects.create(
            property=self.prop1, applicant=self.tenant1,
            employment_status='Engineer', annual_income=120000.00,
            proposed_move_in=timezone.now().date(), lease_term_months=12
        )
        app2 = RentalApplication.objects.create(
            property=self.prop1, applicant=self.tenant2,
            employment_status='Accountant', annual_income=110000.00,
            proposed_move_in=timezone.now().date(), lease_term_months=12
        )

        # Owner approves application 1
        self.client.login(username='audit_owner1', password='Pass123!')
        review_url1 = reverse('rentals:review_application', kwargs={'pk': app1.pk})
        res1 = self.client.post(review_url1, {'status': RentalApplication.ApplicationStatus.APPROVED})
        self.assertEqual(res1.status_code, 302)

        # Verify property is now RENTED
        self.prop1.refresh_from_db()
        self.assertEqual(self.prop1.status, Property.PropertyStatus.RENTED)

        # Competing application 2 should be automatically closed / rejected
        app2.refresh_from_db()
        self.assertEqual(app2.status, RentalApplication.ApplicationStatus.REJECTED)

        # Attempting to approve application 2 anyway should be rejected
        review_url2 = reverse('rentals:review_application', kwargs={'pk': app2.pk})
        res2 = self.client.post(review_url2, {'status': RentalApplication.ApplicationStatus.APPROVED})
        self.assertEqual(res2.status_code, 302)
        app2.refresh_from_db()
        self.assertNotEqual(app2.status, RentalApplication.ApplicationStatus.APPROVED)

    def test_duplicate_payment_and_idempotency_protection(self):
        # Setup active lease
        booking = Booking.objects.create(
            property=self.prop1, tenant=self.tenant1,
            check_in=timezone.now().date(), deposit_amount=2500.00
        )
        lease = Lease.objects.create(
            booking=booking, property=self.prop1, owner=self.owner1, tenant=self.tenant1,
            start_date=timezone.now().date(), end_date=timezone.now().date() + datetime.timedelta(days=365),
            monthly_rent=2500.00, security_deposit=2500.00, status=Lease.LeaseStatus.ACTIVE
        )
        payment = Payment.objects.create(
            lease=lease, tenant=self.tenant1, amount=2500.00,
            payment_type=Payment.PaymentType.RENT, description='November Rent',
            status=Payment.PaymentStatus.PENDING
        )

        self.client.login(username='audit_tenant1', password='Pass123!')
        checkout_url = reverse('payments:checkout', kwargs={'payment_id': payment.id})

        # First checkout attempt -> succeeds
        res1 = self.client.post(checkout_url, {'payment_method': 'CARD', 'card_number': '4242-4242-4242-4242'})
        self.assertEqual(res1.status_code, 302)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.PaymentStatus.PAID)

        # Duplicate checkout attempt on already settled invoice -> redirects safely without double billing
        res2 = self.client.post(checkout_url, {'payment_method': 'CARD', 'card_number': '4242-4242-4242-4242'})
        self.assertEqual(res2.status_code, 302)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.PaymentStatus.PAID)

    def test_cross_tenant_maintenance_ticket_isolation(self):
        # tenant2 has NO lease on prop1, attempts to submit a ticket
        self.client.login(username='audit_tenant2', password='Pass123!')
        create_url = reverse('maintenance:create')
        res = self.client.post(create_url, {
            'property': self.prop1.id,
            'title': 'Unauthorized repair ticket',
            'category': MaintenanceRequest.Category.PLUMBING,
            'priority': MaintenanceRequest.Priority.HIGH,
            'description': 'Water leaking in unit'
        })
        # Should fail form validation with error
        self.assertEqual(res.status_code, 200) # Re-renders form with error
        self.assertFalse(MaintenanceRequest.objects.filter(title='Unauthorized repair ticket').exists())

    def test_terminated_lease_signing_barrier(self):
        booking = Booking.objects.create(
            property=self.prop1, tenant=self.tenant1, check_in=timezone.now().date()
        )
        lease = Lease.objects.create(
            booking=booking, property=self.prop1, owner=self.owner1, tenant=self.tenant1,
            start_date=timezone.now().date(), end_date=timezone.now().date() + datetime.timedelta(days=365),
            monthly_rent=2500.00, security_deposit=2500.00, status=Lease.LeaseStatus.TERMINATED
        )
        self.client.login(username='audit_tenant1', password='Pass123!')
        res = self.client.post(reverse('rentals:lease_sign', kwargs={'pk': lease.pk}))
        self.assertEqual(res.status_code, 302)
        lease.refresh_from_db()
        self.assertFalse(lease.signed_by_tenant)

