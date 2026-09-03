from django import forms
from django.utils import timezone
from .models import Posts, Comment, Event, EventComment


class PostCreateForm(forms.ModelForm):
    # Definimos los campos que necesitan una configuración muy específica fuera del Meta
    caption = forms.CharField(
        label="Descripción",
        required=False,  # En el modelo era opcional, cámbialo a True si quieres obligar
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Cuéntanos más sobre esta publicación...",
            }
        ),
        help_text="Máximo 2000 caracteres.",
    )

    class Meta:
        model = Posts
        # Añadimos 'location', 'external_url' y 'document'
        fields = [
            "title",
            "category",
            "location",
            "caption",
            "image",
            "video",
            "external_url",
            "document",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Dale un título (opcional)",
                }
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "¿Dónde se tomó esto?"}
            ),
            "image": forms.FileInput(
                attrs={
                    "class": "form-control d-none validate-media",
                    "accept": "image/*",
                    "id": "id_image",
                }
            ),
            "video": forms.FileInput(
                attrs={
                    "class": "form-control d-none validate-media",
                    "accept": "video/mp4,video/quicktime,video/x-msvideo,video/webm",
                    "id": "id_video",
                }
            ),
            "external_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://ejemplo.com, enlace a web, vídeo o artículo...",
                    "id": "id_external_url",
                }
            ),
            "document": forms.FileInput(
                attrs={
                    "class": "form-control d-none",
                    "accept": ".pdf,application/pdf",
                    "id": "id_document",
                }
            ),
        }

        error_messages = {
            "category": {
                "required": "Debes elegir una terapia para clasificar tu post.",
            },
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        qs = self.fields["category"].queryset.order_by("name")
        if not (self.user and (self.user.is_staff or self.user.is_superuser)):
            qs = qs.exclude(slug="agora")
        self.fields["category"].queryset = qs
        self.fields["category"].empty_label = "Selecciona o busca una terapia..."

    def clean_category(self):
        category = self.cleaned_data.get("category")
        if category and category.slug == "agora":
            if not (self.user and (self.user.is_staff or self.user.is_superuser)):
                raise forms.ValidationError(
                    "Solo el personal de dirección o administración (staff) puede publicar bajo la categoría Ágora."
                )
        return category

    def clean(self):
        cleaned_data = super().clean()
        caption = cleaned_data.get("caption")
        image = cleaned_data.get("image")
        video = cleaned_data.get("video")
        external_url = cleaned_data.get("external_url")
        document = cleaned_data.get("document")

        if not image and not video and not external_url and not document:
            raise forms.ValidationError(
                "Debes subir una foto, un vídeo, un enlace o un documento PDF para publicar."
            )
        return cleaned_data


class ProfileFollowForm(forms.Form):
    profile_pk = forms.IntegerField(widget=forms.HiddenInput())

    def clean_profile_pk(self):
        profile_pk = self.cleaned_data.get("profile_pk")
        if not profile_pk:
            raise forms.ValidationError("El ID del perfil es requerido.")
        return profile_pk


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["comment"]
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Añade un comentario...",
                    "required": True,
                }
            )
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "image",
            "hobby",
            "is_online",
            "stream_url",
            "location",
            "event_date",
            "max_participants",
            "level",
        ]
        help_texts = {
            "level": "Explica la dificultad: Principiante (sin experiencia), Intermedio (conoces las bases),Avanzado (nivel técnico/competitivo), Experto (nivel profesional o muy experimentado).",
        }
        labels = {
            "hobby": "Terapia",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Quedada para fotos nocturnas",
                }
            ),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "hobby": forms.Select(attrs={"class": "form-select"}),
            "is_online": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "stream_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://www.youtube.com/watch?v=...",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "¿Dónde nos encontramos? (Opcional si es online)",
                }
            ),
            "event_date": forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",  # Esto activa el calendario en el navegador
                }
            ),
            "max_participants": forms.NumberInput(
                attrs={"class": "form-control", "min": 1}
            ),
            "level": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        qs = self.fields["hobby"].queryset.order_by("name")
        if not (self.user and (self.user.is_staff or self.user.is_superuser)):
            qs = qs.exclude(slug="agora")
        self.fields["hobby"].queryset = qs
        self.fields["hobby"].empty_label = "Selecciona o busca una terapia..."

    def clean_hobby(self):
        hobby = self.cleaned_data.get("hobby")
        if hobby and hobby.slug == "agora":
            if not (self.user and (self.user.is_staff or self.user.is_superuser)):
                raise forms.ValidationError(
                    "Solo el personal de dirección o administración (staff) puede crear eventos bajo la categoría Ágora."
                )
        return hobby

    def clean(self):
        cleaned_data = super().clean()
        is_online = cleaned_data.get("is_online")
        location = cleaned_data.get("location")
        stream_url = cleaned_data.get("stream_url")

        if not is_online and not location:
            raise forms.ValidationError("Debes especificar un lugar físico si el evento no es online.")
        
        if is_online and not stream_url and not location:
            raise forms.ValidationError("Debes proveer al menos el enlace de transmisión o un lugar físico.")
            
        event_date = cleaned_data.get("event_date")
        if event_date and event_date < timezone.now():
            raise forms.ValidationError({"event_date": "La fecha del evento no puede estar en el pasado."})

        return cleaned_data


class EventCommentForm(forms.ModelForm):
    class Meta:
        model = EventComment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Escribe un comentario o pregunta...",
                    "rows": "2",
                }
            ),
        }
