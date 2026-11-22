"""
Non-blocking asynchronous email utility for Aficionados Network.
Dispatches transactional emails via Celery tasks with exponential backoff retries,
and provides an in-process ThreadPoolExecutor fallback if Celery/broker is temporarily unavailable.
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from email.mime.image import MIMEImage

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

# Pool de hilos ligero de contingencia para despachar correos si Celery/Redis no responde
_email_executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="mail_fallback")


def _send_hubs_email_sync(
    subject,
    recipient_email,
    recipient_username,
    message_body,
    action_url,
    template_name="general/emails/notification_email.html",
    extra_context=None,
):
    try:
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

        email.send(fail_silently=False)
    except Exception as e:
        logger.error(f"Error enviando correo en worker fallback a {recipient_email}: {e}", exc_info=True)


def send_hubs_email_async(
    subject,
    recipient,
    message_body,
    action_url,
    template_name="general/emails/notification_email.html",
    extra_context=None,
):
    """
    Envía un correo con la plantilla corporativa de Hubs&Clicks de forma no bloqueante.
    Prioriza el encolamiento en Celery para reintentos y persistencia;
    si Celery no está disponible, utiliza ThreadPoolExecutor local como fallback.
    """
    if isinstance(recipient, str):
        recipient_email = recipient
        recipient_username = recipient.split("@")[0]
    elif recipient and getattr(recipient, "email", None):
        recipient_email = recipient.email
        recipient_username = getattr(recipient, "username", "Usuario")
    else:
        return

    try:
        from aficionados_network.tasks import send_email_task
        send_email_task.delay(
            subject=subject,
            recipient_email=recipient_email,
            recipient_username=recipient_username,
            message_body=message_body,
            action_url=action_url,
            template_name=template_name,
            extra_context=extra_context,
        )
    except Exception as e:
        logger.warning(
            f"Celery no disponible para encolar correo a {recipient_email} ({e}). "
            f"Activando ThreadPoolExecutor de contingencia."
        )
        _email_executor.submit(
            _send_hubs_email_sync,
            subject=subject,
            recipient_email=recipient_email,
            recipient_username=recipient_username,
            message_body=message_body,
            action_url=action_url,
            template_name=template_name,
            extra_context=extra_context,
        )
