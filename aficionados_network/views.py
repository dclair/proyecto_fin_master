from django.contrib.admin import action
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView,
    DetailView,
    TemplateView,
    FormView,
    UpdateView,
    ListView,
)
from django.views.generic.edit import FormView
from .forms import ContactForm
from django.utils import timezone
from django.views import View
from django.contrib.auth import login, authenticate, logout, logout as auth_logout
from django.http import Http404, HttpResponseRedirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from profiles.models import UserProfile, Follow, UserHobby, Hobby
from django.contrib.auth.mixins import LoginRequiredMixin
from posts.models import Posts, Event
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
import os
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode


User = get_user_model()

# aficionados_network/views.py

from profiles.models import (
    UserProfile,
    Follow,
    UserHobby,
    Hobby,
)  # Asegura estos imports


class HomeView(TemplateView):
    template_name = "general/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()

        # --- TU LÓGICA DE POSTS ORIGINAL ---
        last_posts = Posts.objects.none()
        if user.is_authenticated:
            has_profile = hasattr(user, "profile")
            context["has_profile"] = has_profile
            if not has_profile:
                last_posts = Posts.objects.all().order_by("-created_at")[:20]
            else:
                profile = user.profile
                seguidos = Follow.objects.filter(follower=profile).values_list(
                    "following__user", flat=True
                )
                last_posts = Posts.objects.filter(user__in=seguidos).order_by(
                    "-created_at"
                )[:20]
                if not last_posts.exists():
                    last_posts = Posts.objects.all().order_by("-created_at")[:20]
        else:
            last_posts = Posts.objects.all().order_by("-created_at")[:20]
        context["last_posts"] = last_posts

        # --- TU LÓGICA DE EVENTOS ORIGINAL ---
        base_filter = Q(event_date__gte=now, is_canceled=False)
        upcoming_events = Event.objects.none()

        if user.is_authenticated and hasattr(user, "profile"):
            my_hobbies = user.profile.hobbies.all()  # Tus terapias para la sidebar

            # --- LÓGICA DE NIVELES PARA LA SIDEBAR (NUEVO) ---
            user_levels = UserHobby.objects.filter(profile=user.profile).values(
                "hobby_id", "level"
            )
            levels_map = {item["hobby_id"]: item["level"] for item in user_levels}

            for hobby in my_hobbies:
                u_level = levels_map.get(hobby.id)
                hobby.match_count = (
                    Event.objects.filter(
                        hobby=hobby, **{"event_date__gte": now, "is_canceled": False}
                    )
                    .filter(
                        Q(level="all") | Q(level=u_level) if u_level else Q(level="all")
                    )
                    .count()
                )
            context["my_hobbies"] = my_hobbies  # Esta es la variable que usa tu sidebar

            if my_hobbies.exists():
                personal_filter = Q(hobby__in=my_hobbies) | Q(organizer=user)
                upcoming_events = (
                    Event.objects.filter(base_filter & personal_filter)
                    .select_related("hobby")
                    .distinct()
                    .order_by("event_date")[:5]
                )
                context["filtered_by_hobbies"] = True
            else:
                upcoming_events = Event.objects.filter(base_filter).order_by(
                    "event_date"
                )[:5]
                context["filtered_by_hobbies"] = False

            context["user_levels_map"] = levels_map
        context["upcoming_events"] = upcoming_events
        return context


class LoginView(FormView):
    template_name = "general/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
            messages.success(self.request, f"¡Bienvenido/a {user.username}!")
            return super().form_valid(form)
        else:
            messages.error(self.request, "Usuario o contraseña incorrectos")
            return self.form_invalid(form)


class LogoutView(LoginRequiredMixin, View):
    """
    Vista segura para manejar el cierre de sesión solo mediante POST.
    """

    login_url = "login"

    def post(self, request, *args, **kwargs):
        auth_logout(request)
        messages.success(request, "Has cerrado sesión correctamente.")
        return redirect("home")

    # Si alguien intenta entrar por GET (escribiendo la URL),
    # lo redirigimos a inicio sin cerrar sesión, o a una página de confirmación.
    def get(self, request, *args, **kwargs):
        return redirect("home")


