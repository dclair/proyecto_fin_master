from django.apps import AppConfig
from django.db.models.signals import post_migrate


def sync_default_site(sender, **kwargs):
    """
    Sincroniza django.contrib.sites (Site ID 1) con SITE_DOMAIN / SITE_NAME
    configurados en el entorno. Se ejecuta con la señal post_migrate para
    que en producción (VPS) la base de datos se actualice automáticamente
    tras 'python manage.py migrate' sin requerir SQL manual.
    """
    try:
        from django.conf import settings
        from django.contrib.sites.models import Site
        from aficionados_network.utils.site import get_site_domain

        target_domain = getattr(settings, "SITE_DOMAIN", "").strip() or get_site_domain()
        if not target_domain or target_domain in ("localhost:8000", "testserver"):
            # Si no hay configuración explícita en settings y es local, solo actualizar si es el placeholder default
            if not getattr(settings, "SITE_DOMAIN", ""):
                return

        site_name = getattr(settings, "SITE_NAME", "Hubs & Clicks").strip()
        site_id = getattr(settings, "SITE_ID", 1)

        site, created = Site.objects.get_or_create(
            id=site_id,
            defaults={"domain": target_domain, "name": site_name},
        )
        if not created and (site.domain == "example.com" or (getattr(settings, "SITE_DOMAIN", "") and site.domain != target_domain)):
            site.domain = target_domain
            site.name = site_name
            site.save(update_fields=["domain", "name"])
    except Exception:
        # Previene que cualquier fallo en migraciones tempranas bloquee el arranque
        pass


class ProfilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "profiles"

    def ready(self):
        # Importa las señales para que se registren
        import profiles.signals

        # Conectar sincronización automática del Site por defecto en post_migrate
        post_migrate.connect(sync_default_site, sender=self)

        # Hacer que el email sea único a nivel de validación de Django
        from django.contrib.auth.models import User
        User._meta.get_field('email')._unique = True
        User._meta.get_field('email').blank = False
        User._meta.get_field('email').null = False
