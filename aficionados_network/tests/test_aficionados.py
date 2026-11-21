from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from aficionados_network.models import ContactMessage


@override_settings(
    DEBUG=True,
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@example.com",
    CONTACT_EMAIL="admin@example.com",
)
# esta clase testea las vistas y los emails del core
class CoreViewAndEmailTests(TestCase):
    # testea la vista home para usuario anonimo
    def test_home_view_renders_for_anonymous_user(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "general/home.html")

    # testea el flujo de login y logout
    def test_login_and_logout_flow(self):
        User.objects.create_user(username="ana", password="testpass123")

        login_response = self.client.post(
            reverse("login"),
            {"username": "ana", "password": "testpass123"},
        )

        self.assertRedirects(login_response, reverse("home"))
        self.assertIn("_auth_user_id", self.client.session)

        logout_response = self.client.post(reverse("logout"))

        self.assertRedirects(logout_response, reverse("home"))
        self.assertNotIn("_auth_user_id", self.client.session)

    # testea el registro de un usuario inactivo y el envio de email de aprobacion a administracion
    def test_register_creates_inactive_user_and_admin_notification(self):
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Ana",
                "username": "ana",
                "email": "ana@example.com",
                "razon_social": "Empresa Salud SL",
                "numero_socio": "SOC-12345",
                "password1": "Complexpass123",
                "password2": "Complexpass123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/registration_pending.html")
        user = User.objects.get(username="ana")
        self.assertFalse(user.is_active)
        self.assertEqual(user.profile.razon_social, "Empresa Salud SL")
        self.assertEqual(user.profile.numero_socio, "SOC-12345")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("aprobación", mail.outbox[0].subject)

    def test_admin_activation_enqueues_welcome_email_via_celery(self):
        user = User.objects.create_user(
            username="paciente_nuevo",
            email="paciente_nuevo@example.com",
            password="testpass123",
            is_active=False,
        )
        mail.outbox.clear()
        user.is_active = True
        user.save()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("activada", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ["paciente_nuevo@example.com"])

    # testea el formulario de contacto y el envio de email de confirmacion
    def test_contact_form_persists_message_and_sends_email(self):
        response = self.client.post(
            reverse("contact"),
            {
                "name": "Ana",
                "email": "ana@example.com",
                "subject": "Duda",
                "message": "Quiero mas informacion.",
            },
        )

        self.assertRedirects(response, reverse("contact"))
        message = ContactMessage.objects.get()
        self.assertEqual(message.name, "Ana")
        self.assertEqual(str(message), "Ana - Duda")
        self.assertFalse(message.read)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Nuevo mensaje", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ["admin@example.com"])


from datetime import timedelta
from django.utils import timezone
from posts.models import Posts, Event
from profiles.models import Hobby, UserProfile, UserHobby
from library.models import Article


