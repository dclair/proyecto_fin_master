from django.contrib import admin
from django.urls import path, include
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
from profiles.views import ProfilesListView, ProfileView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    # path("", include("posts.urls")),  # Incluye las URLs de la app posts
    path("events/", include("posts.urls")),
    path(
        "profile/", include("profiles.urls")
    ),  # Esto delega las rutas a la app profiles
    path("profile/list/", ProfilesListView.as_view(), name="profile_list"),
    path("profile/<int:pk>/", ProfileView.as_view(), name="profile"),
    # urls autenticación
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
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
]

# Configuración para servir archivos multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
