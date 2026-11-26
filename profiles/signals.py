from django.db import transaction
from django.db.models.signals import pre_save, post_save, m2m_changed
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from email.mime.image import MIMEImage
import os
from .models import UserProfile, Hobby, UserHobby
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create a user profile when a new user is created.
    """
    if created and not instance.is_superuser:
        try:
            with transaction.atomic():
                UserProfile.objects.get_or_create(user=instance)
        except Exception as e:
            logger.error(
                f"Error creating profile for user {instance.username}: {str(e)}"
            )


@receiver(post_save, sender=UserProfile)
def assign_default_agora_hobby(sender, instance, created, **kwargs):
    """
    Signal to ensure every UserProfile is automatically subscribed to
    the official association channel ('Ágora').
    """
    if created:
        try:
            agora, _ = Hobby.objects.get_or_create(
                slug="agora",
                defaults={
                    "name": "Ágora",
                    "description": "Canal oficial y publicaciones de la dirección y administración de la asociación.",
                },
            )
            UserHobby.objects.get_or_create(
                profile=instance,
                hobby=agora,
                defaults={"level": "beginner"},
            )
        except Exception as e:
            logger.error(
                f"Error assigning default Agora hobby to profile {instance.id}: {str(e)}"
            )


@receiver(m2m_changed, sender=UserProfile.following.through)
def prevent_self_follow(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Prevent users from following themselves.
    """
    if action == "pre_add" and instance.pk in pk_set:
        from django.core.exceptions import ValidationError

        raise ValidationError("No puedes seguirte a ti mismo.")


@receiver(pre_save, sender=User)
def capture_old_active_state(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            instance._old_is_active = old_instance.is_active
        except User.DoesNotExist:
            instance._old_is_active = False
    else:
        instance._old_is_active = False

@receiver(post_save, sender=User)
def send_welcome_email_on_activation(sender, instance, created, **kwargs):
    if not created and hasattr(instance, '_old_is_active'):
        if not instance._old_is_active and instance.is_active:
            # ¡El usuario fue activado por un admin!
            from aficionados_network.utils.mailer import send_hubs_email_async
            from aficionados_network.utils.site import build_absolute_url
            from django.urls import reverse

            mail_subject = "¡Bienvenido a Hubs & Clicks! Tu cuenta ha sido activada"
            message_body = (
                f"¡Hola {instance.username}!\n\n"
                f"Tu cuenta ha sido revisada y activada con éxito por el equipo de administración.\n\n"
                f"Ya puedes iniciar sesión en la plataforma para descubrir y conectar con la comunidad, "
                f"participar en quedadas, compartir tus clicks y disfrutar de todos los recursos."
            )
            try:
                login_path = reverse("login")
            except Exception:
                login_path = "/login/"
            action_url = build_absolute_url(login_path)

            try:
                send_hubs_email_async(
                    subject=mail_subject,
                    recipient=instance,
                    message_body=message_body,
                    action_url=action_url,
                )
                logger.info(f"Email de bienvenida encolado en Celery para {instance.email}")
            except Exception as e:
                logger.error(f"Error encolando email de bienvenida para {instance.email}: {str(e)}")
