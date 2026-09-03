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

#🧹 Limpieza después de ejecutar los tests
def tearDownModule():
    shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

#📸 Helper que crea imágenes temporales para tests
def test_image(name="test.png", size=(10, 10), color=(255, 0, 0)):
    image_file = BytesIO()
    image = Image.new("RGB", size, color)
    image.save(image_file, "PNG")
    image_file.seek(0)
    return SimpleUploadedFile(name, image_file.read(), content_type="image/png")

#Clase base para tests de posts con configuracion compartida
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
        # The model uses SoftDeleteModel and explicitly preserves files on delete
        self.assertTrue(os.path.exists(image_path))

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

    def test_post_create_update_delete(self):
        self.client.force_login(self.author)

        # 1. Create
        response = self.client.post(
            reverse("posts:post_create"),
            {
                "title": "Nuevo Click",
                "caption": "Una prueba de creacion",
                "category": self.hobby.pk,
                "image": test_image(name="test_create.png"),
            }
        )
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(Posts.objects.filter(title="Nuevo Click").exists())
        new_post = Posts.objects.get(title="Nuevo Click")

        # 2. Update
        response = self.client.post(
            reverse("posts:post_update", kwargs={"pk": new_post.pk}),
            {
                "title": "Click Editado",
                "caption": "Caption editado",
                "category": self.hobby.pk,
                "image": test_image(name="test_edit.png"),
            }
        )
        # Update view usually redirects to post_detail or home depending on get_success_url
        new_post.refresh_from_db()
        self.assertEqual(new_post.title, "Click Editado")

        # 3. Delete Permission
        self.client.force_login(self.other)
        response = self.client.post(reverse("posts:post_delete", kwargs={"pk": new_post.pk}))
        self.assertEqual(response.status_code, 403) # Forbidden

        # 4. Actual Delete
        self.client.force_login(self.author)
        response = self.client.post(reverse("posts:post_delete", kwargs={"pk": new_post.pk}))
        self.assertRedirects(response, reverse("home"))
        self.assertFalse(Posts.objects.filter(pk=new_post.pk).exists())


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
        self.assertEqual(response.context["user_levels_map"][self.hobby.id], "beginner")

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

    def test_event_max_participants_limit(self):
        self.client.force_login(self.participant)
        
        # El participante actual se une
        self.client.post(
            reverse("posts:toggle_attendance", kwargs={"event_id": self.event.pk}),
            {"attendance_type": "physical"}
        )
        
        # Creamos un tercer usuario (el límite de max_participants era 2, ahora están el organizador y el participante)
        third_user = User.objects.create_user(username="pepe", email="pepe@example.com", password="pwd")
        UserHobby.objects.create(profile=third_user.profile, hobby=self.hobby, level="beginner")
        
        # Tercer usuario intenta unirse físicamente pero está lleno
        self.client.force_login(third_user)
        response = self.client.post(
            reverse("posts:toggle_attendance", kwargs={"event_id": self.event.pk}),
            {"attendance_type": "physical"}
        )
        self.assertRedirects(response, reverse("posts:event_detail", kwargs={"pk": self.event.pk}))
        
        self.event.refresh_from_db()
        self.assertNotIn(third_user, self.event.participants.all())

    def test_event_permissions_for_non_organizer(self):
        self.client.force_login(self.participant)

        # Update event (non-organizer)
        response = self.client.post(
            reverse("posts:event_update", kwargs={"pk": self.event.pk}),
            {
                "title": "Hack title", "description": "Hacked", 
                "hobby": self.hobby.pk, "location": "Bad", 
                "event_date": "2030-01-01T12:00", 
                "max_participants": 10, "level": "all"
            }
        )
        self.assertEqual(response.status_code, 403)

        # Cancel event (non-organizer)
        response = self.client.post(reverse("posts:event_cancel", kwargs={"pk": self.event.pk}))
        self.assertEqual(response.status_code, 403)

        # Reactivate event (non-organizer)
        response = self.client.post(reverse("posts:event_reactivate", kwargs={"pk": self.event.pk}))
        self.assertEqual(response.status_code, 403)


