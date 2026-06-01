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
class CoreViewAndEmailTests(TestCase):
    def test_home_view_renders_for_anonymous_user(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "general/home.html")

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

    def test_register_creates_inactive_user_and_activation_email(self):
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Ana",
                "username": "ana",
                "email": "ana@example.com",
                "password1": "Complexpass123",
                "password2": "Complexpass123",
            },
        )

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username="ana")
        self.assertFalse(user.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Activa tu cuenta", mail.outbox[0].subject)

    def test_activation_enables_user_and_sends_welcome_email(self):
        user = User.objects.create_user(
            username="ana",
            email="ana@example.com",
            password="Complexpass123",
            is_active=False,
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.get(
            reverse("activate", kwargs={"uidb64": uid, "token": token})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/activation_success.html")
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Bienvenido", mail.outbox[0].subject)

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
