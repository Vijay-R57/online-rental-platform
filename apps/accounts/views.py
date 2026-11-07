from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView, ListView, DeleteView
from .forms import CustomUserCreationForm, UserProfileUpdateForm, TenantDocumentUploadForm
from .models import CustomUser, TenantDocument


class RegisterView(CreateView):
    """Public user registration view with role selection."""
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('dashboard:index')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        role_label = user.get_role_display()
        messages.success(
            self.request,
            f"Welcome to the Rental Portal, {user.username}! Your {role_label} account has been created."
        )
        return redirect(self.success_url)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)


class UserLoginView(LoginView):
    """User authentication view with role-aware redirection."""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard:index')

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().username}!")
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    """User logout view."""
    next_page = reverse_lazy('core:home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You have been logged out successfully.")
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile overview."""
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_tenant_role:
            context['documents'] = self.request.user.documents.all()
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit user profile details and avatar."""
    model = CustomUser
    form_class = UserProfileUpdateForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your profile details have been updated successfully.")
        return super().form_valid(form)


class TenantDocumentUploadView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Allows tenants to upload identification and lease verification documents."""
    model = TenantDocument
    form_class = TenantDocumentUploadForm
    template_name = 'accounts/document_upload.html'
    success_url = reverse_lazy('accounts:documents')

    def test_func(self):
        return self.request.user.is_tenant_role or self.request.user.is_admin_role

    def form_valid(self, form):
        document = form.save(commit=False)
        document.user = self.request.user
        document.save()
        messages.success(self.request, f"Document '{document.title}' uploaded successfully.")
        return redirect(self.success_url)


class TenantDocumentListView(LoginRequiredMixin, ListView):
    """Lists uploaded documents for the authenticated tenant."""
    model = TenantDocument
    template_name = 'accounts/document_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        if self.request.user.is_admin_role:
            return TenantDocument.objects.all().select_related('user')
        return TenantDocument.objects.filter(user=self.request.user)


class TenantDocumentDeleteView(LoginRequiredMixin, DeleteView):
    """Allows a tenant to delete their own uploaded document."""
    model = TenantDocument
    success_url = reverse_lazy('accounts:documents')

    def get_queryset(self):
        if self.request.user.is_admin_role:
            return TenantDocument.objects.all()
        return TenantDocument.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Document was successfully deleted.")
        return super().form_valid(form)


class TenantDocumentDownloadView(LoginRequiredMixin, View):
    """
    Secure document access endpoint.
    Permits access ONLY to:
    1. The tenant who owns the document.
    2. An administrator.
    3. A property owner reviewing an application or active lease for this tenant.
    All other unauthorized users receive 403 Forbidden.
    """
    def get(self, request, pk):
        doc = get_object_or_404(TenantDocument, pk=pk)
        user = request.user

        is_owner = (doc.user == user)
        is_admin = user.is_admin_role
        is_landlord_evaluating = False

        if not (is_owner or is_admin):
            from apps.rentals.models import RentalApplication, Lease
            has_app = RentalApplication.objects.filter(property__owner=user, applicant=doc.user).exists()
            has_lease = Lease.objects.filter(owner=user, tenant=doc.user).exists()
            is_landlord_evaluating = has_app or has_lease

        if not (is_owner or is_admin or is_landlord_evaluating):
            return HttpResponseForbidden("Access Denied: You do not have permission to view or download this verification document.")

        if not doc.document_file:
            raise Http404("Document file not found.")

        return FileResponse(doc.document_file.open('rb'))
