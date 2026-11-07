from django.urls import path
from .views import (
    MaintenanceListView, MaintenanceCreateView,
    MaintenanceDetailView, MaintenanceUpdateView
)

app_name = 'maintenance'

urlpatterns = [
    path('', MaintenanceListView.as_view(), name='list'),
    path('create/', MaintenanceCreateView.as_view(), name='create'),
    path('<int:pk>/', MaintenanceDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', MaintenanceUpdateView.as_view(), name='update'),
]
