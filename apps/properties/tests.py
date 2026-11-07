from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import CustomUser
from .models import Property, Amenity


class PropertyModelAndViewsTests(TestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            username='testowner',
            password='Password123!',
            role=CustomUser.Role.OWNER
        )
        self.amenity = Amenity.objects.create(name='Wi-Fi', icon_class='bi-wifi')
        self.property = Property.objects.create(
            owner=self.owner,
            title='Sunset Coastal Apartment',
            property_type=Property.PropertyType.APARTMENT,
            status=Property.PropertyStatus.AVAILABLE,
            address='100 Ocean Drive',
            city='San Francisco',
            state='CA',
            postal_code='94101',
            rent_amount=2800.00,
            security_deposit=2800.00,
            bedrooms=2,
            bathrooms=2.0,
            area_sqft=1100
        )
        self.property.amenities.add(self.amenity)

    def test_property_creation_and_slug(self):
        self.assertTrue(self.property.slug.startswith('sunset-coastal-apartment'))
        self.assertTrue(self.property.is_available)
        self.assertEqual(str(self.property), "Sunset Coastal Apartment - $2800.00/mo (San Francisco)")

    def test_property_list_view_and_filtering(self):
        response = self.client.get(reverse('properties:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sunset Coastal Apartment')

        # Filter by city
        response_filtered = self.client.get(reverse('properties:list') + '?location=San Francisco')
        self.assertEqual(response_filtered.status_code, 200)
        self.assertContains(response_filtered, 'Sunset Coastal Apartment')

        # Filter out with different city
        response_empty = self.client.get(reverse('properties:list') + '?location=Miami')
        self.assertEqual(response_empty.status_code, 200)
        self.assertNotContains(response_empty, 'Sunset Coastal Apartment')

    def test_property_detail_view(self):
        response = self.client.get(reverse('properties:detail', kwargs={'slug': self.property.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sunset Coastal Apartment')
        self.assertContains(response, 'Wi-Fi')

