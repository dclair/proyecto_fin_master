from django.db import models

# from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    CHOICES = (
        ("follow", "Seguimiento"),
        ("like", "Me gusta"),
        ("comment", "Comentario"),
        ("event", "Quedada"),
        ("review", "Valoración"),
        ("badge", "Logro Obtenido"),
        ("article_comment", "Comentario en Artículo"),
        ("article_rating", "Valoración de Artículo"),
        ("chat_request", "Solicitud de Chat"),
        ("chat_accepted", "Acceso al Chat Aceptado"),
        ("chat_rejected", "Acceso al Chat Rechazado"),
        ("event_reminder", "Recordatorio de quedada"),
    )

    # Añadimos verbose_name a cada campo
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Destinatario",
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        verbose_name="Remitente",
    )
    notification_type = models.CharField(
        max_length=20, choices=CHOICES, verbose_name="Tipo de notificación"
    )
    post = models.ForeignKey(
        "posts.Posts",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Publicación",
    )

    event = models.ForeignKey(
        "posts.Event",  # Apuntamos al modelo que creamos antes
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Quedada",
    )
    # valoraciones
    review = models.ForeignKey(
        "profiles.Review",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Valoración",
    )
    article = models.ForeignKey(
        "library.Article",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Artículo",
    )

    is_read = models.BooleanField(default=False, verbose_name="¿Leída?")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    # este campo es para cuando la notificación es de un comentario
    comment = models.ForeignKey(
        "posts.Comment", on_delete=models.CASCADE, null=True, blank=True
    )
    message = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Mensaje de sistema/logro"
    )

    class Meta:
        ordering = ["-created_at"]
        # Esto cambia el nombre de la sección en el Admin
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"

    def __str__(self):
        return f"{self.sender} -> {self.recipient} ({self.get_notification_type_display()})"

    @property
    def text(self):
        if self.message:
            return self.message
        if self.notification_type == "event_reminder":
            if self.event:
                return f"Recordatorio: tu quedada '{self.event.title}' comienza en menos de 24 horas."
            return "Recordatorio de quedada"
        if self.notification_type == "event":
            if self.event:
                if self.event.is_canceled:
                    return f"ha cancelado el evento: {self.event.title}"
                return f"se ha apuntado a tu quedada: {self.event.title}"
            return "actualización de evento"
        if self.notification_type == "chat_request":
            return "ha solicitado unirse a tu grupo de chat"
        if self.notification_type == "chat_accepted":
            return "ha aceptado tu solicitud de acceso al grupo de chat"
        if self.notification_type == "chat_rejected":
            return "ha rechazado tu solicitud de acceso al grupo de chat"
        if self.notification_type == "follow":
            return "ha empezado a seguirte"
        if self.notification_type == "like":
            return "le ha dado 'me gusta' a tu publicación"
        if self.notification_type == "comment":
            if self.event:
                return f"ha comentado en tu quedada: {self.event.title}"
            if self.post:
                return f"ha comentado en tu publicación: {self.post.title or 'Publicación'}"
            return "ha comentado en tu publicación/evento"
        if self.notification_type == "article_comment":
            if self.article:
                return f'ha comentado en tu artículo: "{self.article.title}"'
            return "ha comentado en tu artículo"
        if self.notification_type == "article_rating":
            if self.article:
                return f'ha valorado tu artículo: "{self.article.title}"'
            return "ha valorado tu artículo"
        if self.notification_type == "review":
            if self.event:
                return f"ha valorado tu evento: {self.event.title}"
            return "ha enviado una valoración sobre tu labor"
        return self.get_notification_type_display()
