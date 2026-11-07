from django.urls import path
from .views import (
    PropertyListView, PropertyDetailView, OwnerPropertyListView,
    PropertyCreateView, PropertyUpdateView, PropertyDeleteView,
    PropertyImageUploadView
)

app_name = 'properties'

urlpatterns = [
    path('', PropertyListView.as_view(), name='list'),
    path('my-properties/', OwnerPropertyListView.as_view(), name='owner_list'),
    path('create/', PropertyCreateView.as_view(), name='create'),
    path('<slug:slug>/', PropertyDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', PropertyUpdateView.as_view(), name='update'),
    path('<slug:slug>/delete/', PropertyDeleteView.as_view(), name='delete'),
    path('<int:property_id>/images/upload/', PropertyImageUploadView.as_view(), name='image_upload'),
]
