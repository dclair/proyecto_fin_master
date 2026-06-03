from datetime import timedelta
from io import BytesIO
import os
import shutil
import tempfile

from django.contrib.auth.models import User
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from notifications.models import Notification
from posts.models import Comment, Event, EventComment, Posts, validate_image_size
from profiles.models import Hobby, UserHobby


TEMP_MEDIA_ROOT = tempfile.mkdtemp()


def tearDownModule():
    shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)


def test_image(name="test.png", size=(10, 10), color=(255, 0, 0)):
    image_file = BytesIO()
    image = Image.new("RGB", size, color)
    image.save(image_file, "PNG")
    image_file.seek(0)
    return SimpleUploadedFile(name, image_file.read(), content_type="image/png")


@override_settings(
    DEBUG=True,
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@example.com",
    MEDIA_ROOT=TEMP_MEDIA_ROOT,
)
class PostModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ana", email="ana@example.com", password="testpass123"
        )
        self.hobby = Hobby.objects.create(name="Fotografia")

    def test_post_like_comment_counts_absolute_url_and_delete_image(self):
        post = Posts.objects.create(
            user=self.user,
            title="Mi click",
            caption="Una descripcion",
            category=self.hobby,
            image=test_image(),
        )
        post.likes.add(self.user)
        Comment.objects.create(user=self.user, post=post, comment="Muy buena foto")

        image_path = post.image.path
        self.assertEqual(post.total_likes, 1)
        self.assertEqual(post.total_comments, 1)
        self.assertTrue(post.user_has_liked(self.user))
        self.assertEqual(
            post.get_absolute_url(), reverse("posts:post_detail", kwargs={"pk": post.pk})
        )

        post.delete()
        self.assertFalse(Posts.objects.filter(pk=post.pk).exists())
        self.assertFalse(os.path.exists(image_path))

    def test_image_size_validator_rejects_files_over_five_mb(self):
        image = SimpleUploadedFile("big.png", b"x" * (5 * 1024 * 1024 + 1))

        with self.assertRaises(ValidationError):
            validate_image_size(image)

    def test_comment_validation_rejects_parent_from_other_post(self):
        other_post = Posts.objects.create(user=self.user, category=self.hobby)
        post = Posts.objects.create(user=self.user, category=self.hobby)
        parent = Comment.objects.create(user=self.user, post=other_post, comment="Padre")
        reply = Comment(user=self.user, post=post, parent=parent, comment="Respuesta")

        with self.assertRaises(ValidationError):
            reply.clean()


@override_settings(
    DEBUG=True,
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@example.com",
    MEDIA_ROOT=TEMP_MEDIA_ROOT,
)
class EventModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ana", email="ana@example.com", password="testpass123"
        )
        self.hobby = Hobby.objects.create(name="Senderismo")

    def test_event_helpers_and_event_comment(self):
        event = Event.objects.create(
            title="Ruta norte",
            description="Plan",
            location="Teror",
            event_date=timezone.now() - timedelta(days=1),
            organizer=self.user,
            hobby=self.hobby,
        )
        comment = EventComment.objects.create(
            event=event, user=self.user, content="Nos vemos alli"
        )

        self.assertTrue(event.is_past)
        self.assertEqual(
            event.get_absolute_url(),
            reverse("posts:event_detail", kwargs={"pk": event.pk}),
        )
        self.assertEqual(str(event), "Ruta norte - Senderismo")
        self.assertEqual(str(comment), "Comentario de ana en Ruta norte")


@override_settings(
    DEBUG=True,
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@example.com",
    MEDIA_ROOT=TEMP_MEDIA_ROOT,
)
class PostRouteTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="ana", email="ana@example.com", password="testpass123"
        )
        self.other = User.objects.create_user(
            username="luis", email="luis@example.com", password="testpass123"
        )
        self.hobby = Hobby.objects.create(name="Fotografia")
        self.post = Posts.objects.create(
            user=self.author,
            title="Click",
            caption="Un click",
            category=self.hobby,
        )

    def test_toggle_like_adds_and_removes_notification(self):
        self.client.force_login(self.other)

        response = self.client.post(
            reverse("posts:toggle_like", kwargs={"post_id": self.post.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"liked": True, "count": 1})
        self.assertTrue(
            Notification.objects.filter(
                sender=self.other,
                recipient=self.author,
                post=self.post,
                notification_type="like",
            ).exists()
        )

        response = self.client.post(
            reverse("posts:toggle_like", kwargs={"post_id": self.post.pk})
        )

        self.assertJSONEqual(response.content, {"liked": False, "count": 0})
        self.assertFalse(Notification.objects.filter(notification_type="like").exists())

    def test_add_post_comment_creates_notification_and_email(self):
        self.client.force_login(self.other)

        response = self.client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.pk}),
            {"comment": "Me apunto a probarlo"},
        )

        self.assertRedirects(
            response, reverse("posts:post_detail", kwargs={"pk": self.post.pk})
        )
        self.assertTrue(Comment.objects.filter(post=self.post, user=self.other).exists())
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.author,
                sender=self.other,
                post=self.post,
                notification_type="comment",
            ).exists()
        )
        self.assertEqual(len(mail.outbox), 1)

    def test_post_detail_modal_returns_partial(self):
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("posts:post_detail", kwargs={"pk": self.post.pk}), {"modal": "1"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "posts/partials/_post_modal_body.html")


