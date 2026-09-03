from django import forms
from .models import Article, ArticleComment, ArticleRating
from profiles.models import Hobby
from django.utils.text import slugify

class ArticleForm(forms.ModelForm):
    custom_hobby = forms.CharField(
        max_length=100, 
        required=False, 
        label="O añade una nueva terapia",
        help_text="Si tu terapia no está en la lista, escríbela aquí."
    )
    
    class Meta:
        model = Article
        fields = [
            'title', 'hobby', 'custom_hobby', 'content', 
            'cover_image', 'attached_video', 'attached_document', 
            'external_video_url', 'external_document_url'
        ]
        widgets = {
            'content': forms.Textarea(attrs={'id': 'tinymce-editor'}),
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields['hobby'].required = False
        if not (self.user and (self.user.is_staff or self.user.is_superuser)):
            self.fields['hobby'].queryset = self.fields['hobby'].queryset.exclude(slug="agora")
        
    def clean(self):
        cleaned_data = super().clean()
        hobby = cleaned_data.get('hobby')
        custom_hobby = cleaned_data.get('custom_hobby')
        
        if not (self.user and (self.user.is_staff or self.user.is_superuser)):
            if hobby and hobby.slug == "agora":
                raise forms.ValidationError(
                    "Solo la dirección y administración (staff) pueden publicar bajo la categoría Ágora."
                )
            if custom_hobby and slugify(custom_hobby) == "agora":
                raise forms.ValidationError(
                    "Solo la dirección y administración (staff) pueden crear publicaciones bajo el nombre Ágora."
                )

        if not hobby and not custom_hobby:
            raise forms.ValidationError("Debes seleccionar una terapia existente o escribir una nueva.")
            
        return cleaned_data
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        custom_hobby = self.cleaned_data.get('custom_hobby')
        
        # En vez de "not instance.hobby" que tira RelatedObjectDoesNotExist
        if getattr(instance, 'hobby_id', None) is None and custom_hobby:
            # Create the hobby
            slug = slugify(custom_hobby)
            hobby, created = Hobby.objects.get_or_create(
                slug=slug, 
                defaults={'name': custom_hobby, 'description': 'Creada automáticamente desde biblioteca.'}
            )
            instance.hobby = hobby
            
        if commit:
            instance.save()
        return instance

class ArticleCommentForm(forms.ModelForm):
    class Meta:
        model = ArticleComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe tu comentario...', 'class': 'form-control'}),
        }

class ArticleRatingForm(forms.ModelForm):
    class Meta:
        model = ArticleRating
        fields = ['rating']
