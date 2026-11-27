from datetime import timedelta
from unittest.mock import patch

from celery.schedules import crontab
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils import timezone

from aficionados_network.celery import app as celery_app
from notifications.models import Notification
from notifications.tasks import clean_old_read_notifications_task


@override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)
class CleanOldReadNotificationsTaskTests(TestCase):
    def setUp(self):
        self.user_sender = User.objects.create_user(
            username="sender_user",
            email="sender@example.com",
            password="testpass123",
        )
        self.user_recipient = User.objects.create_user(
            username="recipient_user",
            email="recipient@example.com",
            password="testpass123",
        )

    def test_clean_old_read_notifications_filters_correctly(self):
        """
        Verifica que solo se eliminen notificaciones con is_read=True y antigüedad > 90 días.
        Las no leídas o recientes deben preservarse.
        """
        now = timezone.now()

        # 1. Notificación leída y antigua (> 90 días): DEBE ELIMINARSE
        n_old_read = Notification.objects.create(
            sender=self.user_sender,
            recipient=self.user_recipient,
            notification_type="follow",
            is_read=True,
        )
        Notification.objects.filter(pk=n_old_read.pk).update(
            created_at=now - timedelta(days=95)
        )

        # 2. Notificación leída pero reciente (< 90 días): DEBE PRESERVARSE
        n_recent_read = Notification.objects.create(
            sender=self.user_sender,
            recipient=self.user_recipient,
            notification_type="like",
            is_read=True,
        )
        Notification.objects.filter(pk=n_recent_read.pk).update(
            created_at=now - timedelta(days=30)
        )

        # 3. Notificación no leída y antigua (> 90 días): DEBE PRESERVARSE
        n_old_unread = Notification.objects.create(
            sender=self.user_sender,
            recipient=self.user_recipient,
            notification_type="comment",
            is_read=False,
        )
        Notification.objects.filter(pk=n_old_unread.pk).update(
            created_at=now - timedelta(days=120)
        )

        # 4. Notificación no leída y reciente (< 90 días): DEBE PRESERVARSE
        n_recent_unread = Notification.objects.create(
            sender=self.user_sender,
            recipient=self.user_recipient,
            notification_type="badge",
            is_read=False,
        )
        Notification.objects.filter(pk=n_recent_unread.pk).update(
            created_at=now - timedelta(days=5)
        )

        # Ejecutar la tarea de limpieza
        result = clean_old_read_notifications_task()
        self.assertIn("Cleaned 1 old read notifications", result)

        # Aserciones de persistencia
        self.assertFalse(
            Notification.objects.filter(pk=n_old_read.pk).exists(),
            "La notificación leída con más de 90 días debe haber sido eliminada.",
        )
        self.assertTrue(
            Notification.objects.filter(pk=n_recent_read.pk).exists(),
            "La notificación leída reciente debe preservarse.",
        )
        self.assertTrue(
            Notification.objects.filter(pk=n_old_unread.pk).exists(),
            "La notificación no leída antigua debe preservarse.",
        )
        self.assertTrue(
            Notification.objects.filter(pk=n_recent_unread.pk).exists(),
            "La notificación no leída reciente debe preservarse.",
        )

    def test_chunked_deletion(self):
        """
        Verifica que el borrado por lotes procese adecuadamente todas las notificaciones
        elegibles en fragmentos (chunk_size).
        """
        now = timezone.now()
        created_ids = []

        # Crear 7 notificaciones leídas con más de 90 días de antigüedad
        for i in range(7):
            n = Notification.objects.create(
                sender=self.user_sender,
                recipient=self.user_recipient,
                notification_type="follow",
                is_read=True,
            )
            created_ids.append(n.pk)

        Notification.objects.filter(pk__in=created_ids).update(
            created_at=now - timedelta(days=100)
        )

        # Ejecutar con chunk_size=3 para forzar múltiples iteraciones del bucle
        result = clean_old_read_notifications_task(days=90, chunk_size=3)
        self.assertEqual(result, "Cleaned 7 old read notifications")
        self.assertEqual(
            Notification.objects.filter(pk__in=created_ids).count(),
            0,
            "Todas las notificaciones leídas antiguas deben haber sido eliminadas tras el chunking.",
        )

    def test_task_raises_on_error_for_celery_retry(self):
        """
        Verifica que ante errores en la base de datos se lance la excepción para que
        Celery active la política autoretry_for.
        """
        with patch.object(
            Notification.objects, "filter", side_effect=RuntimeError("Database lock error")
        ):
            with self.assertRaises(RuntimeError):
                clean_old_read_notifications_task()

    def test_celery_beat_schedule_registration(self):
        """
        Verifica que la tarea clean_old_read_notifications_task esté registrada
        en app.conf.beat_schedule a las 03:30 AM todos los días.
        """
        schedule_conf = celery_app.conf.beat_schedule
        self.assertIn(
            "clean-old-read-notifications-daily-at-3-30am",
            schedule_conf,
            "La tarea de limpieza de notificaciones debe estar en beat_schedule.",
        )
        entry = schedule_conf["clean-old-read-notifications-daily-at-3-30am"]
        self.assertEqual(
            entry["task"],
            "notifications.tasks.clean_old_read_notifications_task",
        )
        schedule = entry["schedule"]
        self.assertIsInstance(schedule, crontab)
        self.assertEqual(schedule.hour, {3})
        self.assertEqual(schedule.minute, {30})
