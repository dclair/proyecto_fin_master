import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from notifications.models import Notification

logger = logging.getLogger(__name__)

CHUNK_SIZE = 500


@shared_task(
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def clean_old_read_notifications_task(self, days=90, chunk_size=CHUNK_SIZE):
    """
    Tarea periódica de mantenimiento conservador para eliminar notificaciones antiguas leídas.
    Criterios:
      - is_read=True
      - created_at < now - 90 días
      - Borrado por lotes (chunked delete de a 500 registros) para evitar saturar
        el buffer pool y el undo log de InnoDB en producción.
    """
    cutoff_date = timezone.now() - timedelta(days=days)
    logger.info(
        f"[Celery Beat] Iniciando limpieza de notificaciones leídas anteriores a {cutoff_date} (antigüedad > {days} días)..."
    )
    total_deleted = 0
    try:
        while True:
            # Obtener solo las IDs del lote para evitar cargar modelos enteros en memoria
            batch_ids = list(
                Notification.objects.filter(
                    is_read=True,
                    created_at__lt=cutoff_date,
                ).values_list("id", flat=True)[:chunk_size]
            )
            if not batch_ids:
                break

            deleted_count, _ = Notification.objects.filter(id__in=batch_ids).delete()
            total_deleted += deleted_count
            logger.info(
                f"[Celery Beat] Lote procesado: {len(batch_ids)} notificaciones eliminadas."
            )

        logger.info(
            f"[Celery Beat] Limpieza finalizada. Total de notificaciones leídas eliminadas: {total_deleted}"
        )
        return f"Cleaned {total_deleted} old read notifications"
    except Exception as exc:
        logger.error(
            f"[Celery Beat] Error durante la limpieza de notificaciones leídas: {exc}",
            exc_info=True,
        )
        raise exc