@override_settings(
    DEBUG=True,
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@example.com",
    CONTACT_EMAIL="admin@example.com",
)
class HomeViewRestructureTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="terapeuta1", password="password123"
        )
        self.profile = self.user.profile
        self.hobby = Hobby.objects.create(name="Acupuntura", slug="acupuntura")
        UserHobby.objects.create(
            profile=self.profile, hobby=self.hobby, level="intermediate"
        )

    def test_home_view_limits_to_10_posts_events_and_articles(self):
        now = timezone.now()

        # Crear 15 posts
        for i in range(15):
            Posts.objects.create(
                user=self.user,
                title=f"Post {i}",
                caption=f"Contenido {i}",
                category=self.hobby,
            )

        # Crear 15 eventos futuros activos
        for i in range(15):
            Event.objects.create(
                organizer=self.user,
                title=f"Evento {i}",
                description=f"Descripcion {i}",
                hobby=self.hobby,
                event_date=now + timedelta(days=i + 1),
                max_participants=10,
                level="intermediate",
            )

        # Crear 1 evento pasado y 1 cancelado (no deben aparecer en last_events)
        Event.objects.create(
            organizer=self.user,
            title="Evento Pasado",
            description="Ya paso",
            hobby=self.hobby,
            event_date=now - timedelta(days=2),
        )
        Event.objects.create(
            organizer=self.user,
            title="Evento Cancelado",
            description="Cancelado",
            hobby=self.hobby,
            event_date=now + timedelta(days=3),
            is_canceled=True,
        )

        # Crear 15 artículos de biblioteca
        for i in range(15):
            Article.objects.create(
                author=self.user,
                title=f"Articulo {i}",
                content=f"Contenido articulo {i}",
                hobby=self.hobby,
            )

        # 1. Test para usuario autenticado
        self.client.login(username="terapeuta1", password="password123")
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["last_posts"]), 10)
        self.assertEqual(len(response.context["last_events"]), 10)
        self.assertEqual(len(response.context["last_articles"]), 10)

        # Verificar que ningún evento en last_events esté cancelado o sea pasado
        for event in response.context["last_events"]:
            self.assertFalse(event.is_canceled)
            self.assertGreaterEqual(event.event_date, now)

        # Verificar tabs en HTML
        self.assertContains(response, 'id="posts-tab"')
        self.assertContains(response, 'id="events-tab"')
        self.assertContains(response, 'id="library-tab"')
        self.assertContains(response, "Eventos recomendados para ti")

        # 2. Test para usuario anónimo
        self.client.logout()
        anon_response = self.client.get(reverse("home"))
        self.assertEqual(anon_response.status_code, 200)
        self.assertEqual(len(anon_response.context["last_posts"]), 10)
        self.assertEqual(len(anon_response.context["last_events"]), 10)
        self.assertEqual(len(anon_response.context["last_articles"]), 10)

    def test_home_feed_includes_agora_post_even_if_not_following_author(self):
        agora, _ = Hobby.objects.get_or_create(name="Ágora", slug="agora")
        staff_user = User.objects.create_user(
            username="junta_directiva",
            email="directiva@example.com",
            password="password123",
            is_staff=True,
        )
        agora_post = Posts.objects.create(
            user=staff_user,
            title="Comunicado Oficial Urgente",
            caption="Comunicado para todos los socios",
            category=agora,
        )

        self.client.login(username="terapeuta1", password="password123")
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(agora_post, response.context["last_posts"])

    def test_home_prioritizes_agora_items_first(self):
        agora, _ = Hobby.objects.get_or_create(name="Ágora", slug="agora")
        staff_user = User.objects.create_user(
            username="presidencia",
            email="presi@example.com",
            password="password123",
            is_staff=True,
        )
        now = timezone.now()
        # Ágora post created earlier
        agora_post = Posts.objects.create(
            user=staff_user,
            title="Aviso Prioritario de Ágora",
            caption="Comunicado institucional",
            category=agora,
        )
        Posts.objects.filter(id=agora_post.id).update(created_at=now - timedelta(hours=2))

        # Normal post created later (newer)
        Posts.objects.create(
            user=self.user,
            title="Post Normal Más Reciente",
            caption="Contenido normal",
            category=self.hobby,
        )

        self.client.login(username="terapeuta1", password="password123")
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["last_posts"][0].id, agora_post.id)


class CeleryEmailTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="paciente_test",
            email="paciente@example.com",
            password="Password123!",
        )

    def test_send_email_task_delivers_email(self):
        from aficionados_network.tasks import send_email_task

        res = send_email_task.delay(
            subject="Prueba Celery",
            recipient_email="paciente@example.com",
            recipient_username="paciente_test",
            message_body="Mensaje de prueba enviado mediante Celery task",
            action_url="http://localhost:8000/profile/",
        )

        self.assertEqual(res.status, "SUCCESS")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["paciente@example.com"])
        self.assertEqual(mail.outbox[0].subject, "Prueba Celery")
        self.assertIn("paciente_test", mail.outbox[0].body)

    def test_send_hubs_email_async_dispatches_via_celery(self):
        from aficionados_network.utils.mailer import send_hubs_email_async

        send_hubs_email_async(
            subject="Notificación Quedada",
            recipient=self.user,
            message_body="¡Te has apuntado al evento!",
            action_url="http://localhost:8000/events/1/",
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["paciente@example.com"])
        self.assertIn("Notificación Quedada", mail.outbox[0].subject)

    def test_send_hubs_email_async_graceful_fallback(self):
        from unittest.mock import patch
        from aficionados_network.utils.mailer import send_hubs_email_async

        with patch("aficionados_network.tasks.send_email_task.delay", side_effect=RuntimeError("Redis connection refused")):
            send_hubs_email_async(
                subject="Fallback Email",
                recipient=self.user,
                message_body="Mensaje vía fallback",
                action_url="http://localhost:8000/",
            )

        # En fallback se despacha sincrónicamente o vía ThreadPoolExecutor
        # Damos un instante de tiempo por si corre en hilo
        import time
        time.sleep(0.1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["paciente@example.com"])
        self.assertEqual(mail.outbox[0].subject, "Fallback Email")



