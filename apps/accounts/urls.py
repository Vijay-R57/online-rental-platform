from django.urls import path
from .views import (
    RegisterView, UserLoginView, UserLogoutView, ProfileView,
    ProfileEditView, TenantDocumentListView, TenantDocumentUploadView,
    TenantDocumentDeleteView, TenantDocumentDownloadView
)

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('documents/', TenantDocumentListView.as_view(), name='documents'),
    path('documents/upload/', TenantDocumentUploadView.as_view(), name='document_upload'),
    path('documents/<int:pk>/download/', TenantDocumentDownloadView.as_view(), name='document_download'),
    path('documents/<int:pk>/delete/', TenantDocumentDeleteView.as_view(), name='document_delete'),
]
