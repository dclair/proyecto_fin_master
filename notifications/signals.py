from django.db.models.signals import post_save
from django.dispatch import receiver

# Importa tu modelo de Seguidores (ajusta la ruta según tu app)
from profiles.models import Follow
from .services import NotificationDispatcher


@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    # 'created' es True solo cuando se crea el registro por primera vez
    if kwargs.get("raw"):
        return
    if created:
        NotificationDispatcher.dispatch(
            notification_type="follow",
            recipient=instance.following.user,  # El que recibe el seguidor
            sender=instance.follower.user,  # El que dio clic en seguir
        )
