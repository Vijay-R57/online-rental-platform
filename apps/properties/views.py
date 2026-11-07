from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Property, PropertyImage, Amenity
from .forms import PropertyForm, PropertyImageForm


class PropertyListView(ListView):
    """
    Public and tenant property search, filter, and catalog browsing view.
    """
    model = Property
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'
    paginate_by = 6

    def get_queryset(self):
        queryset = Property.objects.filter(status=Property.PropertyStatus.AVAILABLE).select_related('owner').prefetch_related('images', 'amenities')

        # Location / Keyword search
        query = self.request.GET.get('q', '').strip() or self.request.GET.get('location', '').strip()
        if query:
            queryset = queryset.filter(
                Q(city__icontains=query) |
                Q(title__icontains=query) |
                Q(address__icontains=query) |
                Q(state__icontains=query)
            )

        # Property Type filter
        prop_type = self.request.GET.get('property_type') or self.request.GET.get('type')
        if prop_type:
            queryset = queryset.filter(property_type__iexact=prop_type)

        # Minimum Rent filter
        min_rent = self.request.GET.get('min_rent')
        if min_rent and min_rent.isdigit():
            queryset = queryset.filter(rent_amount__gte=float(min_rent))

        # Maximum Rent filter
        max_rent = self.request.GET.get('max_rent') or self.request.GET.get('max_price')
        if max_rent and max_rent.isdigit():
            queryset = queryset.filter(rent_amount__lte=float(max_rent))

        # Bedrooms filter
        bedrooms = self.request.GET.get('bedrooms')
        if bedrooms and bedrooms.isdigit():
            queryset = queryset.filter(bedrooms__gte=int(bedrooms))

        # Furnished Status filter
        furnished = self.request.GET.get('furnished_status')
        if furnished:
            queryset = queryset.filter(furnished_status=furnished)

        # Pet friendly
        if self.request.GET.get('pet_friendly') in ['true', '1', 'on']:
            queryset = queryset.filter(pet_friendly=True)

        # Sorting
        sort = self.request.GET.get('sort', 'newest')
        if sort == 'price_asc':
            queryset = queryset.order_by('rent_amount')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-rent_amount')
        elif sort == 'bedrooms':
            queryset = queryset.order_by('-bedrooms')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_amenities'] = Amenity.objects.all()
        context['property_types'] = Property.PropertyType.choices
        context['total_count'] = self.get_queryset().count()
        context['search_location'] = self.request.GET.get('location', '') or self.request.GET.get('q', '')
        return context


class PropertyDetailView(DetailView):
    """
    Detailed public property view with gallery, amenities list, and application link.
    """
    model = Property
    template_name = 'properties/property_detail.html'
    context_object_name = 'property'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        # Increment view count
        Property.objects.filter(pk=obj.pk).update(views_count=obj.views_count + 1)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gallery_images'] = self.object.images.all()
        context['property_amenities'] = self.object.amenities.all()
        # Similar listings in the same city
        context['similar_properties'] = Property.objects.filter(
            city__iexact=self.object.city,
            status=Property.PropertyStatus.AVAILABLE
        ).exclude(pk=self.object.pk)[:3]
        return context


class OwnerPropertyListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    List properties owned by the authenticated Landlord / Property Owner.
    """
    model = Property
    template_name = 'properties/owner_property_list.html'
    context_object_name = 'properties'
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_owner_role or self.request.user.is_admin_role

    def get_queryset(self):
        if self.request.user.is_admin_role:
            return Property.objects.all().select_related('owner').order_by('-created_at')
        return Property.objects.filter(owner=self.request.user).order_by('-created_at')


class PropertyCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Allows property owners to list a new rental property.
    """
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'

    def test_func(self):
        return self.request.user.is_owner_role or self.request.user.is_admin_role

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, f"Property '{form.instance.title}' has been listed successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('properties:owner_list')


class PropertyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Allows property owners to edit their own rental property.
    """
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'

    def test_func(self):
        property_obj = self.get_object()
        return property_obj.owner == self.request.user or self.request.user.is_admin_role

    def form_valid(self, form):
        messages.success(self.request, f"Property '{form.instance.title}' updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('properties:owner_list')


class PropertyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Allows property owners to remove a property listing.
    """
    model = Property
    template_name = 'properties/property_confirm_delete.html'
    success_url = reverse_lazy('properties:owner_list')

    def test_func(self):
        property_obj = self.get_object()
        return property_obj.owner == self.request.user or self.request.user.is_admin_role

    def form_valid(self, form):
        messages.success(self.request, "Property listing was successfully deleted.")
        return super().form_valid(form)


class PropertyImageUploadView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Allows property owners to add photos to their property gallery.
    """
    model = PropertyImage
    form_class = PropertyImageForm
    template_name = 'properties/property_image_upload.html'

    def test_func(self):
        property_obj = get_object_or_404(Property, pk=self.kwargs['property_id'])
        return property_obj.owner == self.request.user or self.request.user.is_admin_role

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['property'] = get_object_or_404(Property, pk=self.kwargs['property_id'])
        return context

    def form_valid(self, form):
        property_obj = get_object_or_404(Property, pk=self.kwargs['property_id'])
        form.instance.property = property_obj
        messages.success(self.request, "Image added to property gallery.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('properties:detail', kwargs={'slug': self.object.property.slug})
