import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import timezone

from aficionados_network.utils.mailer import send_hubs_email_async
from marketplace.models import Listing

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        'Gestiona el ciclo de vida del mercadillo: envía aviso de expiración a los 83 días '
        'y elimina definitivamente (hard delete) los anuncios con más de 90 días.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecuta la simulación sin modificar la base de datos ni enviar correos.',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        now = timezone.now()

        prefix = "[DRY-RUN] " if dry_run else ""
        self.stdout.write(f"{prefix}Iniciando gestión del ciclo de vida del mercadillo...")

        # 1. Ventana de advertencia idempotente (83 a 90 días)
        # Anuncios creados hace entre 83 y 90 días que NO hayan recibido aviso aún.
        warning_cutoff_start = now - timedelta(days=90)
        warning_cutoff_end = now - timedelta(days=83)

        to_warn = Listing.objects.filter(
            created_at__lte=warning_cutoff_end,
            created_at__gt=warning_cutoff_start,
            expiration_warning_sent=False,
        ).select_related('seller')

        warn_count = 0
        for listing in to_warn:
            self.stdout.write(
                f"{prefix}Avisando al vendedor {listing.seller.username} para el anuncio '{listing.title}' (ID: {listing.pk})."
            )
            if not dry_run:
                self.send_warning_email(listing)
                listing.expiration_warning_sent = True
                listing.save(update_fields=['expiration_warning_sent'])
                logger.info(
                    f"Aviso de caducidad enviado para anuncio ID {listing.pk} ('{listing.title}') a {listing.seller.email}"
                )
            warn_count += 1

        # 2. Eliminación definitiva (hard delete) a los 90 días
        # Anuncios con antigüedad mayor o igual a 90 días
        delete_cutoff = now - timedelta(days=90)
        to_delete = Listing.objects.filter(created_at__lte=delete_cutoff)

        delete_count = 0
        for listing in to_delete:
            listing_id = listing.pk
            listing_title = listing.title
            self.stdout.write(
                f"{prefix}Eliminando anuncio ID {listing_id} ('{listing_title}')."
            )
            if not dry_run:
                listing.delete()
                logger.info(
                    f"Anuncio ID {listing_id} ('{listing_title}') eliminado definitivamente por ciclo de vida."
                )
            delete_count += 1

        summary_msg = (
            f"{prefix}Ciclo de vida completado. "
            f"Avisos procesados: {warn_count}, Anuncios eliminados: {delete_count}."
        )
        self.stdout.write(self.style.SUCCESS(summary_msg))
        logger.info(summary_msg)

    def send_warning_email(self, listing):
        subject = f'Aviso: Tu anuncio "{listing.title}" expirará en 7 días'
        message = (
            f"Hola {listing.seller.username},\n\n"
            f"Te informamos de que tu anuncio '{listing.title}' en el Mercadillo está próximo a caducar. "
            f"Por razones de mantenimiento y actualización de la plataforma, los anuncios tienen una vigencia de 90 días.\n\n"
            f"Tu anuncio será eliminado definitivamente dentro de 7 días. "
            f"Si deseas conservarlo o renovarlo, te recomendamos guardar la información y volverlo a publicar una vez finalizado.\n\n"
            f"Saludos cordiales,\nEl equipo de Aficionados Network"
        )
        try:
            action_url = reverse('marketplace:listing_list')
        except Exception:
            action_url = '/marketplace/'

        try:
            send_hubs_email_async(
                subject=subject,
                recipient=listing.seller,
                message_body=message,
                action_url=action_url,
            )
        except Exception as e:
            logger.error(
                f"Error al enviar correo de aviso para anuncio {listing.pk} ({listing.seller.email}): {e}",
                exc_info=True,
            )
            self.stdout.write(self.style.ERROR(f"Error enviando correo a {listing.seller.email}: {e}"))
