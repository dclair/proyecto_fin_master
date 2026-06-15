from django.db.models.signals import m2m_changed, post_save, post_delete
from django.dispatch import receiver
from posts.models import Posts, EventAttendance
from .services import check_badges

@receiver(m2m_changed, sender=Posts.likes.through)
def check_likes_badges(sender, instance, action, **kwargs):
    # instance es el post que recibió likes
    # Verificamos si se agregó o quitó un like
    if action in ['post_add', 'post_remove']:
        check_badges(instance.user)

@receiver(post_save, sender=EventAttendance)
@receiver(post_delete, sender=EventAttendance)
def check_event_badges(sender, instance, **kwargs):
    # instance es el EventAttendance
    # Validamos al organizador del evento
    check_badges(instance.event.organizer)

@receiver(post_save, sender='profiles.Review')
def check_review_badges(sender, instance, **kwargs):
    # Evaluamos al organizador que recibe la valoración
    check_badges(instance.recipient)
