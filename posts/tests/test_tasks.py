from datetime import timedelta
import tempfile
import shutil

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from celery.schedules import crontab

from aficionados_network.celery import app as celery_app
from notifications.models import Notification
from posts.models import Event, EventAttendance
from profiles.models import Hobby
from posts.tasks import send_event_reminders_task

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


def tearDownModule():
    shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)


@override_settings(
    DEBUG=True,
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@example.com",
    MEDIA_ROOT=TEMP_MEDIA_ROOT,
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class EventReminderTaskTests(TestCase):
    def setUp(self):
        # Limpiar bandeja de salida en memoria
        mail.outbox.clear()

        # Categoría / Hobby común
        self.hobby = Hobby.objects.create(name="Senderismo", slug="senderismo")

        # Usuarios
        self.organizer = User.objects.create_user(
            username="organizador",
            email="organizador@example.com",
            password="password123",
        )
        self.attendee_1 = User.objects.create_user(
            username="asistente1",
            email="asistente1@example.com",
            password="password123",
        )
        self.attendee_2 = User.objects.create_user(
            username="asistente2",
            email="asistente2@example.com",
            password="password123",
        )
        self.inactive_user = User.objects.create_user(
            username="inactivo",
            email="inactivo@example.com",
            password="password123",
            is_active=False,
        )

    def test_event_starting_within_24h_sends_reminder_to_attendees(self):
        """
        Validación a): Evento que arranca en las próximas 24hs envía recordatorio a los asistentes.
        """
        event_time = timezone.now() + timedelta(hours=14)
        event = Event.objects.create(
            title="Ruta por la Sierra",
            description="Caminata matutina.",
            location="Plaza Central",
            event_date=event_time,
            organizer=self.organizer,
            hobby=self.hobby,
        )
        # Inscribir a los asistentes
        EventAttendance.objects.create(
            event=event, user=self.attendee_1, attendance_type="physical"
        )
        EventAttendance.objects.create(
            event=event, user=self.attendee_2, attendance_type="physical"
        )

        sent_count = send_event_reminders_task()
        self.assertEqual(sent_count, 2)

        # Verificar estados de asistencias en base de datos
        att_1 = EventAttendance.objects.get(event=event, user=self.attendee_1)
        att_2 = EventAttendance.objects.get(event=event, user=self.attendee_2)
        self.assertTrue(att_1.reminder_sent)
        self.assertIsNotNone(att_1.reminder_sent_at)
        self.assertTrue(att_2.reminder_sent)
        self.assertIsNotNone(att_2.reminder_sent_at)

        # Verificar notificaciones in-app
        notifications = Notification.objects.filter(
            event=event, notification_type="event_reminder"
        )
        self.assertEqual(notifications.count(), 2)
        recipients = {n.recipient for n in notifications}
        self.assertEqual(recipients, {self.attendee_1, self.attendee_2})

        # Verificar emails enviados
        self.assertEqual(len(mail.outbox), 2)
        email_recipients = [msg.to[0] for msg in mail.outbox]
        self.assertIn("asistente1@example.com", email_recipients)
        self.assertIn("asistente2@example.com", email_recipients)
        for msg in mail.outbox:
            self.assertIn("Ruta por la Sierra", msg.subject)
            # Asegurar que se adjuntó versión HTML renderizada con el template dedicado
            self.assertTrue(any(alt[1] == "text/html" for alt in msg.alternatives))

    def test_event_starting_in_three_days_does_not_send_reminder(self):
        """
        Validación b.1): Eventos lejanos (en 3 días) NO envían recordatorio.
        """
        event_time = timezone.now() + timedelta(days=3)
        event = Event.objects.create(
            title="Ruta Futura Lejana",
            description="En tres días.",
            location="Parque",
            event_date=event_time,
            organizer=self.organizer,
            hobby=self.hobby,
        )
        EventAttendance.objects.create(
            event=event, user=self.attendee_1, attendance_type="physical"
        )

        sent_count = send_event_reminders_task()
        self.assertEqual(sent_count, 0)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(
            Notification.objects.filter(notification_type="event_reminder").count(), 0
        )
        att = EventAttendance.objects.get(event=event, user=self.attendee_1)
        self.assertFalse(att.reminder_sent)

    def test_past_event_does_not_send_reminder(self):
        """
        Validación b.2): Eventos pasados NO envían recordatorio.
        """
        event_time = timezone.now() - timedelta(hours=3)
        event = Event.objects.create(
            title="Ruta Ya Realizada",
            description="Evento de ayer.",
            location="Parque",
            event_date=event_time,
            organizer=self.organizer,
            hobby=self.hobby,
        )
        EventAttendance.objects.create(
            event=event, user=self.attendee_1, attendance_type="physical"
        )

        sent_count = send_event_reminders_task()
        self.assertEqual(sent_count, 0)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(
            Notification.objects.filter(notification_type="event_reminder").count(), 0
        )

    def test_canceled_and_soft_deleted_events_do_not_send_reminder(self):
        """
        Validación b.3): Eventos cancelados o eliminados dentro de 24hs NO envían recordatorio.
        """
        # Evento cancelado
        event_canceled = Event.objects.create(
            title="Ruta Cancelada",
            description="Suspendido por lluvia.",
            location="Montaña",
            event_date=timezone.now() + timedelta(hours=8),
            organizer=self.organizer,
            hobby=self.hobby,
            is_canceled=True,
        )
        EventAttendance.objects.create(
            event=event_canceled, user=self.attendee_1, attendance_type="physical"
        )

        # Evento soft-deleted
        event_deleted = Event.objects.create(
            title="Ruta Borrada",
            description="Borrado lógicamente.",
            location="Playa",
            event_date=timezone.now() + timedelta(hours=10),
            organizer=self.organizer,
            hobby=self.hobby,
            is_active=False,
            deleted_at=timezone.now(),
        )
        EventAttendance.objects.create(
            event=event_deleted, user=self.attendee_2, attendance_type="physical"
        )

        sent_count = send_event_reminders_task()
        self.assertEqual(sent_count, 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_idempotency_second_run_sends_nothing_additional(self):
        """
        Validación c): Idempotencia estricta. Una segunda ejecución inmediata o posterior
        no envía nada adicional ni duplica emails o notificaciones.
        """
        event = Event.objects.create(
            title="Quedada Idempotente",
            description="Prueba de no duplicación.",
            location="Plaza",
            event_date=timezone.now() + timedelta(hours=18),
            organizer=self.organizer,
            hobby=self.hobby,
        )
        EventAttendance.objects.create(
            event=event, user=self.attendee_1, attendance_type="physical"
        )

        # Primera ejecución
        first_run_sent = send_event_reminders_task()
        self.assertEqual(first_run_sent, 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            Notification.objects.filter(
                event=event, recipient=self.attendee_1, notification_type="event_reminder"
            ).count(),
            1,
        )

        # Limpiar la bandeja para aislar la segunda ejecución
        mail.outbox.clear()

        # Segunda ejecución inmediata (simulando reintento o doble ejecución de Beat)
        second_run_sent = send_event_reminders_task()
        self.assertEqual(second_run_sent, 0)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(
            Notification.objects.filter(
                event=event, recipient=self.attendee_1, notification_type="event_reminder"
            ).count(),
            1,
        )

        # Tercera prueba: simular reinicio de attendance con reminder_sent=False pero Notification preexistente
        att = EventAttendance.objects.get(event=event, user=self.attendee_1)
        att.reminder_sent = False
        att.save(update_fields=["reminder_sent"])

        third_run_sent = send_event_reminders_task()
        self.assertEqual(third_run_sent, 0)
        self.assertEqual(len(mail.outbox), 0)
        att.refresh_from_db()
        self.assertTrue(att.reminder_sent)

    def test_unregistered_and_inactive_users_do_not_receive_reminder(self):
        """
        Validación d): Usuarios no confirmados (inactivos) o desapuntados NO reciben recordatorio.
        """
        event = Event.objects.create(
            title="Quedada Control Asistentes",
            description="Verificar bajas e inactivos.",
            location="Parque",
            event_date=timezone.now() + timedelta(hours=12),
            organizer=self.organizer,
            hobby=self.hobby,
        )

        # 1. Asistente activo confirmado
        EventAttendance.objects.create(
            event=event, user=self.attendee_1, attendance_type="physical"
        )

        # 2. Usuario no confirmado / inactivo
        EventAttendance.objects.create(
            event=event, user=self.inactive_user, attendance_type="physical"
        )

        # 3. Usuario que se apuntó y luego se desapuntó (simulado borrando la asistencia)
        att_to_delete = EventAttendance.objects.create(
            event=event, user=self.attendee_2, attendance_type="physical"
        )
        att_to_delete.delete()  # Desapuntado

        sent_count = send_event_reminders_task()

        # Solo debe enviarse 1 recordatorio (al asistente 1 activo)
        self.assertEqual(sent_count, 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["asistente1@example.com"])

        # Ninguna notificación para el usuario inactivo ni para el desapuntado
        self.assertFalse(
            Notification.objects.filter(
                event=event, recipient=self.inactive_user
            ).exists()
        )
        self.assertFalse(
            Notification.objects.filter(
                event=event, recipient=self.attendee_2
            ).exists()
        )

    def test_online_event_template_rendering(self):
        """
        Verifica que para eventos online se renderiza el enlace y la plantilla dedicada.
        """
        event = Event.objects.create(
            title="Webinar Fotografía Nocturna",
            description="Sesión en streaming.",
            is_online=True,
            stream_url="https://meet.google.com/abc-defg-hij",
            event_date=timezone.now() + timedelta(hours=6),
            organizer=self.organizer,
            hobby=self.hobby,
        )
        EventAttendance.objects.create(
            event=event, user=self.attendee_1, attendance_type="online"
        )

        send_event_reminders_task()
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertIn("Webinar Fotografía Nocturna", sent_email.subject)
        self.assertIn("https://meet.google.com/abc-defg-hij", sent_email.body)
        html_alternative = [alt[0] for alt in sent_email.alternatives if alt[1] == "text/html"][0]
        self.assertIn("https://meet.google.com/abc-defg-hij", html_alternative)
        self.assertIn("Encuentro Online", html_alternative)

    def test_celery_beat_schedule_configuration(self):
        """
        Verifica la configuración de Celery Beat en app.conf.beat_schedule a las 08:00 AM.
        """
        schedule_conf = celery_app.conf.beat_schedule
        self.assertIn("send-event-reminders-daily-at-8am", schedule_conf)
        entry = schedule_conf["send-event-reminders-daily-at-8am"]
        self.assertEqual(entry["task"], "posts.tasks.send_event_reminders_task")
        # Verificar crontab
        schedule = entry["schedule"]
        self.assertIsInstance(schedule, crontab)
        self.assertEqual(schedule.hour, {8})
        self.assertEqual(schedule.minute, {0})
