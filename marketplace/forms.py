from django import forms
from .models import Listing, SellerReview

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['hobby', 'title', 'description', 'price', 'listing_type', 'status', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class SellerReviewForm(forms.ModelForm):
    class Meta:
        model = SellerReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe aquí tu valoración del vendedor...'}),
        }
