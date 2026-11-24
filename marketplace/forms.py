from django import forms
from .models import Listing, SellerReview

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['hobby', 'title', 'description', 'price', 'listing_type', 'status', 'image', 'video']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if not (self.user and (self.user.is_staff or self.user.is_superuser)):
            self.fields['hobby'].queryset = self.fields['hobby'].queryset.exclude(slug="agora")

    def clean_hobby(self):
        hobby = self.cleaned_data.get("hobby")
        if hobby and hobby.slug == "agora":
            if not (self.user and (self.user.is_staff or self.user.is_superuser)):
                raise forms.ValidationError(
                    "Solo el personal de dirección o administración (staff) puede clasificar anuncios bajo la categoría Ágora."
                )
        return hobby

class SellerReviewForm(forms.ModelForm):
    class Meta:
        model = SellerReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe aquí tu valoración del vendedor...'}),
        }
