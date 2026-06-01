from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from notifications.models import Notification
from posts.models import Event
from profiles.models import Hobby, Review, UserHobby


@override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)
class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ana", email="ana@example.com", password="testpass123"
        )
        self.other = User.objects.create_user(
            username="luis", email="luis@example.com", password="testpass123"
        )
        self.hobby = Hobby.objects.create(name="Fotografia")

    def test_profile_list_excludes_current_user_and_supports_filters(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("profile_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.other.username)
        self.assertNotContains(response, self.user.username)
        self.assertEqual(response.context["count_all"], 1)
        self.assertEqual(response.context["count_following"], 0)
        self.assertEqual(response.context["count_not_following"], 1)

    def test_profile_detail_toggles_follow_and_creates_notification(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("profiles:profile", kwargs={"pk": self.other.profile.pk}),
            {"profile_pk": self.other.profile.pk},
        )

        self.assertRedirects(
            response, reverse("profiles:profile", kwargs={"pk": self.other.profile.pk})
        )
        self.assertTrue(self.user.profile.is_following(self.other.profile))
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.other, sender=self.user, notification_type="follow"
            ).exists()
        )

        self.client.post(
            reverse("profiles:profile", kwargs={"pk": self.other.profile.pk}),
            {"profile_pk": self.other.profile.pk},
        )
        self.assertFalse(self.user.profile.is_following(self.other.profile))

    def test_profile_edit_updates_user_profile_and_hobbies(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("profiles:profile_edit"),
            {
                "username": "ana-updated",
                "email": "ana-updated@example.com",
                "first_name": "Ana",
                "last_name": "Garcia",
                "bio": "Nueva bio",
                "birth_date": "1990-01-01",
                "location": "Telde",
                "website": "https://example.com",
            },
        )

        self.assertRedirects(
            response, reverse("profiles:profile", kwargs={"pk": self.user.profile.pk})
        )
        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.username, "ana-updated")
        self.assertEqual(self.user.profile.bio, "Nueva bio")
        self.assertEqual(self.user.profile.location, "Telde")

    def test_add_and_delete_hobby_for_current_profile(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("profiles:add_hobby"),
            {"hobby": self.hobby.pk, "level": "advanced"},
        )

        self.assertRedirects(response, reverse("profiles:profile_edit"))
        user_hobby = UserHobby.objects.get(profile=self.user.profile, hobby=self.hobby)
        self.assertEqual(user_hobby.level, "advanced")

        response = self.client.post(
            reverse("profiles:delete_hobby", kwargs={"hobby_id": user_hobby.pk})
        )

        self.assertRedirects(response, reverse("profiles:profile_edit"))
        self.assertFalse(UserHobby.objects.filter(pk=user_hobby.pk).exists())

    def test_add_review_creates_review_and_notification(self):
        event = Event.objects.create(
            title="Fotos al atardecer",
            description="Plan de prueba",
            location="Maspalomas",
            event_date=timezone.now() - timedelta(days=1),
            organizer=self.other,
            hobby=self.hobby,
        )
        event.participants.add(self.user)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("profiles:add_review", kwargs={"event_id": event.pk}),
            {"rating": 5, "comment": "Gran organizacion"},
        )

        self.assertRedirects(response, reverse("posts:my_participations"))
        review = Review.objects.get(event=event, author=self.user)
        self.assertEqual(review.recipient, self.other)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.other,
                sender=self.user,
                notification_type="review",
                review=review,
            ).exists()
        )
