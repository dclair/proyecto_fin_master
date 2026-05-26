from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from profiles.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = "Create UserProfile for regular users without one (excludes superusers and staff)"

    def handle(self, *args, **options):
        # Solo usuarios regulares (no superusuarios ni staff) sin perfil
        regular_users = User.objects.filter(
            profile__isnull=True, is_superuser=False, is_staff=False
        )

        count = 0
        for user in regular_users:
            UserProfile.objects.create(user=user)
            count += 1
            self.stdout.write(f"Created profile for user: {user.username}")

        if count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created {count} user profiles")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("All regular users already have profiles")
            )

        # Mostrar estadísticas
        total_regular = User.objects.filter(is_superuser=False, is_staff=False).count()
        total_with_profiles = User.objects.filter(
            is_superuser=False, is_staff=False, profile__isnull=False
        ).count()

        self.stdout.write("\nUser profile statistics:")
        self.stdout.write(f"Total regular users: {total_regular}")
        self.stdout.write(f"Regular users with profiles: {total_with_profiles}")
        self.stdout.write(
            f"Admin users (no profiles): {User.objects.filter(is_superuser=True).count()}"
        )
        self.stdout.write(
            f"Staff users (no profiles): {User.objects.filter(is_staff=True).exclude(is_superuser=True).count()}"
        )