class RegisterView(CreateView):
    model = User
    template_name = "general/register.html"
    form_class = RegisterForm  # Tu formulario actual
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        # 1. Guardamos el usuario pero sin activar
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # Actualizamos el UserProfile con los nuevos campos
        razon_social = form.cleaned_data.get("razon_social")
        numero_socio = form.cleaned_data.get("numero_socio")
        
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.razon_social = razon_social
        profile.numero_socio = numero_socio
        profile.save()

        # 2. Enviamos el correo a la administración
        admin_email = "jmdclair@gmail.com"
        mail_subject = "Nuevo registro pendiente de aprobación"
        
        text_content = (
            f"Se ha registrado un nuevo usuario y requiere aprobación en el panel de administración:\n\n"
            f"Nombre: {user.first_name}\n"
            f"Email: {user.email}\n"
            f"Razón Social: {razon_social}\n"
            f"Número de Socio: {numero_socio}\n"
        )

        email = EmailMultiAlternatives(
            mail_subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email]
        )
        email.send()

        # 4. Mostramos la pantalla indicando que la solicitud está en revisión
        return render(
            self.request, "registration/registration_pending.html", {"email": user.email}
        )


# --- La función de activación ---
def activate(request, uidb64, token):
    try:
        # Decodificamos el ID del usuario de la URL
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Verificamos si el token es válido
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        # --- CONFIGURACIÓN DEL EMAIL DE BIENVENIDA ---
        current_site = get_current_site(request)
        mail_subject = "¡Bienvenido a Hubs & Clicks!"

        # Renderizamos el HTML del correo
        html_content = render_to_string(
            "registration/welcome_email.html",
            {
                "user": user,
                "domain": current_site.domain,
            },
        )

        # Creamos el correo (EmailMultiAlternatives es necesario para adjuntos CID)
        email = EmailMultiAlternatives(mail_subject, "", to=[user.email])
        email.attach_alternative(html_content, "text/html")

        # Adjuntamos el logo como recurso relacionado (CID)
        img_path = os.path.join(settings.BASE_DIR, "static", "img", "logo_hubs.png")

        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                logo = MIMEImage(f.read())
                # El ID <logo_id> debe coincidir con el src="cid:logo_id" del HTML
                logo.add_header("Content-ID", "<logo_id>")
                email.attach(logo)

        email.send()
        # -------------------------------------

        return render(request, "registration/activation_success.html")
    else:
        return render(request, "registration/activation_invalid.html")



class ContactFormView(FormView):
    template_name = "general/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact")

    def form_valid(self, form):
        contact_message = form.save()

        # 1. Definimos los datos para la plantilla
        subject = f"📬 Nuevo mensaje: {contact_message.subject}"
        recipient_email = settings.CONTACT_EMAIL

        # El cuerpo del mensaje que irá dentro de {{ message_body }}
        full_message = (
            f"Has recibido un nuevo mensaje de contacto a través de la web.\n\n"
            f"👤 Nombre: {contact_message.name}\n"
            f"📧 Email: {contact_message.email}\n"
            f"📝 Mensaje:\n{contact_message.message}"
        )

        context = {
            "recipient_name": "Equipo de Hubs&Clicks",  # Quién recibe el mail (tú)
            "message_body": full_message,
            "action_url": self.request.build_absolute_uri("/admin/"),  # Link al panel
        }

        # 2. Renderizamos el HTML
        html_content = render_to_string(
            "general/emails/notification_email.html", context
        )
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            cc=[contact_message.email],
        )
        email.attach_alternative(html_content, "text/html")

        # 4. Incrustamos el logo usando el ID exacto de tu plantilla: logo_hubs
        logo_path = os.path.join(settings.BASE_DIR, "static", "img", "logo_hubs.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo_image = MIMEImage(f.read())
                logo_image.add_header("Content-ID", "<logo_hubs>")
                email.attach(logo_image)

        # 4.5 Adjuntamos el archivo si el usuario lo subió
        attachment = form.cleaned_data.get('attachment')
        if attachment:
            email.attach(attachment.name, attachment.read(), attachment.content_type)

        # 5. Enviar
        import smtplib
        try:
            email.send(fail_silently=False)
            messages.success(
                self.request, "Gracias por tu mensaje. Nos pondremos en contacto pronto."
            )
        except smtplib.SMTPException as e:
            messages.error(
                self.request, "Hubo un error al enviar el mensaje. Verifica las credenciales de correo electrónico del servidor."
            )
            # Retornar form_invalid para que no se pierdan los datos o redirigir
            return super().form_valid(form)
        except Exception as e:
            messages.error(
                self.request, "Ocurrió un error inesperado al procesar el mensaje."
            )
        return super().form_valid(form)
