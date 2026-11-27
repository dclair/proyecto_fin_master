import os
import shutil
import tempfile
import time
from collections import namedtuple
from pathlib import Path
from unittest.mock import patch

from celery.schedules import crontab
from django.conf import settings
from django.test import TestCase, override_settings

from aficionados_network.celery import app as celery_app
from aficionados_network.tasks import (
    check_disk_usage_task,
    clean_temp_media_files_task,
)

DiskUsageResult = namedtuple("DiskUsageResult", ["total", "used", "free"])


@override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)
class MaintenanceTasksTests(TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.media_dir = Path(self.test_dir) / "media"
        self.media_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_clean_temp_media_files_removes_old_files_only(self):
        """
        Verifica que clean_temp_media_files_task elimine únicamente archivos en MEDIA_ROOT/temp
        con antigüedad superior a 48 horas, preservando archivos recientes y archivos fuera de temp/.
        """
        with override_settings(MEDIA_ROOT=self.media_dir):
            temp_dir = self.media_dir / "temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            nested_temp_dir = temp_dir / "nested"
            nested_temp_dir.mkdir(parents=True, exist_ok=True)

            avatars_dir = self.media_dir / "avatars"
            avatars_dir.mkdir(parents=True, exist_ok=True)

            # Archivo 1: en temp/ con más de 48h -> DEBE ELIMINARSE
            old_temp_file = temp_dir / "old_temp.txt"
            old_temp_file.write_text("old temp content")
            old_mtime = time.time() - (50 * 3600)
            os.utime(old_temp_file, (old_mtime, old_mtime))

            # Archivo 2: en temp/nested/ con más de 48h -> DEBE ELIMINARSE
            old_nested_file = nested_temp_dir / "old_nested.txt"
            old_nested_file.write_text("old nested content")
            nested_mtime = time.time() - (72 * 3600)
            os.utime(old_nested_file, (nested_mtime, nested_mtime))

            # Archivo 3: en temp/ con menos de 48h (10h) -> DEBE PRESERVARSE
            recent_temp_file = temp_dir / "recent_temp.txt"
            recent_temp_file.write_text("recent temp content")
            recent_mtime = time.time() - (10 * 3600)
            os.utime(recent_temp_file, (recent_mtime, recent_mtime))

            # Archivo 4: en avatars/ (fuera de temp/) con más de 100h -> DEBE PRESERVARSE INTACTO
            avatar_file = avatars_dir / "user_avatar.png"
            avatar_file.write_text("avatar content")
            avatar_mtime = time.time() - (100 * 3600)
            os.utime(avatar_file, (avatar_mtime, avatar_mtime))

            # Ejecutar tarea de limpieza
            result = clean_temp_media_files_task(max_age_hours=48)
            self.assertEqual(result, "Cleaned 2 temporary media files")

            # Aserciones de eliminación y preservación
            self.assertFalse(
                old_temp_file.exists(),
                "El archivo temporal con más de 48h debe haber sido eliminado.",
            )
            self.assertFalse(
                old_nested_file.exists(),
                "El archivo temporal anidado con más de 48h debe haber sido eliminado.",
            )
            self.assertTrue(
                recent_temp_file.exists(),
                "El archivo temporal reciente (< 48h) debe conservarse.",
            )
            self.assertTrue(
                avatar_file.exists(),
                "Archivos fuera de MEDIA_ROOT/temp NUNCA deben eliminarse.",
            )

    def test_clean_temp_media_files_non_existent_temp_dir(self):
        """
        Verifica que la tarea maneje con gracia cuando MEDIA_ROOT/temp no existe.
        """
        with override_settings(MEDIA_ROOT=self.media_dir):
            # Asegurar que temp/ no existe
            temp_dir = self.media_dir / "temp"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

            result = clean_temp_media_files_task()
            self.assertEqual(result, "Temp directory does not exist")

    def test_check_disk_usage_task_normal_threshold(self):
        """
        Verifica que cuando el uso de disco es < 75%, se registre log a nivel INFO.
        """
        mock_usage = DiskUsageResult(total=1000, used=500, free=500)  # 50%
        with patch("shutil.disk_usage", return_value=mock_usage):
            with self.assertLogs("aficionados_network.tasks", level="INFO") as cm:
                res = check_disk_usage_task()
                self.assertEqual(res["percent_used"], 50.0)
                self.assertTrue(
                    any("NORMAL DISK USAGE" in msg for msg in cm.output),
                    "Debe registrar log informativo para uso normal.",
                )

    def test_check_disk_usage_task_warning_threshold(self):
        """
        Verifica que cuando el uso de disco es >= 75% y < 90%, se registre log a nivel WARNING.
        """
        mock_usage = DiskUsageResult(total=1000, used=800, free=200)  # 80%
        with patch("shutil.disk_usage", return_value=mock_usage):
            with self.assertLogs("aficionados_network.tasks", level="WARNING") as cm:
                res = check_disk_usage_task()
                self.assertEqual(res["percent_used"], 80.0)
                self.assertTrue(
                    any("HIGH DISK USAGE" in msg for msg in cm.output),
                    "Debe registrar log de advertencia (WARNING) al superar el 75%.",
                )

    def test_check_disk_usage_task_critical_threshold(self):
        """
        Verifica que cuando el uso de disco es >= 90%, se registre log a nivel CRITICAL.
        """
        mock_usage = DiskUsageResult(total=1000, used=950, free=50)  # 95%
        with patch("shutil.disk_usage", return_value=mock_usage):
            with self.assertLogs("aficionados_network.tasks", level="CRITICAL") as cm:
                res = check_disk_usage_task()
                self.assertEqual(res["percent_used"], 95.0)
                self.assertTrue(
                    any("CRITICAL DISK USAGE" in msg for msg in cm.output),
                    "Debe registrar log crítico (CRITICAL) al superar el 90%.",
                )

    def test_check_disk_usage_task_raises_on_shutil_error(self):
        """
        Verifica que si shutil.disk_usage falla, se registre error y se relance la excepción.
        """
        with patch("shutil.disk_usage", side_effect=OSError("Disk access failure")):
            with self.assertRaises(OSError):
                check_disk_usage_task()

    def test_beat_schedule_maintenance_tasks_configuration(self):
        """
        Valida que todas las tareas de mantenimiento y monitoreo estén programadas
        en Celery Beat (app.conf.beat_schedule) en sus horarios correspondientes.
        """
        schedule_conf = celery_app.conf.beat_schedule

        # 1. Limpieza de sesiones expiradas: 03:00 AM
        self.assertIn("clear-expired-sessions-daily-at-3am", schedule_conf)
        entry_sessions = schedule_conf["clear-expired-sessions-daily-at-3am"]
        self.assertEqual(
            entry_sessions["task"],
            "aficionados_network.tasks.clear_expired_sessions_task",
        )
        self.assertEqual(entry_sessions["schedule"].hour, {3})
        self.assertEqual(entry_sessions["schedule"].minute, {0})

        # 2. Limpieza de notificaciones leídas: 03:30 AM
        self.assertIn("clean-old-read-notifications-daily-at-3-30am", schedule_conf)
        entry_notif = schedule_conf["clean-old-read-notifications-daily-at-3-30am"]
        self.assertEqual(
            entry_notif["task"],
            "notifications.tasks.clean_old_read_notifications_task",
        )
        self.assertEqual(entry_notif["schedule"].hour, {3})
        self.assertEqual(entry_notif["schedule"].minute, {30})

        # 3. Ciclo de vida de marketplace: 04:00 AM
        self.assertIn("manage-marketplace-lifecycle-daily-at-4am", schedule_conf)
        entry_market = schedule_conf["manage-marketplace-lifecycle-daily-at-4am"]
        self.assertEqual(
            entry_market["task"],
            "marketplace.tasks.manage_marketplace_lifecycle_task",
        )
        self.assertEqual(entry_market["schedule"].hour, {4})
        self.assertEqual(entry_market["schedule"].minute, {0})

        # 4. Limpieza de media temporal: 04:30 AM
        self.assertIn("clean-temp-media-daily-at-4-30am", schedule_conf)
        entry_media = schedule_conf["clean-temp-media-daily-at-4-30am"]
        self.assertEqual(
            entry_media["task"],
            "aficionados_network.tasks.clean_temp_media_files_task",
        )
        self.assertEqual(entry_media["schedule"].hour, {4})
        self.assertEqual(entry_media["schedule"].minute, {30})

        # 5. Monitoreo de disco: 05:00 AM
        self.assertIn("check-disk-usage-daily-at-5am", schedule_conf)
        entry_disk = schedule_conf["check-disk-usage-daily-at-5am"]
        self.assertEqual(
            entry_disk["task"],
            "aficionados_network.tasks.check_disk_usage_task",
        )
        self.assertEqual(entry_disk["schedule"].hour, {5})
        self.assertEqual(entry_disk["schedule"].minute, {0})

        # 6. Recordatorios de eventos: 08:00 AM
        self.assertIn("send-event-reminders-daily-at-8am", schedule_conf)
        entry_events = schedule_conf["send-event-reminders-daily-at-8am"]
        self.assertEqual(
            entry_events["task"],
            "posts.tasks.send_event_reminders_task",
        )
        self.assertEqual(entry_events["schedule"].hour, {8})
        self.assertEqual(entry_events["schedule"].minute, {0})
