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
from django.db.models import Q, Case, When, Value, IntegerField
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
)
from library.models import Article


class HomeView(TemplateView):
    template_name = "general/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()

        # 1. --- ÚLTIMAS 10 PUBLICACIONES (Priorizando Ágora y luego por fecha) ---
        post_is_agora = Case(
            When(category__slug="agora", then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
        posts_base_qs = (
            Posts.objects.select_related("user", "user__profile", "category")
            .prefetch_related("likes", "comments")
            .annotate(is_agora=post_is_agora)
        )

        last_posts = Posts.objects.none()
        if user.is_authenticated:
            has_profile = hasattr(user, "profile")
            context["has_profile"] = has_profile
            if not has_profile:
                last_posts = posts_base_qs.order_by("-is_agora", "-created_at")[:10]
            else:
                profile = user.profile
                seguidos = Follow.objects.filter(follower=profile).values_list(
                    "following__user", flat=True
                )
                my_hobbies = profile.hobbies.all()
                feed_filter = (
                    Q(category__in=my_hobbies)
                    | Q(user__in=seguidos)
                    | Q(user=user)
                    | Q(category__slug="agora")
                )
                last_posts = (
                    posts_base_qs.filter(feed_filter)
                    .distinct()
                    .order_by("-is_agora", "-created_at")[:10]
                )
                if not last_posts.exists():
                    last_posts = posts_base_qs.order_by("-is_agora", "-created_at")[:10]
        else:
            last_posts = posts_base_qs.order_by("-is_agora", "-created_at")[:10]
        context["last_posts"] = last_posts

        # 2. --- EVENTOS RECOMENDADOS / DESTACADOS (Sidebar horizontal - Priorizando Ágora) ---
        event_is_agora = Case(
            When(hobby__slug="agora", then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
        base_event_filter = Q(event_date__gte=now, is_canceled=False)
        upcoming_events = Event.objects.none()

        if user.is_authenticated and hasattr(user, "profile"):
            my_hobbies = user.profile.hobbies.all()

            if my_hobbies.exists():
                personal_filter = Q(hobby__in=my_hobbies) | Q(organizer=user)
                upcoming_events = (
                    Event.objects.filter(base_event_filter & personal_filter)
                    .select_related("hobby", "organizer")
                    .prefetch_related("participants")
                    .distinct()
                    .annotate(is_agora=event_is_agora)
                    .order_by("-is_agora", "event_date")[:4]
                )
                context["filtered_by_hobbies"] = True

            if not upcoming_events.exists():
                upcoming_events = (
                    Event.objects.filter(base_event_filter)
                    .select_related("hobby", "organizer")
                    .prefetch_related("participants")
                    .annotate(is_agora=event_is_agora)
                    .order_by("-is_agora", "event_date")[:4]
                )
                context["filtered_by_hobbies"] = False

        # Si no hay eventos futuros activos (o usuario anónimo), mostramos los eventos activos más recientes
        if not upcoming_events.exists():
            fallback_qs = (
                Event.objects.filter(is_canceled=False)
                .select_related("hobby", "organizer")
                .prefetch_related("participants")
                .annotate(is_agora=event_is_agora)
            )
            if user.is_authenticated and hasattr(user, "profile") and user.profile.hobbies.exists():
                h_events = fallback_qs.filter(hobby__in=user.profile.hobbies.all()).order_by("-is_agora", "-event_date")[:4]
                upcoming_events = h_events if h_events.exists() else fallback_qs.order_by("-is_agora", "-event_date")[:4]
            else:
                upcoming_events = fallback_qs.order_by("-is_agora", "-event_date")[:4]

        context["upcoming_events"] = upcoming_events

        # 3. --- LOS 10 EVENTOS (Pestaña General de Eventos - Priorizando Ágora) ---
        last_events = (
            Event.objects.filter(base_event_filter)
            .select_related("hobby", "organizer")
            .prefetch_related("participants")
            .annotate(is_agora=event_is_agora)
            .order_by("-is_agora", "event_date")[:10]
        )
        if not last_events.exists():
            last_events = (
                Event.objects.filter(is_canceled=False)
                .select_related("hobby", "organizer")
                .prefetch_related("participants")
                .annotate(is_agora=event_is_agora)
                .order_by("-is_agora", "-event_date")[:10]
            )
        context["last_events"] = last_events

        # 4. --- LAS 10 ÚLTIMAS PUBLICACIONES DE BIBLIOTECA (Pestaña Biblioteca - Priorizando Ágora) ---
        article_is_agora = Case(
            When(hobby__slug="agora", then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
        last_articles = (
            Article.objects.select_related("author", "hobby")
            .annotate(is_agora=article_is_agora)
            .order_by("-is_agora", "-created_at")[:10]
        )
        context["last_articles"] = last_articles

        # 5. --- MAPA DE NIVELES DEL USUARIO (Para badges de match de nivel) ---
        if user.is_authenticated and hasattr(user, "profile"):
            user_levels_qs = UserHobby.objects.filter(profile=user.profile).values(
                "hobby_id", "level"
            )
            context["user_levels_map"] = {
                item["hobby_id"]: item["level"] for item in user_levels_qs
            }
        else:
            context["user_levels_map"] = {}

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
        admin_email = getattr(settings, "CONTACT_EMAIL", "jmdclair@gmail.com")
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
