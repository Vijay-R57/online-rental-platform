from django.urls import path
from .views import (
    ApplyRentalView, TenantApplicationListView, PropertyApplicationsListView,
    OwnerAllApplicationsListView, ApplicationReviewView, BookingListView,
    LeaseListView, LeaseDetailView, LeaseSignView
)

app_name = 'rentals'

urlpatterns = [
    path('apply/<int:property_id>/', ApplyRentalView.as_view(), name='apply'),
    path('my-applications/', TenantApplicationListView.as_view(), name='my_applications'),
    path('property/<int:property_id>/applications/', PropertyApplicationsListView.as_view(), name='property_applications'),
    path('owner/applications/', OwnerAllApplicationsListView.as_view(), name='owner_applications'),
    path('applications/<int:pk>/review/', ApplicationReviewView.as_view(), name='review_application'),
    path('bookings/', BookingListView.as_view(), name='booking_list'),
    path('leases/', LeaseListView.as_view(), name='lease_list'),
    path('leases/<int:pk>/', LeaseDetailView.as_view(), name='lease_detail'),
    path('leases/<int:pk>/sign/', LeaseSignView.as_view(), name='lease_sign'),
]
