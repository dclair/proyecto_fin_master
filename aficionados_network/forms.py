from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from profiles.models import UserProfile, UserHobby, Hobby
from .models import ContactMessage


class RegisterForm(UserCreationForm):
    razon_social = forms.CharField(
        max_length=255,
        required=True,
        label="Razón Social",
        help_text="Nombre de la empresa, autónomo",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de empresa o autónomo"})
    )
    numero_socio = forms.CharField(
        max_length=50,
        required=True,
        label="Número de Socio",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Número de socio"})
    )

    class Meta:
        model = User
        fields = ["first_name", "username", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['first_name'].label = "Nombre Completo"
        self.fields['first_name'].help_text = "Nombre y apellidos completos. La persona que está registrada en la asociación"
        self.fields['email'].required = True
        self.fields['email'].help_text = "Mismo email con el que estás registrado en la Asociación."
        self.fields['username'].help_text = "Letras, números y caracteres @/./+/-/_ únicamente."
        
        # Sobrescribimos el help_text por defecto de password1
        self.fields['password1'].help_text = (
            "<ul>"
            "<li>La contraseña no debe parecer o contener a su nombre, razón social, nombre de usuario o email.</li>"
            "<li>Debe contener al menos 8 caracteres.</li>"
            "<li>No puede ser una clave utilizada comúnmente.</li>"
            "<li>No puede ser completamente numérica.</li>"
            "</ul>"
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe un usuario registrado con este correo electrónico.")
        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Tu correo electrónico"}
        )
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Tu contraseña"}
        )
    )


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este correo electrónico ya está en uso por otro usuario.")
        return email


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["bio", "birth_date", "location", "address", "phone", "mobile", "website", "profile_picture"]
        widgets = {
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "birth_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"
            ),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control", "placeholder": "Dirección completa"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+34 912 345 678"}),
            "mobile": forms.TextInput(attrs={"class": "form-control", "placeholder": "+34 600 000 000"}),
            "website": forms.URLInput(attrs={"class": "form-control"}),
            "profile_picture": forms.FileInput(
                attrs={
                    "class": "form-control-file",
                    "accept": "image/*",
                    "onchange": "previewImage(this);",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurarse de que el formato de fecha sea compatible con el input type="date"
        self.fields["birth_date"].input_formats = ["%Y-%m-%d"]
        self.fields["profile_picture"].required = False

        # Si ya hay una imagen de perfil, mostrarla
        if self.instance and self.instance.profile_picture:
            self.fields["profile_picture"].widget.initial_text = "Imagen actual"
            self.fields["profile_picture"].widget.template_name = (
                "django/forms/widgets/clearable_file_input.html"
            )


# aficionados_network/forms.py
class ProfileFollowForm(forms.Form):
    action = forms.ChoiceField(
        choices=[("follow", "Seguir"), ("unfollow", "Dejar de seguir")]
    )
    profile_id = forms.IntegerField(widget=forms.HiddenInput())


class ContactForm(forms.ModelForm):

    attachment = forms.FileField(
        required=False,
        label="Archivo adjunto (opcional)",
        widget=forms.FileInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Tu nombre", "required": "required", "maxlength": "100"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Tu correo", "required": "required", "maxlength": "254"}
            ),
            "subject": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Asunto", "required": "required", "maxlength": "200"}
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Escribe tu mensaje",
                    "required": "required"
                }
            ),
        }

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            max_size = 20 * 1024 * 1024  # 20MB
            if attachment.size > max_size:
                raise forms.ValidationError("El archivo no puede superar los 20 MB.")
        return attachment


class AddHobbyForm(forms.ModelForm):
    class Meta:
        model = UserHobby
        fields = ["hobby", "level"]
        labels = {"hobby": "Terapia", "level": "Nivel de experiencia"}
        widgets = {
            "hobby": forms.Select(attrs={"class": "form-select"}),
            "level": forms.Select(attrs={"class": "form-select"}),
        }
