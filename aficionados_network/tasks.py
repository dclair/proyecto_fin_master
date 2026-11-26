import logging
import os
from email.mime.image import MIMEImage

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management import call_command
from django.template.loader import render_to_string
from django.utils.html import strip_tags

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
        logger.info("[Celery Beat] Limpieza periódica de sesiones expiradas completada con éxito.")
        return "Expired sessions cleaned successfully"
    except Exception as exc:
        logger.error(
            f"[Celery Beat] Error durante la ejecución de clearsessions: {exc}",
            exc_info=True,
        )
        raise exc


# Exponer la tarea de recordatorio de eventos para conveniencia e interoperabilidad
from posts.tasks import send_event_reminders_task  # noqa: E402, F401

