from django.db.models.signals import m2m_changed, post_save, post_delete
from django.dispatch import receiver
from posts.models import Posts, EventAttendance
from .services import check_likes_badge, check_event_badges, check_review_badges

@receiver(m2m_changed, sender=Posts.likes.through)
def check_likes_badges(sender, instance, action, **kwargs):
    # instance es el post que recibió likes
    # Verificamos solo si se agregó un like y evaluamos únicamente las medallas de likes
    if action == 'post_add':
        check_likes_badge(instance.user)

@receiver(post_save, sender=EventAttendance)
@receiver(post_delete, sender=EventAttendance)
def check_event_badges_signal(sender, instance, **kwargs):
    if kwargs.get('raw', False):
        return
    # Evaluamos únicamente las medallas de eventos al organizador
    check_event_badges(instance.event.organizer)

@receiver(post_save, sender='profiles.Review')
def check_review_badges_signal(sender, instance, **kwargs):
    if kwargs.get('raw', False):
        return
    # Evaluamos únicamente las medallas de reseñas al organizador
    check_review_badges(instance.recipient)