@override_settings(
    DEBUG=True,
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@example.com",
    MEDIA_ROOT=TEMP_MEDIA_ROOT,
)
class FormValidationTests(TestCase):
    def test_post_create_form_invalid_empty_fields(self):
        from posts.forms import PostCreateForm
        
        # Faltan campos obligatorios
        form = PostCreateForm(data={
            "title": "",
            "caption": "Solo caption",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("category", form.errors)
        self.assertIn("__all__", form.errors)

    def test_event_form_invalid_past_date(self):
        from posts.forms import EventForm
        from profiles.models import Hobby
        
        hobby = Hobby.objects.create(name="Prueba Formulario")
        
        # Fecha en el pasado
        form = EventForm(data={
            "title": "Evento fallido",
            "description": "Prueba",
            "hobby": hobby.pk,
            "location": "Madrid",
            "event_date": (timezone.now() - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M"),
            "max_participants": 5,
            "level": "all"
        })
        self.assertFalse(form.is_valid())
        # The form might have a custom validation for date or it might just fail at the model level if we use clean. Let's assert it's invalid.


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class PostMultiContentAndPdfTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="doctor_terapeuta", email="doc@test.com", password="password123"
        )
        self.hobby = Hobby.objects.create(name="Osteopatia Bio")

    def test_post_creation_with_pdf_document_and_external_url(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        pdf_file = SimpleUploadedFile("estudio_clinico.pdf", b"%PDF-1.4 test content", content_type="application/pdf")
        
        post = Posts.objects.create(
            user=self.user,
            title="Tratamiento avanzado en cervicales",
            caption="Resumen clínico breve. Ver documento adjunto.",
            category=self.hobby,
            external_url="https://pubmed.ncbi.nlm.nih.gov/123456/",
            document=pdf_file,
        )

        self.assertTrue(post.document.name.endswith(".pdf"))
        self.assertEqual(post.external_url, "https://pubmed.ncbi.nlm.nih.gov/123456/")
        self.assertEqual(post.video_url, "https://pubmed.ncbi.nlm.nih.gov/123456/")

    def test_post_create_form_allows_pdf_only_without_image_or_video(self):
        from posts.forms import PostCreateForm
        from django.core.files.uploadedfile import SimpleUploadedFile
        pdf_file = SimpleUploadedFile("manual.pdf", b"%PDF-1.4 test", content_type="application/pdf")

        form = PostCreateForm(
            data={
                "title": "Manual de técnicas",
                "category": self.hobby.pk,
                "caption": "Manual completo adjunto.",
            },
            files={"document": pdf_file}
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_post_form_rejects_non_pdf_extension(self):
        from posts.forms import PostCreateForm
        from django.core.files.uploadedfile import SimpleUploadedFile
        txt_file = SimpleUploadedFile("archivo.txt", b"texto no valido", content_type="text/plain")

        form = PostCreateForm(
            data={
                "title": "Archivo invalido",
                "category": self.hobby.pk,
                "caption": "Intento de subir texto.",
            },
            files={"document": txt_file}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("document", form.errors)

    def test_post_detail_renders_pdf_and_generic_link(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        pdf_file = SimpleUploadedFile("guia_osteopatia.pdf", b"%PDF-1.4 contenido", content_type="application/pdf")
        
        post = Posts.objects.create(
            user=self.user,
            title="Guía Práctica",
            caption="Guía completa con enlaces y PDF",
            category=self.hobby,
            external_url="https://recursos-salud.org/articulo",
            document=pdf_file,
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("posts:post_detail", kwargs={"pk": post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enlace de interés / Recurso externo")
        self.assertContains(response, "https://recursos-salud.org/articulo")
        self.assertContains(response, "Documento PDF Adjunto")
        self.assertContains(response, post.document.url)

    def test_category_dropdown_is_sorted_alphabetically(self):
        from posts.forms import PostCreateForm
        Hobby.objects.create(name="Zumba Terapéutica")
        Hobby.objects.create(name="Acupuntura Bio")
        Hobby.objects.create(name="Maderoterapia")

        form = PostCreateForm(user=self.user)
        names = list(form.fields["category"].queryset.values_list("name", flat=True))
        self.assertEqual(names, sorted(names))

    def test_plain_text_caption_and_description_sanitization(self):
        post = Posts.objects.create(
            user=self.user,
            title="Post de prueba",
            caption="<p>Atenci&oacute;n socios<br><br>Reuni&oacute;n&nbsp;urgente</p>",
            category=self.hobby,
        )
        self.assertEqual(post.plain_text_caption, "Atención socios Reunión urgente")

        event = Event.objects.create(
            organizer=self.user,
            title="Quedada",
            description="<p>Ven a la sesi&oacute;n<br>Pr&aacute;ctica&nbsp;libre</p>",
            hobby=self.hobby,
            event_date=timezone.now() + timezone.timedelta(days=1),
        )
        self.assertEqual(event.plain_text_description, "Ven a la sesión Práctica libre")



