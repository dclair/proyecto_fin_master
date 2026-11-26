from datetime import timedelta
from unittest.mock import patch

from celery.schedules import crontab
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from aficionados_network.celery import app as celery_app
from aficionados_network.tasks import clear_expired_sessions_task

User = get_user_model()


class SessionSecurityAndTimeoutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="sesion_test_user",
            email="sesion_test@example.com",
            password="SecurePassword123!",
        )

    def test_strict_session_security_settings(self):
        """
        Valida que los ajustes de seguridad y expiración de sesiones en settings
        cumplen estrictamente con los estándares requeridos.
        """
        self.assertEqual(
            settings.SESSION_COOKIE_AGE,
            3600,
            "SESSION_COOKIE_AGE debe ser de 3600 segundos (1 hora).",
        )
        self.assertIs(
            settings.SESSION_SAVE_EVERY_REQUEST,
            True,
            "SESSION_SAVE_EVERY_REQUEST debe ser True para renovar la sesión en cada request (rolling session).",
        )
        self.assertIs(
            settings.SESSION_EXPIRE_AT_BROWSER_CLOSE,
            True,
            "SESSION_EXPIRE_AT_BROWSER_CLOSE debe ser True para expirar al cerrar el navegador.",
        )
        self.assertIs(
            settings.SESSION_COOKIE_HTTPONLY,
            True,
            "SESSION_COOKIE_HTTPONLY debe ser True para mitigar robo de cookies por XSS.",
        )

    def test_celery_beat_schedule_configuration(self):
        """
        Valida que la tarea clear_expired_sessions_task esté programada en Celery Beat
        todos los días a las 03:00 AM sin alterar las tareas preexistentes.
        """
        schedule_conf = celery_app.conf.beat_schedule
        self.assertIn(
            "send-event-reminders-daily-at-8am",
            schedule_conf,
            "La tarea preexistente de recordatorios de eventos debe permanecer intacta.",
        )
        self.assertIn(
            "clear-expired-sessions-daily-at-3am",
            schedule_conf,
            "La tarea de limpieza de sesiones debe estar registrada en beat_schedule.",
        )

        entry = schedule_conf["clear-expired-sessions-daily-at-3am"]
        self.assertEqual(
            entry["task"],
            "aficionados_network.tasks.clear_expired_sessions_task",
        )
        schedule = entry["schedule"]
        self.assertIsInstance(schedule, crontab)
        self.assertEqual(schedule.hour, {3})
        self.assertEqual(schedule.minute, {0})

    def test_rolling_session_renews_expire_date_on_authenticated_request(self):
        """
        Valida el comportamiento rolling: crear sesión con usuario autenticado,
        registrar expire_date inicial, simular el paso del tiempo dentro de la ventana activa,
        hacer un segundo request autenticado y comprobar que expire_date se renueva hacia el futuro.
        """
        self.client.force_login(self.user)
        session_key = self.client.session.session_key
        self.assertTrue(session_key, "Debe existir un session_key tras el login.")

        session_record = Session.objects.get(session_key=session_key)
        initial_expire = session_record.expire_date

        # Simulamos que transcurrieron 20 minutos (adelantando el tiempo de envejecimiento de la sesión en DB)
        simulated_elapsed_expire = initial_expire - timedelta(minutes=20)
        session_record.expire_date = simulated_elapsed_expire
        session_record.save(update_fields=["expire_date"])

        # Realizamos un segundo request autenticado a una vista protegida
        response = self.client.get(reverse("profiles:profile_edit"))
        self.assertEqual(response.status_code, 200)

        # Recargamos la sesión desde la base de datos
        updated_session = Session.objects.get(session_key=session_key)
        self.assertGreater(
            updated_session.expire_date,
            simulated_elapsed_expire,
            "El expire_date de la sesión debe renovarse hacia el futuro tras el nuevo request.",
        )
        # Comprobar que la nueva fecha de expiración se extendió a aproximadamente 1 hora desde ahora
        expected_min_expire = timezone.now() + timedelta(seconds=3500)
        self.assertGreaterEqual(
            updated_session.expire_date,
            expected_min_expire,
            "La expiración debe extenderse ~1 hora completa (SESSION_COOKIE_AGE=3600) desde el request.",
        )

    def test_session_expiration_after_inactivity(self):
        """
        Valida la expiración tras inactividad: simular el paso del tiempo (> 3600s modificando
        el expire_date de la sesión en base de datos), realizar un request a una vista protegida,
        y constatar que el usuario ya NO está autenticado y es redirigido al login.
        """
        self.client.force_login(self.user)
        session_key = self.client.session.session_key
        self.assertTrue(session_key)

        # Modificamos el expire_date en la base de datos simulando > 3600s de inactividad (pasado)
        session_record = Session.objects.get(session_key=session_key)
        session_record.expire_date = timezone.now() - timedelta(minutes=5)
        session_record.save(update_fields=["expire_date"])

        # Hacemos una petición a la vista protegida que requiere login
        target_url = reverse("profiles:profile_edit")
        response = self.client.get(target_url)

        # Constatar que es redirigido al login (302 Found)
        self.assertEqual(
            response.status_code,
            302,
            "Un usuario con sesión expirada debe ser redirigido.",
        )
        self.assertIn(
            settings.LOGIN_URL,
            response.url,
            f"La redirección debe apuntar al login ({settings.LOGIN_URL}).",
        )

        # Constatar que en el request el usuario ya NO está autenticado
        self.assertFalse(
            response.wsgi_request.user.is_authenticated,
            "El usuario en el request no debe estar autenticado tras expirar la sesión.",
        )

    def test_clear_expired_sessions_task_cleans_only_expired(self):
        """
        Valida que clear_expired_sessions_task elimine las sesiones expiradas
        de django_session manteniendo las sesiones vigentes intactas.
        """
        now = timezone.now()
        # Sesión activa 1
        active_1 = Session.objects.create(
            session_key="active_session_test_1",
            session_data="data_active_1",
            expire_date=now + timedelta(hours=1),
        )
        # Sesión activa 2
        active_2 = Session.objects.create(
            session_key="active_session_test_2",
            session_data="data_active_2",
            expire_date=now + timedelta(minutes=15),
        )
        # Sesión expirada 1 (hace 10 minutos)
        expired_1 = Session.objects.create(
            session_key="expired_session_test_1",
            session_data="data_expired_1",
            expire_date=now - timedelta(minutes=10),
        )
        # Sesión expirada 2 (hace 3 días)
        expired_2 = Session.objects.create(
            session_key="expired_session_test_2",
            session_data="data_expired_2",
            expire_date=now - timedelta(days=3),
        )

        # Ejecutar la tarea periódica
        result = clear_expired_sessions_task()
        self.assertEqual(result, "Expired sessions cleaned successfully")

        # Verificar que las sesiones expiradas fueron eliminadas
        self.assertFalse(
            Session.objects.filter(session_key=expired_1.session_key).exists(),
            "La sesión expirada 1 debió ser eliminada por clearsessions.",
        )
        self.assertFalse(
            Session.objects.filter(session_key=expired_2.session_key).exists(),
            "La sesión expirada 2 debió ser eliminada por clearsessions.",
        )

        # Verificar que las sesiones activas permanecen en la base de datos
        self.assertTrue(
            Session.objects.filter(session_key=active_1.session_key).exists(),
            "La sesión activa 1 debe conservarse intacta.",
        )
        self.assertTrue(
            Session.objects.filter(session_key=active_2.session_key).exists(),
            "La sesión activa 2 debe conservarse intacta.",
        )

    def test_clear_expired_sessions_task_error_handling(self):
        """
        Valida que si call_command('clearsessions') genera una excepción,
        la tarea capture el error en logs y lo propague para permitir el autoretry de Celery.
        """
        with patch("aficionados_network.tasks.call_command", side_effect=RuntimeError("DB Lock error")):
            with self.assertLogs("aficionados_network.tasks", level="ERROR") as cm:
                with self.assertRaises(RuntimeError):
                    clear_expired_sessions_task()
                self.assertTrue(
                    any("Error durante la ejecución de clearsessions" in msg or "DB Lock error" in msg for msg in cm.output),
                    "Se debe registrar un log descriptivo a nivel ERROR ante excepciones.",
                )
