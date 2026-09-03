from django.db import migrations


def assign_agora_to_existing_profiles(apps, schema_editor):
    UserProfile = apps.get_model("profiles", "UserProfile")
    Hobby = apps.get_model("profiles", "Hobby")
    UserHobby = apps.get_model("profiles", "UserHobby")

    agora = Hobby.objects.filter(slug="agora").first()
    if not agora:
        agora = Hobby.objects.create(
            name="Ágora",
            slug="agora",
            description="Canal oficial y publicaciones de la dirección y administración de la asociación.",
        )

    for profile in UserProfile.objects.all():
        UserHobby.objects.get_or_create(
            profile=profile,
            hobby=agora,
            defaults={"level": "beginner"},
        )


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0009_hobby_deleted_at_hobby_is_active"),
    ]

    operations = [
        migrations.RunPython(assign_agora_to_existing_profiles, reverse_func),
    ]
