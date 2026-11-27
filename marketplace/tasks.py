import logging
from celery import shared_task
from django.core.management import call_command

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def manage_marketplace_lifecycle_task(self):
    """
    Tarea periódica de Celery Beat para gestionar el ciclo de vida de los anuncios del mercadillo:
    - Envía avisos de caducidad a los 83 días (7 días antes).
    - Ejecuta hard delete (eliminación definitiva y limpieza física de multimedia) a los 90 días.
    """
    logger.info("[Celery Beat] Iniciando tarea de ciclo de vida del mercadillo...")
    try:
        call_command("manage_marketplace_lifecycle")
        logger.info("[Celery Beat] Ciclo de vida del mercadillo completado con éxito.")
        return "Marketplace lifecycle managed successfully"
    except Exception as exc:
        logger.error(
            f"[Celery Beat] Error durante la ejecución de manage_marketplace_lifecycle: {exc}",
            exc_info=True,
        )
        raise exc
