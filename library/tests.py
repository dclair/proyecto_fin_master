from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from library.models import Article, ArticleComment, ArticleRating
from notifications.models import Notification
from profiles.models import Hobby


class ArticlePlainTextSummaryTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="author1", email="author1@test.com", password="password123")
        self.hobby = Hobby.objects.create(name="Fitoterapia", slug="fitoterapia")

    def test_plain_text_summary_decodes_entities_and_separates_block_tags(self):
        content = '<p>Qu&eacute; es exactamente la astenia<br><br>La <strong>astenia</strong>&nbsp;adaptaci&oacute;n</p>'
        article = Article.objects.create(
            title="Test Article",
            author=self.user,
            hobby=self.hobby,
            content=content,
        )
        summary = article.plain_text_summary
        self.assertEqual(summary, "Qué es exactamente la astenia La astenia adaptación")


@override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)
class ArticleNotificationAndRatingTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="autor", email="autor@test.com", password="password123"
        )
        self.reader = User.objects.create_user(
            username="lector", email="lector@test.com", password="password123"
        )
        self.hobby = Hobby.objects.create(name="Acupuntura", slug="acupuntura")
        self.article = Article.objects.create(
            title="Principios de Acupuntura",
            slug="principios-de-acupuntura",
            author=self.author,
            hobby=self.hobby,
            content="Texto explicativo",
        )

    def test_add_comment_dispatches_notification_and_celery_email(self):
        mail.outbox.clear()
        self.client.force_login(self.reader)
        response = self.client.post(
            reverse("library:add_comment", kwargs={"slug": self.article.slug}),
            {"content": "Excelente artículo explicativo."},
        )
        self.assertRedirects(
            response, reverse("library:article_detail", kwargs={"slug": self.article.slug})
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.author,
                sender=self.reader,
                notification_type="article_comment",
                article=self.article,
            ).exists()
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Nuevo comentario en tu artículo", mail.outbox[0].subject)

    def test_rate_article_dispatches_notification_and_celery_email(self):
        mail.outbox.clear()
        self.client.force_login(self.reader)
        response = self.client.post(
            reverse("library:rate_article", kwargs={"slug": self.article.slug}),
            {"rating": "5"},
        )
        self.assertRedirects(
            response, reverse("library:article_detail", kwargs={"slug": self.article.slug})
        )
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.author,
                sender=self.reader,
                notification_type="article_rating",
                article=self.article,
            ).exists()
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Nueva valoración en tu artículo", mail.outbox[0].subject)


@override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)
class ArticleSecurityTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="autor_original", email="autor@test.com", password="password123"
        )
        self.other_user = User.objects.create_user(
            username="otro_usuario", email="otro@test.com", password="password123"
        )
        self.hobby = Hobby.objects.create(name="Osteopatía", slug="osteopatia")
        self.article = Article.objects.create(
            title="Guía de Osteopatía Craneal",
            slug="guia-osteopatia-craneal",
            author=self.author,
            hobby=self.hobby,
            content="Contenido protegido",
        )

    def test_non_author_cannot_edit_article_forbidden(self):
        self.client.force_login(self.other_user)
        update_url = reverse("library:article_update", kwargs={"slug": self.article.slug})
        # GET del formulario debe devolver 403 Forbidden
        response_get = self.client.get(update_url)
        self.assertEqual(response_get.status_code, 403)
        # POST modificando datos debe devolver 403 Forbidden
        response_post = self.client.post(update_url, {
            "title": "Hacked Title",
            "hobby": self.hobby.id,
            "content": "Malicious content",
        })
        self.assertEqual(response_post.status_code, 403)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, "Guía de Osteopatía Craneal")

    def test_non_author_cannot_delete_article_forbidden(self):
        self.client.force_login(self.other_user)
        delete_url = reverse("library:article_delete", kwargs={"slug": self.article.slug})
        # GET confirmación de borrado debe devolver 403 Forbidden
        response_get = self.client.get(delete_url)
        self.assertEqual(response_get.status_code, 403)
        # POST borrado debe devolver 403 Forbidden
        response_post = self.client.post(delete_url)
        self.assertEqual(response_post.status_code, 403)
        self.assertTrue(Article.objects.filter(id=self.article.id).exists())


