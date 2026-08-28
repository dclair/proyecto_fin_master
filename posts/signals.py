from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Event, EventAttendance
from chat.models import Conversation, ConversationParticipant

@receiver(post_save, sender=Event)
def create_event_chat_group(sender, instance, created, **kwargs):
    """
    Cuando se crea o actualiza un evento, si es online y no tiene grupo de chat,
    se le crea uno automáticamente.
    """
    if instance.is_online and not instance.chat_group:
        # Título del grupo: "Título del evento - Nombre del creador"
        group_name = f"{instance.title} - {instance.organizer.username}"
        
        # Crear la conversación grupal
        conversation = Conversation.objects.create(
            is_group=True,
            name=group_name,
            admin=instance.organizer
        )
        
        # Vincular el grupo al evento
        instance.chat_group = conversation
        instance.save(update_fields=['chat_group'])
        
        # Añadir al creador del evento como participante del chat
        ConversationParticipant.objects.get_or_create(
            conversation=conversation,
            user=instance.organizer
        )

@receiver(post_save, sender=EventAttendance)
def add_user_to_event_chat(sender, instance, created, **kwargs):
    """
    Cuando un usuario se apunta a un evento de forma online,
    lo añadimos al grupo de chat del evento (si existe).
    """
    # Solo añadimos si la asistencia es online y el evento tiene chat_group
    if instance.attendance_type == 'online' and instance.event.chat_group:
        ConversationParticipant.objects.get_or_create(
            conversation=instance.event.chat_group,
            user=instance.user
        )

@receiver(post_delete, sender=EventAttendance)
def remove_user_from_event_chat(sender, instance, **kwargs):
    """
    Si el usuario cancela su asistencia, lo sacamos del grupo de chat.
    """
    if instance.event.chat_group:
        # No eliminamos al organizador aunque por algún bug se borrara su asistencia
        if instance.user != instance.event.organizer:
            ConversationParticipant.objects.filter(
                conversation=instance.event.chat_group,
                user=instance.user
            ).delete()
