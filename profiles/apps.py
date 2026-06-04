from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "profiles"

    def ready(self):
        # Importa las señales para que se registren
        import profiles.signals

        # Hacer que el email sea único a nivel de validación de Django
        from django.contrib.auth.models import User
        User._meta.get_field('email')._unique = True
        User._meta.get_field('email').blank = False
        User._meta.get_field('email').null = False
