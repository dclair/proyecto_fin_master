import logging
import os
from email.mime.image import MIMEImage

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
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
):
    """
    Tarea asíncrona de Celery para enviar correos transaccionales con
    reintentos exponenciales automáticos y jitter.
    """
    logger.info(
        f"[Celery] Enviando correo a {recipient_email} - Intento {self.request.retries + 1}/5"
    )
    context = {
        "recipient_name": recipient_username,
        "message_body": message_body,
        "action_url": action_url,
    }
    html_content = render_to_string(template_name, context)
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

