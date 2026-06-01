from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.utils import timezone

from posts.models import Event
from profiles.models import Follow, Hobby, Review, UserHobby, UserProfile


@override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)
class ProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ana", email="ana@example.com", password="testpass123"
        )
        self.other = User.objects.create_user(
            username="luis", email="luis@example.com", password="testpass123"
        )

    def test_user_profile_is_created_by_signal_for_regular_user(self):
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
        self.assertEqual(str(self.user.profile), "ana")

    def test_superuser_does_not_get_profile_from_signal(self):
        admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="testpass123"
        )

        self.assertFalse(UserProfile.objects.filter(user=admin).exists())

    def test_profile_age_and_birth_date_validation(self):
        profile = self.user.profile
        profile.birth_date = date.today().replace(year=date.today().year - 20)
        profile.full_clean()
        self.assertEqual(profile.age, 20)

        profile.birth_date = date.today() + timedelta(days=1)
        with self.assertRaises(ValidationError):
            profile.full_clean()

    def test_hobby_generates_unique_slug(self):
        hobby = Hobby.objects.create(name="Fotografia Nocturna")

        self.assertEqual(hobby.slug, "fotografia-nocturna")
        self.assertEqual(str(hobby), "Fotografia Nocturna")

    def test_user_hobby_is_unique_per_profile_and_hobby(self):
        hobby = Hobby.objects.create(name="Senderismo")
        UserHobby.objects.create(profile=self.user.profile, hobby=hobby, level="beginner")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                UserHobby.objects.create(
                    profile=self.user.profile, hobby=hobby, level="advanced"
                )

    def test_follow_relationship_counts_toggle_and_notifications(self):
        followed = self.user.profile.toggle_follow(self.other.profile)

        self.assertTrue(followed)
        self.assertTrue(self.user.profile.is_following(self.other.profile))
        self.assertTrue(self.other.profile.is_followed_by(self.user.profile))
        self.assertEqual(self.user.profile.following_count(), 1)
        self.assertEqual(self.other.profile.followers_count(), 1)
        self.assertEqual(
            str(Follow.objects.get()),
            "ana follows luis",
        )

        unfollowed = self.user.profile.toggle_follow(self.other.profile)

        self.assertFalse(unfollowed)
        self.assertFalse(self.user.profile.is_following(self.other.profile))

    def test_follow_cannot_target_same_profile(self):
        with self.assertRaises(ValidationError):
            Follow.objects.create(follower=self.user.profile, following=self.user.profile)

    def test_review_is_unique_per_event_and_author(self):
        hobby = Hobby.objects.create(name="Ciclismo")
        event = Event.objects.create(
            title="Ruta corta",
            description="Plan de prueba",
            location="Las Palmas",
            event_date=timezone.now() + timedelta(days=2),
            organizer=self.other,
            hobby=hobby,
        )
        Review.objects.create(
            event=event,
            author=self.user,
            recipient=self.other,
            rating=5,
            comment="Muy buena quedada",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Review.objects.create(
                    event=event,
                    author=self.user,
                    recipient=self.other,
                    rating=4,
                )
