from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from library.models import Article
from notifications.context_processors import unread_notifications
from notifications.models import Notification
from notifications.services import NotificationDispatcher
from posts.models import Event, Posts
from profiles.models import Follow, Hobby, Review


@override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)
class NotificationModelSignalTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username="ana", email="ana@example.com", password="testpass123"
        )
        self.recipient = User.objects.create_user(
            username="luis", email="luis@example.com", password="testpass123"
        )

    def test_notification_string_and_default_read_state(self):
        notification = Notification.objects.create(
            recipient=self.recipient,
            sender=self.sender,
            notification_type="follow",
        )

        self.assertFalse(notification.is_read)
        self.assertEqual(str(notification), "ana -> luis (Seguimiento)")

    def test_follow_signal_creates_notification(self):
        Follow.objects.create(
            follower=self.sender.profile, following=self.recipient.profile
        )

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.recipient,
                sender=self.sender,
                notification_type="follow",
            ).exists()
        )


@override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)
class NotificationRouteTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username="ana", email="ana@example.com", password="testpass123"
        )
        self.recipient = User.objects.create_user(
            username="luis", email="luis@example.com", password="testpass123"
        )
        self.hobby = Hobby.objects.create(name="Escalada")
        self.post = Posts.objects.create(user=self.sender, category=self.hobby)
        self.event = Event.objects.create(
            title="Roco tarde",
            description="Plan",
            location="Arinaga",
            event_date=timezone.now() + timedelta(days=2),
            organizer=self.sender,
            hobby=self.hobby,
        )

    def test_notification_list_marks_all_as_read(self):
        Notification.objects.create(
            recipient=self.recipient,
            sender=self.sender,
            notification_type="like",
            post=self.post,
        )
        self.client.force_login(self.recipient)

        response = self.client.get(reverse("notifications:list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["notifications"].count(), 1)
        self.assertFalse(
            Notification.objects.filter(recipient=self.recipient, is_read=False).exists()
        )

    def test_unread_count_endpoint_and_context_processor(self):
        Notification.objects.create(
            recipient=self.recipient,
            sender=self.sender,
            notification_type="event",
            event=self.event,
        )
        self.client.force_login(self.recipient)

        response = self.client.get(reverse("notifications:api_unread_count"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "1")
        request = response.wsgi_request
        request.user = self.recipient
        self.assertEqual(unread_notifications(request), {"unread_notifications_count": 1})

    def test_notification_redirects_to_linked_targets_and_marks_read(self):
        self.client.force_login(self.recipient)
        like_notification = Notification.objects.create(
            recipient=self.recipient,
            sender=self.sender,
            notification_type="like",
            post=self.post,
        )
        event_notification = Notification.objects.create(
            recipient=self.recipient,
            sender=self.sender,
            notification_type="event",
            event=self.event,
        )
        follow_notification = Notification.objects.create(
            recipient=self.recipient,
            sender=self.sender,
            notification_type="follow",
        )

        like_response = self.client.get(
            reverse(
                "notifications:notification_redirect",
                kwargs={"pk": like_notification.pk},
            )
        )
        self.assertRedirects(
            like_response, reverse("posts:post_detail", kwargs={"pk": self.post.pk})
        )
        like_notification.refresh_from_db()
        self.assertTrue(like_notification.is_read)

        event_response = self.client.get(
            reverse(
                "notifications:read_and_redirect",
                kwargs={"notification_id": event_notification.pk},
            )
        )
        self.assertRedirects(
            event_response, reverse("posts:event_detail", kwargs={"pk": self.event.pk})
        )

        follow_response = self.client.get(
            reverse(
                "notifications:notification_redirect",
                kwargs={"pk": follow_notification.pk},
            )
        )
        self.assertRedirects(
            follow_response,
            reverse("profiles:profile", kwargs={"pk": self.sender.profile.pk}),
        )

    def test_delete_single_notification(self):
        notification = Notification.objects.create(
            recipient=self.recipient,
            sender=self.sender,
            notification_type="follow",
        )
        self.client.force_login(self.recipient)
        
        response = self.client.delete(
            reverse("notifications:delete_notification", kwargs={"pk": notification.pk})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["HX-Trigger"], "updateNotificationCount")
        self.assertFalse(Notification.objects.filter(pk=notification.pk).exists())

    def test_delete_all_notifications(self):
        Notification.objects.create(
            recipient=self.recipient, sender=self.sender, notification_type="follow"
        )
        Notification.objects.create(
            recipient=self.recipient, sender=self.sender, notification_type="like", post=self.post
        )
        
        self.client.force_login(self.recipient)
        
        response = self.client.delete(reverse("notifications:delete_all_notifications"))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["HX-Trigger"], "updateNotificationCount")
        self.assertIn("No tienes notificaciones en este momento", response.content.decode())
        self.assertEqual(Notification.objects.filter(recipient=self.recipient).count(), 0)


@override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)
class NotificationDispatcherAndArticleTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username="lucia", email="lucia@example.com", password="testpass123"
        )
        self.recipient = User.objects.create_user(
            username="carlos", email="carlos@example.com", password="testpass123"
        )
        self.hobby = Hobby.objects.create(name="Fitoterapia", slug="fitoterapia")
        self.article = Article.objects.create(
            title="Beneficios de la Lavanda",
            slug="beneficios-de-la-lavanda",
            content="Contenido médico",
            author=self.recipient,
            hobby=self.hobby,
        )

    def test_dispatcher_prevents_self_notification_on_social_actions(self):
        result = NotificationDispatcher.dispatch(
            notification_type="like",
            sender=self.recipient,
            recipient=self.recipient,
        )
        self.assertIsNone(result)
        self.assertEqual(Notification.objects.count(), 0)

    def test_dispatcher_enforces_anti_spam_rule_for_likes(self):
        mail.outbox.clear()
        notif = NotificationDispatcher.dispatch(
            notification_type="like",
            sender=self.sender,
            recipient=self.recipient,
            send_email=True,  # Intento de enviar email en un like
        )
        self.assertIsNotNone(notif)
        self.assertEqual(notif.notification_type, "like")
        self.assertEqual(len(mail.outbox), 0)  # Cero correos enviados por like

    def test_dispatcher_creates_notification_and_dispatches_email(self):
        mail.outbox.clear()
        notif = NotificationDispatcher.dispatch(
            notification_type="comment",
            sender=self.sender,
            recipient=self.recipient,
            message="ha comentado en tu publicación",
            send_email=True,
            email_subject="Nuevo comentario",
            email_body="Hola, tienes un nuevo comentario",
            action_url="/posts/1/",
        )
        self.assertIsNotNone(notif)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Nuevo comentario", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ["carlos@example.com"])

    def test_article_comment_and_rating_redirection(self):
        self.client.force_login(self.recipient)
        comment_notif = NotificationDispatcher.dispatch(
            notification_type="article_comment",
            sender=self.sender,
            recipient=self.recipient,
            article=self.article,
        )
        rating_notif = NotificationDispatcher.dispatch(
            notification_type="article_rating",
            sender=self.sender,
            recipient=self.recipient,
            article=self.article,
        )

        response_comment = self.client.get(
            reverse("notifications:notification_redirect", kwargs={"pk": comment_notif.pk})
        )
        self.assertRedirects(
            response_comment,
            reverse("library:article_detail", kwargs={"slug": self.article.slug}),
        )

        response_rating = self.client.get(
            reverse("notifications:read_and_redirect", kwargs={"notification_id": rating_notif.pk})
        )
        self.assertRedirects(
            response_rating,
            reverse("library:article_detail", kwargs={"slug": self.article.slug}),
        )
