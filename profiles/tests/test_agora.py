from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from profiles.models import Hobby, UserHobby, UserProfile
from posts.forms import PostCreateForm, EventForm
from library.forms import ArticleForm
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class AgoraInstitutionalTests(TestCase):
    def setUp(self):
        # Aseguramos que existe Ágora
        self.agora, _ = Hobby.objects.get_or_create(
            slug="agora",
            defaults={"name": "Ágora", "description": "Canal oficial de la asociación"}
        )
        self.osteopatia = Hobby.objects.create(
            name="Osteopatía",
            slug="osteopatia"
        )

        # Usuario normal
        self.user = User.objects.create_user(
            username="socio_normal",
            email="socio@test.com",
            password="password123"
        )

        # Usuario staff
        self.staff_user = User.objects.create_user(
            username="directivo_staff",
            email="directivo@test.com",
            password="password123",
            is_staff=True
        )

    def test_user_creation_automatically_assigns_agora_hobby(self):
        profile = self.user.profile
        self.assertTrue(
            UserHobby.objects.filter(profile=profile, hobby=self.agora).exists()
        )
        self.assertTrue(
            profile.hobbies.filter(slug="agora").exists()
        )

    def test_agora_cannot_be_deleted_from_profile(self):
        self.client.force_login(self.user)
        user_hobby = UserHobby.objects.get(profile=self.user.profile, hobby=self.agora)

        response = self.client.get(reverse("profiles:delete_hobby", kwargs={"hobby_id": user_hobby.id}))
        self.assertRedirects(response, reverse("profiles:profile_edit"))

        # Debe seguir existiendo
        self.assertTrue(
            UserHobby.objects.filter(id=user_hobby.id).exists()
        )

    def test_profile_edit_excludes_agora_from_selectable_hobbies(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("profiles:profile_edit"))
        self.assertEqual(response.status_code, 200)

        selectable_hobbies = response.context["all_hobbies"]
        self.assertNotIn(self.agora, selectable_hobbies)
        self.assertIn(self.osteopatia, selectable_hobbies)

    def test_non_staff_cannot_select_or_submit_agora_for_posts(self):
        # 1. El queryset del formulario no debe incluir Ágora para usuario normal
        form = PostCreateForm(user=self.user)
        self.assertNotIn(self.agora, form.fields["category"].queryset)

        # 2. Si intenta forzar Ágora en el POST
        form_post = PostCreateForm(
            data={
                "title": "Intento no autorizado",
                "category": self.agora.pk,
                "caption": "Publicación intentando suplantar Ágora",
                "external_url": "https://ejemplo.com",
            },
            user=self.user
        )
        self.assertFalse(form_post.is_valid())
        self.assertIn("category", form_post.errors)

    def test_staff_user_can_publish_under_agora_category(self):
        form = PostCreateForm(user=self.staff_user)
        self.assertIn(self.agora, form.fields["category"].queryset)

        form_post = PostCreateForm(
            data={
                "title": "Comunicado Oficial",
                "category": self.agora.pk,
                "caption": "Aviso oficial de la junta directiva",
                "external_url": "https://asociacion.org/comunicado",
            },
            user=self.staff_user
        )
        self.assertTrue(form_post.is_valid(), form_post.errors)

    def test_non_staff_cannot_select_agora_for_events(self):
        form = EventForm(user=self.user)
        self.assertNotIn(self.agora, form.fields["hobby"].queryset)

        form_event = EventForm(
            data={
                "title": "Asamblea General",
                "description": "Reunión anual",
                "hobby": self.agora.pk,
                "location": "Sede Central",
                "event_date": (timezone.now() + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M"),
                "max_participants": 50,
                "level": "all",
            },
            user=self.user
        )
        self.assertFalse(form_event.is_valid())
        self.assertIn("hobby", form_event.errors)

    def test_staff_user_can_create_agora_event(self):
        form = EventForm(user=self.staff_user)
        self.assertIn(self.agora, form.fields["hobby"].queryset)

        form_event = EventForm(
            data={
                "title": "Asamblea General Oficial",
                "description": "Reunión anual oficial de la asociación",
                "hobby": self.agora.pk,
                "location": "Sede Central",
                "event_date": (timezone.now() + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M"),
                "max_participants": 50,
                "level": "all",
            },
            user=self.staff_user
        )
        self.assertTrue(form_event.is_valid(), form_event.errors)

    def test_non_staff_cannot_create_agora_article_in_library(self):
        form = ArticleForm(user=self.user)
        self.assertNotIn(self.agora, form.fields["hobby"].queryset)

        form_article = ArticleForm(
            data={
                "title": "Artículo institucional falso",
                "hobby": self.agora.pk,
                "content": "Contenido...",
            },
            user=self.user
        )
        self.assertFalse(form_article.is_valid())
