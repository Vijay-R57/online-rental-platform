from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
import uuid


class Amenity(models.Model):
    """
    Features and amenities associated with a property (e.g. WiFi, Parking, AC).
    """
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Amenity Name'))
    icon_class = models.CharField(
        max_length=60,
        default='bi-check-circle',
        help_text=_('Bootstrap icon class (e.g. bi-wifi, bi-car-front, bi-snow)'),
        verbose_name=_('Icon Class')
    )

    class Meta:
        verbose_name = _('Amenity')
        verbose_name_plural = _('Amenities')
        ordering = ['name']

    def __str__(self):
        return self.name


class Property(models.Model):
    """
    Real estate rental property listing managed by property owners or portal admin.
    """
    class PropertyType(models.TextChoices):
        APARTMENT = 'APARTMENT', _('Apartment')
        HOUSE = 'HOUSE', _('Single Family House')
        CONDO = 'CONDO', _('Condominium')
        STUDIO = 'STUDIO', _('Studio Loft')
        VILLA = 'VILLA', _('Luxury Villa')
        TOWNHOUSE = 'TOWNHOUSE', _('Townhouse')

    class PropertyStatus(models.TextChoices):
        AVAILABLE = 'AVAILABLE', _('Available for Rent')
        RENTED = 'RENTED', _('Currently Occupied / Rented')
        MAINTENANCE = 'MAINTENANCE', _('Under Maintenance')
        UNLISTED = 'UNLISTED', _('Unlisted / Inactive')

    class FurnishedStatus(models.TextChoices):
        FURNISHED = 'FURNISHED', _('Fully Furnished')
        SEMI_FURNISHED = 'SEMI_FURNISHED', _('Semi-Furnished')
        UNFURNISHED = 'UNFURNISHED', _('Unfurnished')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='properties',
        verbose_name=_('Property Owner')
    )
    title = models.CharField(max_length=220, verbose_name=_('Listing Title'))
    slug = models.SlugField(max_length=260, unique=True, blank=True)
    description = models.TextField(verbose_name=_('Property Description'))

    property_type = models.CharField(
        max_length=30,
        choices=PropertyType.choices,
        default=PropertyType.APARTMENT,
        verbose_name=_('Property Type')
    )
    status = models.CharField(
        max_length=30,
        choices=PropertyStatus.choices,
        default=PropertyStatus.AVAILABLE,
        verbose_name=_('Listing Status')
    )

    # Address & Location
    address = models.CharField(max_length=255, verbose_name=_('Street Address'))
    city = models.CharField(max_length=100, db_index=True, verbose_name=_('City'))
    state = models.CharField(max_length=100, verbose_name=_('State / Province'))
    postal_code = models.CharField(max_length=20, verbose_name=_('Postal / ZIP Code'))

    # Financial details
    rent_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_index=True,
        verbose_name=_('Monthly Rent ($)')
    )
    security_deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Security Deposit ($)')
    )

    # Physical Specifications
    bedrooms = models.PositiveSmallIntegerField(default=1, verbose_name=_('Bedrooms'))
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, default=1.0, verbose_name=_('Bathrooms'))
    area_sqft = models.PositiveIntegerField(verbose_name=_('Area (Sq. Ft.)'))
    furnished_status = models.CharField(
        max_length=30,
        choices=FurnishedStatus.choices,
        default=FurnishedStatus.UNFURNISHED,
        verbose_name=_('Furnishing Status')
    )
    pet_friendly = models.BooleanField(default=False, verbose_name=_('Pet Friendly'))
    available_from = models.DateField(default=timezone.now, verbose_name=_('Available From Date'))

    # Amenities & Media
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='properties', verbose_name=_('Amenities'))
    featured_image = models.ImageField(
        upload_to='properties/featured/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_('Cover / Featured Image')
    )

    views_count = models.PositiveIntegerField(default=0, verbose_name=_('Page Views'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Property')
        verbose_name_plural = _('Properties')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'property'
            unique_suffix = str(uuid.uuid4())[:8]
            self.slug = f"{base_slug}-{unique_suffix}"
        super().save(*args, **kwargs)

    @property
    def is_available(self):
        return self.status == self.PropertyStatus.AVAILABLE

    @property
    def primary_image_url(self):
        if self.featured_image:
            return self.featured_image.url
        first_gallery_img = self.images.first()
        if first_gallery_img and first_gallery_img.image:
            return first_gallery_img.image.url
        return 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80'

    def __str__(self):
        return f"{self.title} - ${self.rent_amount:.2f}/mo ({self.city})"


class PropertyImage(models.Model):
    """
    Multiple property gallery images.
    """
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Property')
    )
    image = models.ImageField(upload_to='properties/gallery/%Y/%m/', verbose_name=_('Image File'))
    caption = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('Caption'))
    is_primary = models.BooleanField(default=False, verbose_name=_('Set as Primary Image'))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Uploaded At'))

    class Meta:
        verbose_name = _('Property Image')
        verbose_name_plural = _('Property Images')
        ordering = ['-is_primary', '-uploaded_at']

    def __str__(self):
        return f"Image for {self.property.title}"
