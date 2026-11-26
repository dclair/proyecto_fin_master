from django.db import migrations


def update_site_domain(apps, schema_editor):
    from django.conf import settings

    Site = apps.get_model("sites", "Site")
    site_id = getattr(settings, "SITE_ID", 1)

    site_domain = getattr(settings, "SITE_DOMAIN", "").strip()
    if not site_domain:
        for host in getattr(settings, "ALLOWED_HOSTS", []):
            host = host.strip()
            if host and host not in ("*", "localhost", "127.0.0.1", "testserver"):
                site_domain = host
                break
    if not site_domain:
        site_domain = "localhost:8000"

    site_name = getattr(settings, "SITE_NAME", "Hubs & Clicks").strip()

    site, created = Site.objects.get_or_create(
        id=site_id,
        defaults={"domain": site_domain, "name": site_name},
    )
    if not created and (site.domain == "example.com" or getattr(settings, "SITE_DOMAIN", "")):
        site.domain = site_domain
        site.name = site_name
        site.save(update_fields=["domain", "name"])


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0011_alter_hobby_options"),
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [
        migrations.RunPython(update_site_domain, reverse_func),
    ]
