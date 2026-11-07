from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class CustomUserModelTests(TestCase):
    def test_create_tenant_user(self):
        user = User.objects.create_user(
            username='testtenant',
            email='tenant@test.com',
            password='password123',
            role=User.Role.TENANT,
            phone_number='1234567890'
        )
        self.assertEqual(user.role, User.Role.TENANT)
        self.assertTrue(user.is_tenant_role)
        self.assertFalse(user.is_owner_role)
        self.assertFalse(user.is_admin_role)
        self.assertEqual(str(user), "testtenant - Tenant")

    def test_create_owner_user(self):
        user = User.objects.create_user(
            username='testowner',
            email='owner@test.com',
            password='password123',
            role=User.Role.OWNER,
            first_name='Bob',
            last_name='Builder'
        )
        self.assertEqual(user.role, User.Role.OWNER)
        self.assertTrue(user.is_owner_role)
        self.assertFalse(user.is_tenant_role)
        self.assertFalse(user.is_admin_role)
        self.assertEqual(str(user), "Bob Builder (testowner) - Property Owner")

    def test_create_admin_superuser(self):
        admin = User.objects.create_superuser(
            username='superadmin',
            email='admin@test.com',
            password='password123',
            role=User.Role.ADMIN
        )
        self.assertEqual(admin.role, User.Role.ADMIN)
        self.assertTrue(admin.is_admin_role)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)

    def test_superuser_auto_admin_role(self):
        # Even if default role is passed, superuser should save as ADMIN
        admin = User.objects.create_superuser(
            username='superadmin2',
            email='admin2@test.com',
            password='password123',
            role=User.Role.TENANT
        )
        self.assertEqual(admin.role, User.Role.ADMIN)
        self.assertTrue(admin.is_admin_role)


class AccountsViewsTests(TestCase):
    def test_login_page_renders(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_register_page_renders(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

