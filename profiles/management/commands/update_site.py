from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.sites.models import Site
from aficionados_network.utils.site import get_site_domain


class Command(BaseCommand):
    help = "Actualiza el dominio y nombre de django.contrib.sites (Site ID 1 por defecto) desde argumentos o variables de entorno"

    def add_arguments(self, parser):
        parser.add_argument(
            "--domain",
            type=str,
            default="",
            help="Nuevo dominio del sitio (ej. 141.148.227.48 o hubsclicks.com). Si se omite, usa SITE_DOMAIN o ALLOWED_HOSTS.",
        )
        parser.add_argument(
            "--name",
            type=str,
            default="",
            help="Nuevo nombre del sitio (ej. 'Hubs & Clicks'). Si se omite, usa SITE_NAME de settings.",
        )
        parser.add_argument(
            "--site-id",
            type=int,
            default=getattr(settings, "SITE_ID", 1),
            help="ID del sitio en django.contrib.sites a actualizar (por defecto SITE_ID de settings).",
        )

    def handle(self, *args, **options):
        site_id = options["site_id"]
        domain = options["domain"].strip() or getattr(settings, "SITE_DOMAIN", "").strip() or get_site_domain()
        name = options["name"].strip() or getattr(settings, "SITE_NAME", "Hubs & Clicks").strip()

        if not domain:
            self.stderr.write(self.style.ERROR("No se especificó un dominio y no se pudo determinar desde la configuración."))
            return

        site, created = Site.objects.get_or_create(
            id=site_id,
            defaults={"domain": domain, "name": name},
        )

        old_domain = site.domain
        old_name = site.name

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Sitio ID {site_id} creado con éxito: domain='{domain}', name='{name}'")
            )
        else:
            site.domain = domain
            site.name = name
            site.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Sitio ID {site_id} actualizado con éxito:\n"
                    f"  Anterior: domain='{old_domain}', name='{old_name}'\n"
                    f"  Actual:   domain='{domain}', name='{name}'"
                )
            )
