from django.contrib import admin
from .models import Listing, SellerReview

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'hobby', 'listing_type', 'status', 'price', 'created_at')
    list_filter = ('status', 'listing_type', 'hobby')
    search_fields = ('title', 'description', 'seller__username')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(SellerReview)
class SellerReviewAdmin(admin.ModelAdmin):
    list_display = ('seller', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('seller__username', 'reviewer__username', 'comment')
