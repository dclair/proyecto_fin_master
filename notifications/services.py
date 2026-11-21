import logging
from django.conf import settings
from django.urls import reverse
from aficionados_network.utils.mailer import send_hubs_email_async
from .models import Notification

logger = logging.getLogger(__name__)


class NotificationDispatcher:
    """
    Capa de servicio centralizada para el despacho consistente y desacoplado
    de notificaciones in-app (campanita) y correos transaccionales asíncronos vía Celery.
    """

    @classmethod
    def dispatch(
        cls,
        notification_type: str,
        sender,
        recipient,
        message: str = None,
        post=None,
        event=None,
        review=None,
        comment=None,
        article=None,
        send_email: bool = False,
        email_subject: str = None,
        email_body: str = None,
        action_url: str = None,
    ):
        """
        Despacha una notificación in-app y opcionalmente un correo electrónico por Celery.

        Reglas de negocio garantizadas:
        - 1. Anti auto-notificación: Si sender == recipient, se descarta silenciosamente.
        - 2. Anti-spam: Los 'likes' jamás disparan correos electrónicos.
        - 3. Resiliencia: Fallos en el encolamiento de correo no impiden la creación in-app.
        """
        if not recipient:
            return None

        # 1. Regla anti auto-notificación (evita que un usuario se notifique a sí mismo por sus propias acciones)
        if sender and sender == recipient and notification_type in [
            "like",
            "comment",
            "follow",
            "event",
            "review",
            "chat_request",
            "article_comment",
            "article_rating",
        ]:
            return None

        # 2. Regla anti-spam estricta: los likes nunca envían email
        if notification_type == "like":
            send_email = False

        # 2.1 Validación defensiva: Notification.comment apunta a posts.Comment, no a EventComment
        if comment and getattr(comment, "_meta", None) and comment._meta.model_name != "comment":
            comment = None

        # 3. Creación in-app (modelo Notification)
        try:
            notification = Notification.objects.create(
                recipient=recipient,
                sender=sender,
                notification_type=notification_type,
                post=post,
                event=event,
                review=review,
                comment=comment,
                article=article,
                message=message,
            )
        except Exception as e:
            logger.error(
                f"[NotificationDispatcher] Error creando notificación in-app ({notification_type}): {e}",
                exc_info=True,
            )
            notification = None

        # 4. Despacho por email asíncrono (Celery)
        if send_email and getattr(recipient, "email", None):
            # Derivación inteligente de URL de acción si no fue provista
            if not action_url:
                try:
                    if event:
                        action_url = reverse("posts:event_detail", args=[event.id])
                    elif post:
                        action_url = reverse("posts:post_detail", args=[post.id])
                    elif article:
                        action_url = reverse("library:article_detail", args=[article.slug])
                    else:
                        action_url = reverse("notifications:list")
                except Exception:
                    action_url = "/"

            if not email_subject:
                sender_name = getattr(sender, "username", "Hubs & Clicks") if sender else "Hubs & Clicks"
                email_subject = f"🔔 Nueva notificación de @{sender_name}"

            if not email_body:
                email_body = message or (
                    notification.text
                    if notification
                    else "Tienes una nueva actualización en Aficionados Network."
                )

            try:
                send_hubs_email_async(
                    subject=email_subject,
                    recipient=recipient,
                    message_body=email_body,
                    action_url=action_url,
                )
            except Exception as e:
                logger.error(
                    f"[NotificationDispatcher] Error despachando correo asíncrono a {recipient.email}: {e}",
                    exc_info=True,
                )

        return notification
