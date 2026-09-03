from django.test import TestCase
from django.contrib.auth.models import User
from profiles.models import Hobby
from library.models import Article


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

