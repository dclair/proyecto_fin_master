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
            from django.contrib.sites.models import Site
            try:
                current_site = Site.objects.get_current()
                domain = current_site.domain
            except Exception:
                domain = "localhost:8000"

            mail_subject = "¡Bienvenido a Hubs & Clicks! Tu cuenta ha sido activada"
            html_content = render_to_string(
                "registration/welcome_email.html",
                {
                    "user": instance,
                    "domain": domain,
                },
            )

            email = EmailMultiAlternatives(mail_subject, "", settings.DEFAULT_FROM_EMAIL, to=[instance.email])
            email.attach_alternative(html_content, "text/html")

            img_path = os.path.join(settings.BASE_DIR, "static", "img", "logo_hubs.png")
            if os.path.exists(img_path):
                with open(img_path, "rb") as f:
                    logo = MIMEImage(f.read())
                    logo.add_header("Content-ID", "<logo_id>")
                    email.attach(logo)

            try:
                email.send()
                logger.info(f"Email de bienvenida enviado a {instance.email}")
            except Exception as e:
                logger.error(f"Error enviando email de bienvenida a {instance.email}: {str(e)}")
