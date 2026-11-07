from django.test import TestCase
from django.urls import reverse


class CoreViewsTests(TestCase):
    def test_landing_page_renders_successfully(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertTemplateUsed(response, 'base.html')
        self.assertContains(response, 'RentEase')
        self.assertContains(response, 'Featured Rental Properties')
        self.assertContains(response, 'Search Available Rentals')

    def test_about_page_renders_successfully(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/about.html')

