import os
import shutil
import tempfile
from datetime import timedelta
from unittest.mock import patch

from celery.schedules import crontab
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from aficionados_network.celery import app as celery_app
from marketplace.models import Listing
from profiles.models import Hobby


class MarketplaceLifecycleTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.temp_media_dir = tempfile.mkdtemp()
        cls._media_override = override_settings(MEDIA_ROOT=cls.temp_media_dir)
        cls._media_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._media_override.disable()
        shutil.rmtree(cls.temp_media_dir, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(
            username="seller_user",
            email="seller@example.com",
            password="PassComplex123!",
        )
        self.hobby = Hobby.objects.create(name="Osteopatía", slug="osteopatia")

    def create_listing(self, title, days_ago, warning_sent=False, with_files=False):
        image_file = None
        video_file = None

        if with_files:
            dummy_png = (
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
                b'\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01'
                b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
            )
            image_file = SimpleUploadedFile(
                f"{title.lower().replace(' ', '_')}.png",
                dummy_png,
                content_type="image/png",
            )
            video_file = SimpleUploadedFile(
                f"{title.lower().replace(' ', '_')}.mp4",
                b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00isommp42",
                content_type="video/mp4",
            )

        listing = Listing.objects.create(
            seller=self.user,
            hobby=self.hobby,
            title=title,
            description="Descripción de prueba para ciclo de vida",
            price=50.00,
            listing_type="SALE",
            status="AVAILABLE",
            expiration_warning_sent=warning_sent,
            image=image_file,
            video=video_file,
        )

        past_time = timezone.now() - timedelta(days=days_ago)
        Listing.objects.filter(pk=listing.pk).update(created_at=past_time)
        listing.refresh_from_db()
        return listing

    @patch("marketplace.management.commands.manage_marketplace_lifecycle.send_hubs_email_async")
    def test_listing_under_83_days_untouched_and_no_warning(self, mock_send_email):
        """
        Anuncios de menos de 83 días no deben recibir aviso de caducidad ni ser eliminados.
        """
        listing = self.create_listing(title="Camilla Reciente", days_ago=50)

        call_command("manage_marketplace_lifecycle")

        listing.refresh_from_db()
        self.assertFalse(listing.expiration_warning_sent)
        self.assertTrue(Listing.objects.filter(pk=listing.pk).exists())
        mock_send_email.assert_not_called()

    @patch("marketplace.management.commands.manage_marketplace_lifecycle.send_hubs_email_async")
    def test_listing_between_83_and_90_days_receives_warning_and_sets_flag(self, mock_send_email):
        """
        Anuncios de entre 83 y 90 días con expiration_warning_sent=False deben recibir aviso
        y quedar marcados con expiration_warning_sent=True.
        """
        listing = self.create_listing(title="Ecógrafo Antiguo", days_ago=85, warning_sent=False)

        call_command("manage_marketplace_lifecycle")

        listing.refresh_from_db()
        self.assertTrue(listing.expiration_warning_sent)
        self.assertTrue(Listing.objects.filter(pk=listing.pk).exists())

        mock_send_email.assert_called_once()
        _, kwargs = mock_send_email.call_args
        self.assertEqual(kwargs["recipient"], self.user)
        self.assertIn("expirará en 7 días", kwargs["subject"])
        self.assertIn("Ecógrafo Antiguo", kwargs["subject"])
        self.assertEqual(kwargs["action_url"], reverse("marketplace:listing_list"))

    @patch("marketplace.management.commands.manage_marketplace_lifecycle.send_hubs_email_async")
    def test_idempotency_second_run_does_not_resend_warning(self, mock_send_email):
        """
        Garantía de idempotencia: Si ya se envió el aviso (expiration_warning_sent=True),
        una segunda o subsecuente ejecución no vuelve a enviar correo.
        """
        listing = self.create_listing(title="Lámpara Infrarroja", days_ago=86, warning_sent=False)

        # Primera ejecución: debe enviar correo
        call_command("manage_marketplace_lifecycle")
        self.assertEqual(mock_send_email.call_count, 1)

        listing.refresh_from_db()
        self.assertTrue(listing.expiration_warning_sent)

        # Segunda ejecución: no debe volver a enviar correo
        mock_send_email.reset_mock()
        call_command("manage_marketplace_lifecycle")
        mock_send_email.assert_not_called()

    @patch("marketplace.management.commands.manage_marketplace_lifecycle.send_hubs_email_async")
    def test_listing_over_90_days_hard_deleted(self, mock_send_email):
        """
        Anuncios con antigüedad mayor a 90 días deben eliminarse definitivamente
        (hard delete) de la base de datos.
        """
        listing = self.create_listing(title="Tensiómetro Vencido", days_ago=92)
        listing_id = listing.pk

        call_command("manage_marketplace_lifecycle")

        self.assertFalse(Listing.objects.filter(pk=listing_id).exists())
        # Anuncios > 90 días no entran en la ventana de aviso de 83 a 90 días
        mock_send_email.assert_not_called()

    def test_post_delete_signal_cleans_multimedia_files(self):
        """
        Valida que al eliminar un Listing, la señal post_delete elimine físicamente
        los archivos de imagen y video asociados en el almacenamiento.
        """
        listing = self.create_listing(title="Kit Completo con Media", days_ago=10, with_files=True)

        image_name = listing.image.name
        video_name = listing.video.name

        self.assertTrue(default_storage.exists(image_name))
        self.assertTrue(default_storage.exists(video_name))

        # Hard delete de la instancia
        listing.delete()

        # Comprobar que los archivos físicos se eliminaron
        self.assertFalse(default_storage.exists(image_name))
        self.assertFalse(default_storage.exists(video_name))

    def test_lifecycle_command_deletes_files_via_post_delete(self):
        """
        Valida que la ejecución del comando para anuncios > 90 días active la señal
        post_delete y elimine los archivos multimedia del storage.
        """
        listing = self.create_listing(title="Equipo Muy Viejo", days_ago=95, with_files=True)

        image_name = listing.image.name
        video_name = listing.video.name

        self.assertTrue(default_storage.exists(image_name))
        self.assertTrue(default_storage.exists(video_name))

        call_command("manage_marketplace_lifecycle")

        self.assertFalse(Listing.objects.filter(pk=listing.pk).exists())
        self.assertFalse(default_storage.exists(image_name))
        self.assertFalse(default_storage.exists(video_name))

    @patch("marketplace.management.commands.manage_marketplace_lifecycle.send_hubs_email_async")
    def test_dry_run_flag(self, mock_send_email):
        """
        Valida que la opción --dry-run no realice cambios en la base de datos ni envíe correos.
        """
        listing_warn = self.create_listing(title="Aviso DryRun", days_ago=85, warning_sent=False)
        listing_del = self.create_listing(title="Eliminar DryRun", days_ago=95)

        call_command("manage_marketplace_lifecycle", dry_run=True)

        mock_send_email.assert_not_called()

        listing_warn.refresh_from_db()
        self.assertFalse(listing_warn.expiration_warning_sent)

        self.assertTrue(Listing.objects.filter(pk=listing_del.pk).exists())

    def test_celery_task_and_beat_schedule_configuration(self):
        """
        Valida que la tarea Celery Beat esté registrada para las 4:00 AM UTC
        y que la tarea manage_marketplace_lifecycle_task ejecute el comando.
        """
        schedule = celery_app.conf.beat_schedule
        self.assertIn("manage-marketplace-lifecycle-daily-at-4am", schedule)

        config = schedule["manage-marketplace-lifecycle-daily-at-4am"]
        self.assertEqual(config["task"], "marketplace.tasks.manage_marketplace_lifecycle_task")
        self.assertEqual(config["schedule"], crontab(hour=4, minute=0))

        # Verificar ejecución de la tarea Celery
        with patch("marketplace.tasks.call_command") as mock_call:
            from marketplace.tasks import manage_marketplace_lifecycle_task

            res = manage_marketplace_lifecycle_task.apply().get()
            mock_call.assert_called_once_with("manage_marketplace_lifecycle")
            self.assertEqual(res, "Marketplace lifecycle managed successfully")
