from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Listing, SellerReview
from .forms import ListingForm, SellerReviewForm
from django.contrib.auth.models import User
from profiles.models import Hobby
from django.db.models import Avg

class ListingListView(LoginRequiredMixin, ListView):
    model = Listing
    template_name = 'marketplace/listing_list.html'
    context_object_name = 'listings'
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset().select_related('seller', 'hobby')
        
        # Filtros
        query = self.request.GET.get('q')
        listing_type = self.request.GET.get('type')
        hobby_id = self.request.GET.get('hobby')
        status = self.request.GET.get('status', 'AVAILABLE')
        
        seller_filter = self.request.GET.get('seller')
        
        if status and status != 'ALL':
            qs = qs.filter(status=status)
            
        if seller_filter == 'me':
            qs = qs.filter(seller=self.request.user)
            
        if query:
            qs = qs.filter(title__icontains=query)
        if listing_type:
            qs = qs.filter(listing_type=listing_type)
        if hobby_id:
            qs = qs.filter(hobby_id=hobby_id)
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hobbies'] = Hobby.objects.all()
        context['listing_types'] = Listing.LISTING_TYPES
        return context

class ListingDetailView(LoginRequiredMixin, DetailView):
    model = Listing
    template_name = 'marketplace/listing_detail.html'
    context_object_name = 'listing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller = self.object.seller
        reviews = seller.seller_reviews.all()
        context['reviews'] = reviews
        context['avg_rating'] = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        context['review_form'] = SellerReviewForm()
        context['has_reviewed'] = reviews.filter(reviewer=self.request.user).exists()
        return context

class ListingCreateView(LoginRequiredMixin, CreateView):
    model = Listing
    form_class = ListingForm
    template_name = 'marketplace/listing_form.html'
    
    def form_valid(self, form):
        form.instance.seller = self.request.user
        messages.success(self.request, "Tu anuncio ha sido publicado exitosamente.")
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse('marketplace:listing_detail', kwargs={'slug': self.object.slug})

class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Listing
    form_class = ListingForm
    template_name = 'marketplace/listing_form.html'

    def form_valid(self, form):
        messages.success(self.request, "Anuncio actualizado correctamente.")
        return super().form_valid(form)

    def test_func(self):
        listing = self.get_object()
        return self.request.user == listing.seller

    def get_success_url(self):
        return reverse('marketplace:listing_detail', kwargs={'slug': self.object.slug})

class ListingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Listing
    template_name = 'marketplace/listing_confirm_delete.html'
    success_url = reverse_lazy('marketplace:listing_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Anuncio eliminado definitivamente.")
        return super().delete(request, *args, **kwargs)

    def test_func(self):
        listing = self.get_object()
        return self.request.user == listing.seller

@login_required
def add_seller_review(request, username):
    seller = get_object_or_404(User, username=username)
    
    if request.user == seller:
        messages.error(request, "No puedes valorarte a ti mismo.")
        return redirect('marketplace:listing_list')
        
    if request.method == 'POST':
        form = SellerReviewForm(request.POST)
        if form.is_valid():
            review, created = SellerReview.objects.update_or_create(
                seller=seller,
                reviewer=request.user,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'comment': form.cleaned_data['comment']
                }
            )
            if created:
                messages.success(request, f"Has valorado a {seller.username} con éxito.")
            else:
                messages.success(request, f"Has actualizado tu valoración para {seller.username}.")
                
            # Redirigir a donde venía (probablemente detail view de un listing)
            next_url = request.POST.get('next', reverse('marketplace:listing_list'))
            return redirect(next_url)
    
    return redirect('marketplace:listing_list')
