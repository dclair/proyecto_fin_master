import logging
from django.db.models.signals import post_delete
from django.dispatch import receiver
from marketplace.models import Listing

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Listing)
def delete_listing_media_files(sender, instance, **kwargs):
    """
    Elimina físicamente del sistema de almacenamiento los archivos multimedia
    asociados al anuncio (imagen y video) cuando el registro se elimina (hard delete).
    """
    if instance.image:
        try:
            instance.image.delete(save=False)
        except Exception as e:
            logger.error(
                f"Error al eliminar la imagen del anuncio ID {getattr(instance, 'id', None)}: {e}",
                exc_info=True,
            )

    if instance.video:
        try:
            instance.video.delete(save=False)
        except Exception as e:
            logger.error(
                f"Error al eliminar el video del anuncio ID {getattr(instance, 'id', None)}: {e}",
                exc_info=True,
            )
