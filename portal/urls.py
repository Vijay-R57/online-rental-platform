"""
URL configuration for Online Property Rental and Management Portal.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Customize Admin Site Headers
admin.site.site_header = "Rental Portal Administration"
admin.site.site_title = "Rental Portal Admin"
admin.site.index_title = "Property Rental & Management System"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('properties/', include('apps.properties.urls', namespace='properties')),
    path('rentals/', include('apps.rentals.urls', namespace='rentals')),
    path('payments/', include('apps.payments.urls', namespace='payments')),
    path('maintenance/', include('apps.maintenance.urls', namespace='maintenance')),
    path('', include('apps.core.urls', namespace='core')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

