"""
Non-blocking asynchronous email utility for Aficionados Network.
Dispatches transactional emails in a background worker pool so slow SMTP connections
(such as Gmail) never block HTTP request cycles.
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

# Pool de hilos ligero para despachar correos en segundo plano sin bloquear el worker web
_email_executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="mail_worker")


def _send_hubs_email_sync(subject, recipient_email, recipient_username, message_body, action_url):
    try:
        context = {
            "recipient_name": recipient_username,
            "message_body": message_body,
            "action_url": action_url,
        }
        html_content = render_to_string("general/emails/notification_email.html", context)
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

        email.send(fail_silently=True)
    except Exception as e:
        logger.error(f"Error enviando correo en background a {recipient_email}: {e}", exc_info=True)


def send_hubs_email_async(subject, recipient, message_body, action_url):
    """
    Envía un correo con la plantilla corporativa de Hubs&Clicks de forma no bloqueante.
    Retorna inmediatamente al usuario mientras el correo se despacha en segundo plano.
    """
    if not recipient or not getattr(recipient, "email", None):
        return

    _email_executor.submit(
        _send_hubs_email_sync,
        subject=subject,
        recipient_email=recipient.email,
        recipient_username=getattr(recipient, "username", "Usuario"),
        message_body=message_body,
        action_url=action_url,
    )

