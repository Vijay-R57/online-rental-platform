from django.contrib import admin
from .models import Property, PropertyImage, Amenity


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ('image', 'caption', 'is_primary', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_class')
    search_fields = ('name',)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'owner', 'property_type', 'status',
        'city', 'rent_amount', 'bedrooms', 'bathrooms',
        'views_count', 'created_at'
    )
    list_filter = ('property_type', 'status', 'furnished_status', 'pet_friendly', 'city')
    search_fields = ('title', 'address', 'city', 'state', 'postal_code', 'owner__username')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('amenities',)
    inlines = [PropertyImageInline]
    date_hierarchy = 'created_at'


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'caption', 'is_primary', 'uploaded_at')
    list_filter = ('is_primary', 'uploaded_at')
    search_fields = ('property__title', 'caption')
