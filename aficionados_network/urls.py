from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from .views import (
    HomeView,
    LoginView,
    RegisterView,
    LogoutView,
    ContactFormView,
    activate,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    # path("", include("posts.urls")),  # Incluye las URLs de la app posts
    path("events/", include("posts.urls")),
    path(
        "profile/", include("profiles.urls")
    ),  # Esto delega las rutas a la app profiles
    # urls autenticación
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="general/password_reset/form.html",
            email_template_name="general/password_reset/email.html",
            from_email=settings.DEFAULT_FROM_EMAIL,
            subject_template_name="general/password_reset/subject.txt",
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="general/password_reset/done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="general/password_reset/confirm.html",
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="general/password_reset/complete.html",
        ),
        name="password_reset_complete",
    ),
    path("register/", RegisterView.as_view(), name="register"),
    # Esta es la URL que el usuario pincha en su correo:
    path("activate/<uidb64>/<token>/", activate, name="activate"),
    path("contact/", ContactFormView.as_view(), name="contact"),
    path(
        "legal/",
        TemplateView.as_view(template_name="general/legal.html"),
        name="legal",
    ),
    path(
        "privacidad/",
        TemplateView.as_view(template_name="general/privacy.html"),
        name="privacy_policy",
    ),
    path(
        "politica-cookies/",
        TemplateView.as_view(template_name="general/cookies_policy.html"),
        name="cookies_policy",
    ),
    path(
        "cookies/",
        TemplateView.as_view(template_name="general/cookies_policy.html"),
        name="cookies",
    ),
    path("pages/", include("django.contrib.flatpages.urls")),
    path("notifications/", include("notifications.urls")),
    path("api/chat/", include("chat.api_urls")),
]

# Configuración para servir archivos multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
