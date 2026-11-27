import logging
import os
import shutil
import time
from email.mime.image import MIMEImage
from pathlib import Path

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management import call_command
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from aficionados_network.utils.mailer import send_hubs_email_async

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=5,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def send_email_task(
    self,
    subject,
    recipient_email,
    recipient_username,
    message_body,
    action_url,
    template_name="general/emails/notification_email.html",
    extra_context=None,
):
    """
    Tarea asíncrona de Celery para enviar correos transaccionales con
    reintentos exponenciales automáticos y jitter.
    """
    logger.info(
        f"[Celery] Enviando correo a {recipient_email} - Intento {self.request.retries + 1}/5"
    )
    from aficionados_network.utils.site import build_absolute_url

    if action_url:
        action_url = build_absolute_url(action_url)

    context = {
        "recipient_name": recipient_username,
        "message_body": message_body,
        "action_url": action_url,
    }
    if extra_context and isinstance(extra_context, dict):
        context.update(extra_context)

    html_content = render_to_string(template_name, context)

    txt_template_name = template_name.rsplit(".", 1)[0] + ".txt"
    try:
        text_content = render_to_string(txt_template_name, context)
    except Exception:
        text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
    )
    email.attach_alternative(html_content, "text/html")

    logo_path = os.path.join(settings.BASE_DIR, "static", "img", "logo_hubs_email.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_image = MIMEImage(f.read())
            logo_image.add_header("Content-ID", "<logo_hubs_email>")
            email.attach(logo_image)

    # Si falla, lanza la excepción para que Celery active autoretry_for
    email.send(fail_silently=False)
    logger.info(f"[Celery] Correo enviado exitosamente a {recipient_email}")
    return f"Sent to {recipient_email}"


@shared_task(
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
)
def clear_expired_sessions_task(self):
    """
    Tarea periódica de mantenimiento en Celery Beat para eliminar sesiones
    expiradas de la base de datos (django_session) mediante el comando clearsessions.
    """
    logger.info("[Celery Beat] Iniciando limpieza periódica de sesiones expiradas...")
    try:
        call_command("clearsessions")
        logger.info(
            "[Celery Beat] Limpieza periódica de sesiones expiradas completada con éxito."
        )
        return "Expired sessions cleaned successfully"
    except Exception as exc:
        logger.error(
            f"[Celery Beat] Error durante la ejecución de clearsessions: {exc}",
            exc_info=True,
        )
        raise exc


@shared_task(
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def clean_temp_media_files_task(self, max_age_hours=48):
    """
    Tarea periódica de mantenimiento para eliminar archivos temporales huérfanos
    en MEDIA_ROOT / 'temp' con más de max_age_hours horas de antigüedad (por defecto 48h).
    Bajo ninguna circunstancia toca otros directorios de MEDIA_ROOT.
    """
    media_root = Path(settings.MEDIA_ROOT).resolve()
    temp_dir = (media_root / "temp").resolve()

    # Seguridad estricta: verificar que temp_dir reside dentro de media_root
    try:
        temp_dir.relative_to(media_root)
    except ValueError:
        logger.error(
            f"[Celery Beat] Ruta de temp_dir insegura o fuera de media_root: {temp_dir}"
        )
        return "Invalid temp directory path"

    if not temp_dir.exists() or not temp_dir.is_dir():
        logger.info(
            f"[Celery Beat] Directorio temporal {temp_dir} no existe. Nada que limpiar."
        )
        return "Temp directory does not exist"

    now = time.time()
    cutoff_time = now - (max_age_hours * 3600)
    deleted_files_count = 0

    logger.info(
        f"[Celery Beat] Iniciando limpieza de archivos temporales en {temp_dir} (> {max_age_hours} horas)..."
    )

    for item in temp_dir.rglob("*"):
        try:
            # Asegurar que cada archivo resuelto pertenece estrictamente a temp_dir
            resolved_item = item.resolve()
            resolved_item.relative_to(temp_dir)

            if item.is_file():
                stat = item.stat()
                if stat.st_mtime < cutoff_time:
                    item.unlink()
                    deleted_files_count += 1
                    logger.debug(f"[Celery Beat] Archivo temporal eliminado: {item}")
        except Exception as file_err:
            logger.warning(
                f"[Celery Beat] Error al procesar o eliminar archivo temporal {item}: {file_err}"
            )

    logger.info(
        f"[Celery Beat] Limpieza de temporales completada. Archivos eliminados: {deleted_files_count}"
    )
    return f"Cleaned {deleted_files_count} temporary media files"


@shared_task(
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def check_disk_usage_task(self):
    """
    Tarea periódica de monitoreo del espacio en disco usando shutil.disk_usage(settings.BASE_DIR).
    Registra:
      - Log WARNING al superar el 75% de ocupación.
      - Log CRITICAL al superar el 90% de ocupación.
    """
    base_dir = str(settings.BASE_DIR)
    logger.info(f"[Celery Beat] Verificando uso de disco en {base_dir}...")
    try:
        usage = shutil.disk_usage(base_dir)
        total_gb = usage.total / (1024**3)
        used_gb = usage.used / (1024**3)
        free_gb = usage.free / (1024**3)
        percent_used = (usage.used / usage.total) * 100 if usage.total > 0 else 0.0

        log_msg = (
            f"[Disk Monitor] Uso de disco: {percent_used:.2f}% "
            f"({used_gb:.2f} GB usado / {total_gb:.2f} GB total, {free_gb:.2f} GB libre) en {base_dir}"
        )

        if percent_used >= 90:
            logger.critical(f"CRITICAL DISK USAGE: {log_msg}")
        elif percent_used >= 75:
            logger.warning(f"HIGH DISK USAGE: {log_msg}")
        else:
            logger.info(f"NORMAL DISK USAGE: {log_msg}")

        # Despacho automático de correos a superusuarios ante umbral WARNING (>= 75%) o CRITICAL (>= 90%)
        if percent_used >= 75:
            try:
                from django.contrib.auth import get_user_model

                User = get_user_model()
                admin_emails = list(
                    User.objects.filter(is_superuser=True, is_active=True)
                    .exclude(email="")
                    .values_list("email", flat=True)
                )

                if not admin_emails:
                    admin_emails = [
                        email
                        for _, email in getattr(settings, "ADMINS", [])
                        if email and email.strip()
                    ]

                admin_emails = list(dict.fromkeys(admin_emails))

                if not admin_emails:
                    logger.warning(
                        "[Disk Monitor] Uso de disco elevado pero no se encontraron superusuarios "
                        "activos ni correos en settings.ADMINS para despachar la alerta."
                    )
                else:
                    if percent_used >= 90:
                        severity = "CRITICAL"
                        subject = (
                            f"[ALERTA CRÍTICA] Espacio en disco al {percent_used:.1f}% en Hubs & Clicks"
                        )
                    else:
                        severity = "WARNING"
                        subject = (
                            f"[AVISO] Espacio en disco al {percent_used:.1f}% en Hubs & Clicks"
                        )

                    message_body = (
                        f"Nivel de alerta: {severity}\n"
                        f"Porcentaje de ocupación: {percent_used:.1f}%\n"
                        f"Espacio usado: {used_gb:.2f} GB\n"
                        f"Espacio libre: {free_gb:.2f} GB\n"
                        f"Espacio total: {total_gb:.2f} GB\n"
                        f"Ruta del sistema verificada: {base_dir}\n\n"
                        f"Acciones sugeridas de mitigación:\n"
                        f"- Purgar imágenes y contenedores dangling de Docker (`docker system prune -f`).\n"
                        f"- Revisar y rotar backups antiguos del sistema.\n"
                        f"- Inspeccionar almacenamiento y logs en MariaDB."
                    )

                    for email in admin_emails:
                        send_hubs_email_async(
                            subject=subject,
                            recipient=email,
                            message_body=message_body,
                            action_url="/admin/",
                        )
            except Exception as mail_err:
                logger.error(
                    f"[Disk Monitor] Error al despachar correos de alerta de espacio en disco: {mail_err}",
                    exc_info=True,
                )

        return {
            "total_bytes": usage.total,
            "used_bytes": usage.used,
            "free_bytes": usage.free,
            "percent_used": round(percent_used, 2),
        }
    except Exception as exc:
        logger.error(
            f"[Celery Beat] Error al chequear uso de disco en {base_dir}: {exc}",
            exc_info=True,
        )
        raise exc


# Exponer la tarea de recordatorio de eventos para conveniencia e interoperabilidad
from posts.tasks import send_event_reminders_task  # noqa: E402, F401
