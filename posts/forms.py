from django import forms
from .models import Posts, Comment, Event, EventComment


from django import forms
from .models import Posts


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
        # Añadimos 'location' y organizamos el orden de aparición
        fields = ["title", "category", "location", "caption", "image", "video", "video_url"]

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
            "video_url": forms.URLInput(
                attrs={
                    "class": "form-control validate-media",
                    "placeholder": "https://www.youtube.com/watch?v=...",
                    "id": "id_video_url",
                }
            ),
        }

        error_messages = {
            "category": {
                "required": "Debes elegir una terapia para clasificar tu post.",
            },
        }

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("image")
        video = cleaned_data.get("video")
        video_url = cleaned_data.get("video_url")

        if not image and not video and not video_url:
            raise forms.ValidationError(
                "Debes subir una foto, un vídeo o proporcionar un enlace de vídeo para publicar."
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

    def clean(self):
        cleaned_data = super().clean()
        is_online = cleaned_data.get("is_online")
        location = cleaned_data.get("location")
        stream_url = cleaned_data.get("stream_url")

        if not is_online and not location:
            raise forms.ValidationError("Debes especificar un lugar físico si el evento no es online.")
        
        if is_online and not stream_url and not location:
            raise forms.ValidationError("Debes proveer al menos el enlace de transmisión o un lugar físico.")
            
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
