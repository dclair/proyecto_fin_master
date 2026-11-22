import logging
from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from notifications.models import Notification
from notifications.services import NotificationDispatcher
from .models import Event, EventAttendance

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
)
def send_event_reminders_task(self):
    """
    Tarea periódica de Celery Beat para enviar recordatorios por correo y notificación in-app
    a los asistentes confirmados de eventos que comienzan dentro de las próximas 24 horas.

    Garantías de diseño e idempotencia:
    1. Ventana de tiempo estricta: eventos activos y no cancelados con event_date entre now() y now() + 24 horas.
    2. Idempotencia a nivel de modelo: EventAttendance.reminder_sent = True evita reenvíos.
    3. Idempotencia defensiva: Se comprueba la existencia previa de Notification(event_reminder).
    4. Aislamiento transaccional: cada asistente se procesa de forma atómica para no bloquear el lote.
    """
    now = timezone.now()
    window_end = now + timedelta(hours=24)
    logger.info(
        f"[Celery Beat] Iniciando escaneo de quedadas entre {now} y {window_end}..."
    )

    qualifying_events = Event.objects.filter(
        is_canceled=False,
        is_active=True,
        deleted_at__isnull=True,
        event_date__gt=now,
        event_date__lte=window_end,
    ).select_related("organizer", "hobby")

    total_reminders_sent = 0

    for event in qualifying_events:
        # Recuperar asistencias no notificadas de usuarios activos con correo
        attendances = (
            event.attendances.filter(reminder_sent=False, user__is_active=True)
            .exclude(user__email="")
            .select_related("user")
        )

        for attendance in attendances:
            user = attendance.user

            with transaction.atomic():
                # Doble verificación defensiva contra la base de datos
                already_notified = Notification.objects.filter(
                    recipient=user,
                    event=event,
                    notification_type="event_reminder",
                ).exists()

                if already_notified:
                    logger.info(
                        f"[Celery Beat] Notificación previa detectada para {user.username} en quedada {event.id}. Marcando reminder_sent=True."
                    )
                    attendance.reminder_sent = True
                    attendance.reminder_sent_at = timezone.now()
                    attendance.save(update_fields=["reminder_sent", "reminder_sent_at"])
                    continue

                # Preparar datos de despacho
                action_url = reverse("posts:event_detail", args=[event.id])
                formatted_date = event.event_date.strftime("%d/%m/%Y a las %H:%M")
                location_str = (
                    "Encuentro Online (ver enlace en la quedada)"
                    if event.is_online
                    else (event.location or "Ubicación por confirmar")
                )

                email_subject = f"⏰ Recordatorio: '{event.title}' comienza en menos de 24 horas"
                email_body = (
                    f"¡Hola {user.username}! Te recordamos que la quedada '{event.title}' "
                    f"se llevará a cabo el {formatted_date}. Lugar: {location_str}."
                )

                # Despacho centralizado in-app y correo
                NotificationDispatcher.dispatch(
                    notification_type="event_reminder",
                    sender=event.organizer,
                    recipient=user,
                    event=event,
                    message=f"Recordatorio: la quedada '{event.title}' comienza en menos de 24 horas.",
                    send_email=True,
                    email_subject=email_subject,
                    email_body=email_body,
                    action_url=action_url,
                    template_name="emails/event_reminder.html",
                    extra_context={
                        "event_title": event.title,
                        "event_date": formatted_date,
                        "event_location": location_str,
                        "is_online": event.is_online,
                        "stream_url": event.stream_url or "",
                        "organizer_username": event.organizer.username,
                    },
                )

                attendance.reminder_sent = True
                attendance.reminder_sent_at = timezone.now()
                attendance.save(update_fields=["reminder_sent", "reminder_sent_at"])
                total_reminders_sent += 1
                logger.info(
                    f"[Celery Beat] Recordatorio enviado a {user.username} para quedada {event.title} (ID: {event.id})"
                )

    logger.info(
        f"[Celery Beat] Finalizado escaneo de recordatorios. Total enviados: {total_reminders_sent}"
    )
    return total_reminders_sent