@override_settings(
    DEBUG=True,
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@example.com",
    MEDIA_ROOT=TEMP_MEDIA_ROOT,
)
class EventRouteTests(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(
            username="ana", email="ana@example.com", password="testpass123"
        )
        self.participant = User.objects.create_user(
            username="luis", email="luis@example.com", password="testpass123"
        )
        self.hobby = Hobby.objects.create(name="Ciclismo")
        UserHobby.objects.create(
            profile=self.participant.profile, hobby=self.hobby, level="beginner"
        )
        self.event = Event.objects.create(
            title="Ruta sencilla",
            description="Plan",
            location="Arucas",
            event_date=timezone.now() + timedelta(days=2),
            organizer=self.organizer,
            hobby=self.hobby,
            max_participants=2,
            level="beginner",
        )
        self.event.participants.add(self.organizer)

    def test_event_list_detail_and_level_match_context(self):
        self.client.force_login(self.participant)

        response = self.client.get(reverse("posts:event_list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["events"][0].pk, self.event.pk)
        self.assertTrue(response.context["events"][0].is_match)

        response = self.client.get(
            reverse("posts:event_detail", kwargs={"pk": self.event.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_match"])
        self.assertFalse(response.context["is_mentor"])

    def test_event_create_adds_organizer_as_participant(self):
        self.client.force_login(self.organizer)

        response = self.client.post(
            reverse("posts:event_create"),
            {
                "title": "Nueva ruta",
                "description": "Plan nuevo",
                "hobby": self.hobby.pk,
                "location": "Galdar",
                "event_date": (timezone.now() + timedelta(days=3)).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
                "max_participants": 5,
                "level": "all",
            },
        )

        self.assertRedirects(response, reverse("posts:event_list"))
        created = Event.objects.get(title="Nueva ruta")
        self.assertEqual(created.organizer, self.organizer)
        self.assertIn(self.organizer, created.participants.all())

    def test_toggle_attendance_adds_and_removes_participant_and_sends_email(self):
        self.client.force_login(self.participant)

        response = self.client.post(
            reverse("posts:toggle_attendance", kwargs={"event_id": self.event.pk})
        )

        self.assertRedirects(
            response, reverse("posts:event_detail", kwargs={"pk": self.event.pk})
        )
        self.event.refresh_from_db()
        self.assertIn(self.participant, self.event.participants.all())
        self.assertEqual(len(mail.outbox), 1)

        response = self.client.post(
            reverse("posts:toggle_attendance", kwargs={"event_id": self.event.pk})
        )

        self.assertRedirects(
            response, reverse("posts:event_detail", kwargs={"pk": self.event.pk})
        )
        self.assertNotIn(self.participant, self.event.participants.all())
        self.assertEqual(len(mail.outbox), 2)

    def test_organizer_cancels_reactivates_duplicates_and_comments_on_event(self):
        self.event.participants.add(self.participant)
        self.client.force_login(self.organizer)

        cancel_response = self.client.post(
            reverse("posts:event_cancel", kwargs={"pk": self.event.pk})
        )

        self.assertRedirects(
            cancel_response, reverse("posts:event_detail", kwargs={"pk": self.event.pk})
        )
        self.event.refresh_from_db()
        self.assertTrue(self.event.is_canceled)
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.participant,
                sender=self.organizer,
                event=self.event,
                notification_type="event",
            ).exists()
        )
        self.assertEqual(len(mail.outbox), 1)

        reactivate_response = self.client.post(
            reverse("posts:event_reactivate", kwargs={"pk": self.event.pk})
        )

        self.assertRedirects(
            reactivate_response,
            reverse("posts:event_detail", kwargs={"pk": self.event.pk}),
        )
        self.event.refresh_from_db()
        self.assertFalse(self.event.is_canceled)

        comment_response = self.client.post(
            reverse("posts:add_event_comment", kwargs={"event_id": self.event.pk}),
            {"content": "Cambio de hora confirmado"},
        )

        self.assertRedirects(
            comment_response, reverse("posts:event_detail", kwargs={"pk": self.event.pk})
        )
        self.assertTrue(
            EventComment.objects.filter(event=self.event, user=self.organizer).exists()
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.participant,
                sender=self.organizer,
                notification_type="comment",
                event=self.event,
            ).exists()
        )

        duplicate_response = self.client.post(
            reverse("posts:event_duplicate", kwargs={"pk": self.event.pk})
        )

        duplicated = Event.objects.get(title=f"COPIA: {self.event.title}")
        self.assertRedirects(
            duplicate_response,
            reverse("posts:event_update", kwargs={"pk": duplicated.pk}),
        )

    def test_hobby_hub_clicks_gallery_and_membership_toggle(self):
        self.client.force_login(self.participant)
        Posts.objects.create(user=self.participant, category=self.hobby, image=test_image())
        self.event.image = test_image(name="event.png")
        self.event.save()

        hub_response = self.client.get(
            reverse("posts:hobby_hub", kwargs={"hobby_slug": self.hobby.slug})
        )
        self.assertEqual(hub_response.status_code, 200)
        self.assertEqual(hub_response.context["hobby"], self.hobby)

        toggle_response = self.client.post(
            reverse("posts:toggle_hobby_membership", kwargs={"hobby_slug": self.hobby.slug})
        )
        self.assertRedirects(
            toggle_response,
            reverse("posts:hobby_hub", kwargs={"hobby_slug": self.hobby.slug}),
        )

        gallery_response = self.client.get(reverse("posts:clicks_list"))
        self.assertEqual(gallery_response.status_code, 200)
        self.assertIn("clicks", gallery_response.context)
