from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, TenantDocument
from .forms import CustomUserCreationForm, CustomUserChangeForm


class TenantDocumentInline(admin.TabularInline):
    model = TenantDocument
    extra = 0
    fields = ('document_type', 'title', 'document_file', 'is_verified', 'verification_notes', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for CustomUser model.
    Includes custom fields (role, phone_number, profile_picture, is_verified, bio, etc.).
    """
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = CustomUser
    inlines = [TenantDocumentInline]

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_verified',
        'phone_number',
        'is_staff',
        'is_active',
        'date_joined',
    )
    list_filter = (
        'role',
        'is_verified',
        'is_staff',
        'is_superuser',
        'is_active',
        'date_joined',
    )
    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
        'phone_number',
        'city',
        'company_name',
    )
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name', 'last_name', 'email', 'phone_number',
                'profile_picture', 'bio'
            )
        }),
        (_('Location & Address'), {
            'fields': ('address', 'city', 'state', 'postal_code')
        }),
        (_('Employment & Emergency Contact'), {
            'fields': (
                'occupation', 'company_name',
                'emergency_contact_name', 'emergency_contact_phone'
            )
        }),
        (_('Portal Role & Verification'), {'fields': ('role', 'is_verified')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'first_name',
                'last_name',
                'role',
                'phone_number',
                'password1',
                'password2',
                'is_verified',
                'is_staff',
                'is_active',
            ),
        }),
    )


@admin.register(TenantDocument)
class TenantDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'document_type', 'is_verified', 'uploaded_at')
    list_filter = ('document_type', 'is_verified', 'uploaded_at')
    search_fields = ('title', 'user__username', 'user__email', 'verification_notes')
    list_editable = ('is_verified',)
