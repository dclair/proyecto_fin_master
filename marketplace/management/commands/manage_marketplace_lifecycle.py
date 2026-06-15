from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from marketplace.models import Listing
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Limpia anuncios expirados (90 días) y avisa a los usuarios a los 83 días (faltan 7 días).'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        
        # 1. Avisar a usuarios a los 83 días
        # Para evitar spamear, filtramos exactamente los anuncios creados entre 83 y 84 días atrás.
        start_83 = now - timedelta(days=84)
        end_83 = now - timedelta(days=83)
        
        to_warn = Listing.objects.filter(created_at__gte=start_83, created_at__lt=end_83)
        warn_count = 0
        for listing in to_warn:
            self.send_warning_email(listing)
            warn_count += 1
            
        # 2. Eliminar anuncios de más de 90 días
        limit_90 = now - timedelta(days=90)
        to_delete = Listing.objects.filter(created_at__lt=limit_90)
        delete_count = 0
        for listing in to_delete:
            listing.delete()  # Esto ejecutará el os.remove() de models.py
            delete_count += 1
            
        self.stdout.write(self.style.SUCCESS(f'Avisos enviados: {warn_count}'))
        self.stdout.write(self.style.SUCCESS(f'Anuncios eliminados: {delete_count}'))

    def send_warning_email(self, listing):
        subject = f'Aviso: Tu anuncio "{listing.title}" expirará en 7 días'
        message = (
            f"Hola {listing.seller.username},\n\n"
            f"Te avisamos que tu anuncio '{listing.title}' en el Mercadillo está a punto de caducar. "
            f"Por nuestras políticas de mantenimiento y calidad, los anuncios se eliminan automáticamente a los 3 meses.\n\n"
            f"Tu anuncio será eliminado de la plataforma en exactamente 7 días. "
            f"Si deseas seguir ofreciéndolo, te invitamos a que guardes la información y lo vuelvas a publicar "
            f"una vez caduque. Podrás mantenerlo por otros 3 meses sin problema.\n\n"
            f"Saludos,\nEl equipo de Aficionados Network"
        )
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [listing.seller.email],
                fail_silently=True,
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error enviando correo a {listing.seller.email}: {e}"))
