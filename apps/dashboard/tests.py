from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import CustomUser


class DashboardViewsTests(TestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_superuser(
            username='dash_admin', password='Password123!', role=CustomUser.Role.ADMIN
        )
        self.owner_user = CustomUser.objects.create_user(
            username='dash_owner', password='Password123!', role=CustomUser.Role.OWNER
        )
        self.tenant_user = CustomUser.objects.create_user(
            username='dash_tenant', password='Password123!', role=CustomUser.Role.TENANT
        )

    def test_admin_dashboard(self):
        self.client.login(username='dash_admin', password='Password123!')
        res = self.client.get(reverse('dashboard:index'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Administrator')
        self.assertContains(res, 'Django Admin')

    def test_owner_dashboard(self):
        self.client.login(username='dash_owner', password='Password123!')
        res = self.client.get(reverse('dashboard:index'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Property Owner')
        self.assertContains(res, 'My Properties')

    def test_tenant_dashboard(self):
        self.client.login(username='dash_tenant', password='Password123!')
        res = self.client.get(reverse('dashboard:index'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Tenant')

