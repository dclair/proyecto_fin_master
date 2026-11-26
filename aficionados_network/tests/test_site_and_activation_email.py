from django.test import TestCase, override_settings
from django.core import mail
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from aficionados_network.utils.site import (
    get_site_domain,
    get_site_protocol,
    get_base_url,
    build_absolute_url,
)
from aficionados_network.utils.mailer import send_hubs_email_async
from io import StringIO

User = get_user_model()


class SiteAndActivationEmailTests(TestCase):
    def setUp(self):
        mail.outbox.clear()
        # Reset default site to clean state
        Site.objects.filter(id=1).update(domain="127.0.0.1:8000", name="Hubs & Clicks")

    @override_settings(SITE_DOMAIN="hubsclicks.com", SITE_URL="", SITE_PROTOCOL="https")
    def test_get_site_domain_and_protocol(self):
        self.assertEqual(get_site_domain(), "hubsclicks.com")
        self.assertEqual(get_site_protocol(), "https")
        self.assertEqual(get_base_url(), "https://hubsclicks.com")
        self.assertEqual(
            build_absolute_url("/login/"), "https://hubsclicks.com/login/"
        )
        self.assertEqual(
            build_absolute_url("https://external.com/test"),
            "https://external.com/test",
        )

    @override_settings(SITE_DOMAIN="", SITE_URL="https://custom-domain.org/app")
    def test_get_site_domain_from_site_url(self):
        self.assertEqual(get_site_domain(), "custom-domain.org")
        self.assertEqual(get_base_url(), "https://custom-domain.org/app")
        self.assertEqual(
            build_absolute_url("/login/"), "https://custom-domain.org/app/login/"
        )

    @override_settings(
        SITE_DOMAIN="",
        SITE_URL="",
        ALLOWED_HOSTS=["141.148.227.48", "localhost"],
    )
    def test_fallback_to_allowed_hosts_when_db_is_example_com(self):
        Site.objects.filter(id=1).update(domain="example.com")
        self.assertEqual(get_site_domain(), "141.148.227.48")

    @override_settings(
        SITE_DOMAIN="141.148.227.48",
        SITE_URL="http://141.148.227.48",
        SITE_PROTOCOL="http",
    )
    def test_activation_email_contains_real_domain_and_not_example_com(self):
        # Crear usuario inactivo
        user = User.objects.create_user(
            username="test_socio",
            email="socio@example.com",
            password="testpassword123",
            is_active=False,
        )
        mail.outbox.clear()

        # Activar usuario como lo haría un administrador
        user.is_active = True
        user.save()

        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]

        # Verificar asunto y destinatario
        self.assertIn("activada", sent_mail.subject)
        self.assertEqual(sent_mail.to, ["socio@example.com"])

        # Verificar que NO contiene example.com en ninguna parte del correo
        self.assertNotIn("example.com/login", sent_mail.body)
        self.assertNotIn("http://example.com", sent_mail.body)

        # Verificar que el botón / action_url apunta a la URL real
        expected_url = "http://141.148.227.48/login/"
        html_content = sent_mail.alternatives[0][0]
        self.assertIn(expected_url, html_content)
        self.assertIn("Ver en la Web", html_content)
        self.assertNotIn("example.com", html_content)

    @override_settings(
        SITE_DOMAIN="comunidad.hubsclicks.es",
        SITE_URL="https://comunidad.hubsclicks.es",
        SITE_PROTOCOL="https",
    )
    def test_activation_email_with_https_domain(self):
        user = User.objects.create_user(
            username="socio_https",
            email="socio_https@example.com",
            password="testpassword123",
            is_active=False,
        )
        mail.outbox.clear()

        user.is_active = True
        user.save()

        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        html_content = sent_mail.alternatives[0][0]

        expected_url = "https://comunidad.hubsclicks.es/login/"
        self.assertIn(expected_url, html_content)
        self.assertNotIn("example.com", html_content)

    def test_update_site_management_command(self):
        out = StringIO()
        call_command(
            "update_site",
            "--domain",
            "141.148.227.48",
            "--name",
            "Hubs & Clicks Producción",
            stdout=out,
        )

        site = Site.objects.get(id=1)
        self.assertEqual(site.domain, "141.148.227.48")
        self.assertEqual(site.name, "Hubs & Clicks Producción")
        self.assertIn("actualizado con éxito", out.getvalue())

    @override_settings(
        SITE_DOMAIN="141.148.227.48",
        SITE_URL="http://141.148.227.48",
    )
    def test_relative_action_url_converted_to_absolute_in_email(self):
        user = User.objects.create_user(
            username="test_relative",
            email="relative@example.com",
            password="testpass123",
        )
        mail.outbox.clear()

        # Enviar con action_url relativa (ej. /events/42/)
        send_hubs_email_async(
            subject="Test URL relativa",
            recipient=user,
            message_body="Probando resolución absoluta de URL",
            action_url="/events/42/",
        )

        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        html_content = sent_mail.alternatives[0][0]

        self.assertIn("http://141.148.227.48/events/42/", html_content)
        self.assertNotIn('href="/events/42/"', html_content)
