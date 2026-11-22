import time
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from chat.models import Conversation, ConversationParticipant, GroupJoinRequest
from gamification.services import award_badge, send_motivation_warning
from library.models import Article
from notifications.models import Notification
from notifications.services import NotificationDispatcher
from posts.models import Event, EventAttendance, Posts
from profiles.models import Follow, Hobby, Review


@override_settings(
    DEBUG=True,
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@aficionados.com",
)
class EventNotificationTests(TestCase):
    """
    Pruebas integrales de notificaciones y correos para QUEDADAS / EVENTOS:
    - Asistencia confirmada a evento.
    - Baja de asistencia a evento.
    - Cancelación de evento por creador.
    - Reactivación de evento por creador.
    - Comentario en el muro de evento (por asistente y por organizador).
    """

    def setUp(self):
        mail.outbox.clear()
        self.organizer = User.objects.create_user(
            username="organizador",
            email="organizador@example.com",
            password="TestPassword123!",
        )
        self.attendee1 = User.objects.create_user(
            username="asistente1",
            email="asistente1@example.com",
            password="TestPassword123!",
        )
        self.attendee2 = User.objects.create_user(
            username="asistente2",
            email="asistente2@example.com",
            password="TestPassword123!",
        )
        self.hobby = Hobby.objects.create(name="Senderismo", slug="senderismo")
        self.event = Event.objects.create(
            title="Ruta Cumbre Vieja",
            description="Excursión de senderismo botánico",
            location="La Palma",
            event_date=timezone.now() + timedelta(days=3),
            organizer=self.organizer,
            hobby=self.hobby,
            max_participants=10,
        )

    def test_event_attendance_confirmed_dispatches_notification_and_email(self):
        """Asistencia confirmada a evento -> Campanita + Email en mail.outbox para el organizador."""
        self.client.force_login(self.attendee1)
        response = self.client.post(
            reverse("posts:toggle_attendance", kwargs={"event_id": self.event.id}),
            {"attendance_type": "physical"},
        )
        self.assertRedirects(
            response, reverse("posts:event_detail", kwargs={"pk": self.event.id})
        )

        # 1. Campanita en base de datos para el organizador
        notif = Notification.objects.filter(
            recipient=self.organizer,
            sender=self.attendee1,
            notification_type="event",
            event=self.event,
        ).first()
        self.assertIsNotNone(notif)
        self.assertIn("se ha apuntado", notif.text)

        # 2. Correo transaccional en mail.outbox
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["organizador@example.com"])
        self.assertIn("Alguien se ha unido", mail.outbox[0].subject)
        self.assertIn(self.event.title, mail.outbox[0].subject)

    def test_event_attendance_leave_dispatches_notification_and_email(self):
        """Baja de asistencia a evento -> Campanita + Email en mail.outbox para el organizador."""
        # Inscribir previamente al asistente
        EventAttendance.objects.create(
            event=self.event, user=self.attendee1, attendance_type="physical"
        )
        mail.outbox.clear()
        Notification.objects.all().delete()

        self.client.force_login(self.attendee1)
        response = self.client.post(
            reverse("posts:toggle_attendance", kwargs={"event_id": self.event.id})
        )
        self.assertRedirects(
            response, reverse("posts:event_detail", kwargs={"pk": self.event.id})
        )

        # 1. Campanita de baja para el organizador
        notif = Notification.objects.filter(
            recipient=self.organizer,
            sender=self.attendee1,
            notification_type="event",
            event=self.event,
        ).first()
        self.assertIsNotNone(notif)
        self.assertIn("desapuntado", notif.message)

        # 2. Correo de baja para el organizador
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["organizador@example.com"])
        self.assertIn("Baja en tu evento", mail.outbox[0].subject)
        self.assertIn(self.event.title, mail.outbox[0].subject)

    def test_event_cancellation_by_creator_dispatches_notifications_and_emails_to_all_attendees(self):
        """Cancelación de evento por creador -> Campanita + Email a todos los asistentes."""
        EventAttendance.objects.create(
            event=self.event, user=self.attendee1, attendance_type="physical"
        )
        EventAttendance.objects.create(
            event=self.event, user=self.attendee2, attendance_type="online"
        )
        mail.outbox.clear()
        Notification.objects.all().delete()

        self.client.force_login(self.organizer)
        response = self.client.post(
            reverse("posts:event_cancel", kwargs={"pk": self.event.pk})
        )
        self.assertRedirects(
            response, reverse("posts:event_detail", kwargs={"pk": self.event.pk})
        )
        self.event.refresh_from_db()
        self.assertTrue(self.event.is_canceled)

        # 1. Notificaciones en DB para ambos asistentes
        for attendee in [self.attendee1, self.attendee2]:
            self.assertTrue(
                Notification.objects.filter(
                    recipient=attendee,
                    sender=self.organizer,
                    notification_type="event",
                    event=self.event,
                ).exists()
            )

        # Anti-autoalerta: El organizador no se auto-notifica
        self.assertFalse(
            Notification.objects.filter(recipient=self.organizer).exists()
        )

        # 2. Correos para todos los asistentes inscritos
        self.assertEqual(len(mail.outbox), 2)
        destinatarios = [m.to[0] for m in mail.outbox]
        self.assertIn("asistente1@example.com", destinatarios)
        self.assertIn("asistente2@example.com", destinatarios)
        for msg in mail.outbox:
            self.assertIn("Quedada cancelada", msg.subject)
            self.assertIn(self.event.title, msg.subject)

    def test_event_reactivation_by_creator_dispatches_notifications_and_emails_to_all_attendees(self):
        """Reactivación de evento por creador -> Campanita + Email a todos los asistentes."""
        self.event.is_canceled = True
        self.event.save()
        EventAttendance.objects.create(
            event=self.event, user=self.attendee1, attendance_type="physical"
        )
        EventAttendance.objects.create(
            event=self.event, user=self.attendee2, attendance_type="online"
        )
        mail.outbox.clear()
        Notification.objects.all().delete()

        self.client.force_login(self.organizer)
        response = self.client.post(
            reverse("posts:event_reactivate", kwargs={"pk": self.event.pk})
        )
        self.assertRedirects(
            response, reverse("posts:event_detail", kwargs={"pk": self.event.pk})
        )
        self.event.refresh_from_db()
        self.assertFalse(self.event.is_canceled)

        # 1. Notificaciones en DB
        for attendee in [self.attendee1, self.attendee2]:
            self.assertTrue(
                Notification.objects.filter(
                    recipient=attendee,
                    sender=self.organizer,
                    notification_type="event",
                    event=self.event,
                ).exists()
            )

        # 2. Correos a todos los asistentes
        self.assertEqual(len(mail.outbox), 2)
        destinatarios = [m.to[0] for m in mail.outbox]
        self.assertIn("asistente1@example.com", destinatarios)
        self.assertIn("asistente2@example.com", destinatarios)
        for msg in mail.outbox:
            self.assertIn("reactivado", msg.subject.lower())
            self.assertIn(self.event.title, msg.subject)

    def test_event_wall_comment_by_attendee_dispatches_notification_and_email_to_organizer(self):
        """Comentario en el muro de evento por asistente -> Notificación y Email al organizador."""
        self.client.force_login(self.attendee1)
        response = self.client.post(
            reverse("posts:add_event_comment", kwargs={"event_id": self.event.id}),
            {"content": "¿A qué hora exacta nos encontramos en el punto de salida?"},
        )
        self.assertRedirects(
            response, reverse("posts:event_detail", kwargs={"pk": self.event.id})
        )

        # 1. Campanita al organizador
        notif = Notification.objects.filter(
            recipient=self.organizer,
            sender=self.attendee1,
            notification_type="comment",
            event=self.event,
        ).first()
        self.assertIsNotNone(notif)

        # 2. Email al organizador
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["organizador@example.com"])
        self.assertIn("Nuevo comentario", mail.outbox[0].subject)

    def test_event_wall_comment_by_organizer_dispatches_notifications_and_emails_to_all_participants(self):
        """Comentario del organizador en el muro -> Notificación y Email a todos los participantes inscritos."""
        EventAttendance.objects.create(
            event=self.event, user=self.attendee1, attendance_type="physical"
        )
        EventAttendance.objects.create(
            event=self.event, user=self.attendee2, attendance_type="online"
        )
        mail.outbox.clear()
        Notification.objects.all().delete()

        self.client.force_login(self.organizer)
        response = self.client.post(
            reverse("posts:add_event_comment", kwargs={"event_id": self.event.id}),
            {"content": "He añadido el mapa detallado de la ruta en la descripción."},
        )
        self.assertRedirects(
            response, reverse("posts:event_detail", kwargs={"pk": self.event.id})
        )

        # 1. Notificaciones en DB para participantes (excluyendo al organizador)
        self.assertEqual(
            Notification.objects.filter(
                sender=self.organizer, notification_type="comment", event=self.event
            ).count(),
            2,
        )
        self.assertFalse(
            Notification.objects.filter(recipient=self.organizer).exists()
        )

        # 2. Correos para los participantes
        self.assertEqual(len(mail.outbox), 2)
        destinatarios = [m.to[0] for m in mail.outbox]
        self.assertIn("asistente1@example.com", destinatarios)
        self.assertIn("asistente2@example.com", destinatarios)
        for msg in mail.outbox:
            self.assertIn("ha respondido", msg.subject)


@override_settings(
    DEBUG=True,
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@aficionados.com",
)
class PostAndClickNotificationTests(TestCase):
    """
    Pruebas integrales de notificaciones y correos para PUBLICACIONES & CLICKS:
    - Like a publicación: SÍ crea Notification (campanita), pero NUNCA envía email (0 emails).
    - Comentario en publicación: SÍ crea Notification + Email en mail.outbox.
    - Like a click (foto): SÍ crea Notification, 0 emails.
    - Comentario en click: SÍ crea Notification + Email en mail.outbox.
    """

    def setUp(self):
        mail.outbox.clear()
        self.author = User.objects.create_user(
            username="autor", email="autor@example.com", password="TestPassword123!"
        )
        self.interactor = User.objects.create_user(
            username="interactor",
            email="interactor@example.com",
            password="TestPassword123!",
        )
        self.hobby = Hobby.objects.create(name="Fitoterapia", slug="fitoterapia")
        # Post estándar
        self.standard_post = Posts.objects.create(
            user=self.author,
            title="Propiedades del Romero",
            caption="El romero es excelente para la memoria.",
            category=self.hobby,
        )
        # Click (Publicación con imagen fotográfica válida)
        import io
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile

        f = io.BytesIO()
        img = Image.new("RGB", (10, 10), color="blue")
        img.save(f, format="JPEG")
        f.seek(0)
        click_image = SimpleUploadedFile("click.jpg", f.read(), content_type="image/jpeg")

        self.click_post = Posts.objects.create(
            user=self.author,
            title="Fotografía Macro de Romero",
            caption="Detalle de floración en primavera.",
            image=click_image,
            category=self.hobby,
        )

    def test_post_like_creates_bell_notification_and_zero_emails(self):
        """Like a publicación -> SÍ crea Notification (campanita), pero NUNCA envía email (0 emails)."""
        self.client.force_login(self.interactor)
        response = self.client.post(
            reverse("posts:toggle_like", kwargs={"post_id": self.standard_post.id})
        )
        self.assertEqual(response.status_code, 200)

        # 1. Campanita creada
        notif = Notification.objects.filter(
            recipient=self.author,
            sender=self.interactor,
            notification_type="like",
            post=self.standard_post,
        ).first()
        self.assertIsNotNone(notif)

        # 2. CERO correos enviados (regla anti-spam estricta)
        self.assertEqual(len(mail.outbox), 0)

    def test_post_comment_creates_notification_and_email_to_author(self):
        """Comentario en publicación -> SÍ crea Notification + Email en mail.outbox al autor."""
        self.client.force_login(self.interactor)
        response = self.client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.standard_post.id}),
            {"comment": "Excelente explicación sobre el romero, muchas gracias."},
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"pk": self.standard_post.id}),
        )

        # 1. Campanita creada
        notif = Notification.objects.filter(
            recipient=self.author,
            sender=self.interactor,
            notification_type="comment",
            post=self.standard_post,
        ).first()
        self.assertIsNotNone(notif)
        self.assertIsNotNone(notif.comment)

        # 2. Correo enviado al autor del post
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["autor@example.com"])
        self.assertIn("Nuevo comentario", mail.outbox[0].subject)
        self.assertIn("interactor", mail.outbox[0].subject)

    def test_click_photo_like_creates_bell_notification_and_zero_emails(self):
        """Like a click (foto) -> SÍ crea Notification (campanita), 0 emails."""
        self.client.force_login(self.interactor)
        response = self.client.post(
            reverse("posts:toggle_like", kwargs={"post_id": self.click_post.id})
        )
        self.assertEqual(response.status_code, 200)

        # 1. Campanita en base de datos
        notif = Notification.objects.filter(
            recipient=self.author,
            sender=self.interactor,
            notification_type="like",
            post=self.click_post,
        ).first()
        self.assertIsNotNone(notif)

        # 2. Regla anti-spam: 0 emails
        self.assertEqual(len(mail.outbox), 0)

    def test_click_photo_comment_creates_notification_and_email(self):
        """Comentario en click -> SÍ crea Notification + Email en mail.outbox."""
        self.client.force_login(self.interactor)
        response = self.client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.click_post.id}),
            {"comment": "Qué nitidez de imagen botánica. ¡Magnífico click!"},
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"pk": self.click_post.id}),
        )

        # 1. Campanita en base de datos
        notif = Notification.objects.filter(
            recipient=self.author,
            sender=self.interactor,
            notification_type="comment",
            post=self.click_post,
        ).first()
        self.assertIsNotNone(notif)

        # 2. Email al autor de la foto
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["autor@example.com"])
        self.assertIn("Nuevo comentario", mail.outbox[0].subject)


@override_settings(
    DEBUG=True,
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@aficionados.com",
)
class GroupChatNotificationTests(TestCase):
    """
    Pruebas integrales de notificaciones y correos para CHAT GRUPAL:
    - Solicitud de acceso a grupo cerrado: Notificación + Email al admin del grupo.
    - Solicitud aprobada: Notificación + Email al solicitante.
    - Solicitud rechazada: Notificación + Email al solicitante.
    """

    def setUp(self):
        mail.outbox.clear()
        self.admin = User.objects.create_user(
            username="admin_grupo",
            email="admin_grupo@example.com",
            password="TestPassword123!",
        )
        self.applicant = User.objects.create_user(
            username="solicitante",
            email="solicitante@example.com",
            password="TestPassword123!",
        )
        self.conversation = Conversation.objects.create(
            is_group=True,
            name="Círculo de Osteopatía",
            admin=self.admin,
        )
        ConversationParticipant.objects.create(
            conversation=self.conversation, user=self.admin
        )

    def test_group_join_request_dispatches_notification_and_email_to_admin(self):
        """Solicitud de acceso a grupo cerrado -> SÍ crea Notification + Email en mail.outbox al admin del grupo."""
        self.client.force_login(self.applicant)
        url = reverse(
            "api-groups-request-join",
            kwargs={"conversation_id": self.conversation.id},
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

        # 1. Campanita al administrador
        notif = Notification.objects.filter(
            recipient=self.admin,
            sender=self.applicant,
            notification_type="chat_request",
        ).first()
        self.assertIsNotNone(notif)
        self.assertIn("ha solicitado unirse", notif.message)

        # 2. Email en mail.outbox al admin
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["admin_grupo@example.com"])
        self.assertIn("Solicitud de acceso a grupo de chat", mail.outbox[0].subject)
        self.assertIn("Círculo de Osteopatía", mail.outbox[0].subject)

    def test_group_join_request_approved_dispatches_notification_and_email_to_applicant(self):
        """Solicitud aprobada -> SÍ crea Notification + Email en mail.outbox al solicitante."""
        join_req = GroupJoinRequest.objects.create(
            conversation=self.conversation, user=self.applicant, status="pending"
        )
        mail.outbox.clear()

        self.client.force_login(self.admin)
        url = reverse(
            "api-groups-manage-request", kwargs={"request_id": join_req.id}
        )
        response = self.client.post(
            url, {"action": "accept"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # 1. Campanita al solicitante
        notif = Notification.objects.filter(
            recipient=self.applicant,
            sender=self.admin,
            notification_type="chat_accepted",
        ).first()
        self.assertIsNotNone(notif)
        self.assertIn("ha aceptado tu solicitud", notif.message)

        # 2. Email al solicitante
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["solicitante@example.com"])
        self.assertIn("Aceptado en el grupo", mail.outbox[0].subject)
        self.assertIn("Círculo de Osteopatía", mail.outbox[0].subject)

    def test_group_join_request_rejected_dispatches_notification_and_email_to_applicant(self):
        """Solicitud rechazada -> SÍ crea Notification + Email en mail.outbox al solicitante."""
        join_req = GroupJoinRequest.objects.create(
            conversation=self.conversation, user=self.applicant, status="pending"
        )
        mail.outbox.clear()

        self.client.force_login(self.admin)
        url = reverse(
            "api-groups-manage-request", kwargs={"request_id": join_req.id}
        )
        response = self.client.post(
            url, {"action": "reject"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # 1. Campanita al solicitante
        notif = Notification.objects.filter(
            recipient=self.applicant,
            sender=self.admin,
            notification_type="chat_rejected",
        ).first()
        self.assertIsNotNone(notif)
        self.assertIn("ha rechazado tu solicitud", notif.message)

        # 2. Email al solicitante
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["solicitante@example.com"])
        self.assertIn("Solicitud al grupo", mail.outbox[0].subject)
        self.assertIn("Círculo de Osteopatía", mail.outbox[0].subject)


@override_settings(
    DEBUG=True,
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@aficionados.com",
)
class ReviewNotificationTests(TestCase):
    """
    Pruebas integrales de notificaciones y correos para RESEÑAS Y VALORACIONES:
    - Nueva reseña a organizador -> SÍ crea Notification + Email en mail.outbox al anfitrión.
    """

    def setUp(self):
        mail.outbox.clear()
        self.host = User.objects.create_user(
            username="anfitrion",
            email="anfitrion@example.com",
            password="TestPassword123!",
        )
        self.reviewer = User.objects.create_user(
            username="evaluador",
            email="evaluador@example.com",
            password="TestPassword123!",
        )
        self.hobby = Hobby.objects.create(name="Meditación", slug="meditacion")
        # El evento debe ser en el pasado para poder ser valorado
        self.past_event = Event.objects.create(
            title="Taller Mindfulness Pasado",
            description="Sesión práctica de relajación",
            location="Parque Central",
            event_date=timezone.now() - timedelta(days=2),
            organizer=self.host,
            hobby=self.hobby,
        )
        # El evaluador debe haber sido participante
        EventAttendance.objects.create(
            event=self.past_event, user=self.reviewer, attendance_type="physical"
        )

    def test_new_review_dispatches_notification_and_email_to_event_host(self):
        """Nueva reseña a organizador -> SÍ crea Notification + Email en mail.outbox al anfitrión."""
        self.client.force_login(self.reviewer)
        response = self.client.post(
            reverse("profiles:add_review", kwargs={"event_id": self.past_event.id}),
            {"rating": 5, "comment": "Una facilitación impecable y gran calidez humana."},
        )
        self.assertRedirects(response, reverse("posts:my_participations"))

        # 1. Campanita al organizador / anfitrión
        notif = Notification.objects.filter(
            recipient=self.host,
            sender=self.reviewer,
            notification_type="review",
            event=self.past_event,
        ).first()
        self.assertIsNotNone(notif)
        self.assertIsNotNone(notif.review)
        self.assertEqual(notif.review.rating, 5)

        # 2. Email al organizador / anfitrión
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["anfitrion@example.com"])
        self.assertIn("Nueva valoración recibida", mail.outbox[0].subject)
        self.assertIn(self.past_event.title, mail.outbox[0].subject)


@override_settings(
    DEBUG=True,
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@aficionados.com",
)
class FollowNotificationTests(TestCase):
    """
    Pruebas integrales de notificaciones para SEGUIDORES (FOLLOW):
    - Nuevo seguidor -> SÍ crea Notification (campanita), 0 emails.
    - Regla anti-spam estricta: Follow jamás genera correo saliente.
    """

    def setUp(self):
        mail.outbox.clear()
        self.target_user = User.objects.create_user(
            username="figura_seguida",
            email="figura@example.com",
            password="TestPassword123!",
        )
        self.follower_user = User.objects.create_user(
            username="seguidor",
            email="seguidor@example.com",
            password="TestPassword123!",
        )

    def test_new_follower_creates_bell_notification_and_zero_emails(self):
        """Nuevo seguidor -> SÍ crea Notification (campanita), 0 emails."""
        self.client.force_login(self.follower_user)
        response = self.client.post(
            reverse(
                "profiles:profile",
                kwargs={"pk": self.target_user.profile.pk},
            ),
            {"profile_pk": self.target_user.profile.pk},
        )
        self.assertRedirects(
            response,
            reverse(
                "profiles:profile", kwargs={"pk": self.target_user.profile.pk}
            ),
        )

        # 1. Campanita para el usuario seguido
        notif = Notification.objects.filter(
            recipient=self.target_user,
            sender=self.follower_user,
            notification_type="follow",
        ).first()
        self.assertIsNotNone(notif)
        self.assertIn("ha empezado a seguirte", notif.text)

        # 2. Regla anti-spam: 0 emails generados
        self.assertEqual(len(mail.outbox), 0)

    def test_follow_signal_creates_notification_and_zero_emails(self):
        """Creación directa mediante Follow model signal no despacha correos."""
        Follow.objects.create(
            follower=self.follower_user.profile,
            following=self.target_user.profile,
        )

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.target_user,
                sender=self.follower_user,
                notification_type="follow",
            ).exists()
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_anti_spam_follow_enforces_zero_emails_even_if_send_email_requested(self):
        """Incluso si se invoca el Dispatcher con send_email=True en un follow, se fuerzan 0 correos."""
        notif = NotificationDispatcher.dispatch(
            notification_type="follow",
            sender=self.follower_user,
            recipient=self.target_user,
            send_email=True,
        )
        self.assertIsNotNone(notif)
        self.assertEqual(len(mail.outbox), 0)


@override_settings(
    DEBUG=True,
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@aficionados.com",
)
class GamificationNotificationTests(TestCase):
    """
    Pruebas integrales de notificaciones y correos para GAMIFICACIÓN:
    - Medalla / logro desbloqueado -> SÍ crea Notification + Email HTML en mail.outbox.
    - Advertencia motivacional de medalla -> SÍ crea Notification + Email HTML en mail.outbox.
    """

    def setUp(self):
        mail.outbox.clear()
        self.user = User.objects.create_user(
            username="terapeuta_estrella",
            email="terapeuta_estrella@example.com",
            password="TestPassword123!",
        )

    def test_badge_unlocked_dispatches_notification_and_html_email(self):
        """Medalla / logro desbloqueado -> SÍ crea Notification + Email HTML en mail.outbox."""
        award_badge(
            user=self.user,
            code_name="maestro-facilitador",
            name_fallback="Maestro Facilitador",
            icon_fallback="award",
        )

        # 1. Campanita con tipo badge y mensaje
        notif = Notification.objects.filter(
            recipient=self.user,
            notification_type="badge",
        ).first()
        self.assertIsNotNone(notif)
        self.assertIn("Has desbloqueado la medalla", notif.message)
        self.assertIn("Maestro Facilitador", notif.message)

        # 2. Email HTML enviado
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["terapeuta_estrella@example.com"])
        self.assertIn("Logro Desbloqueado", mail.outbox[0].subject)
        self.assertIn("Maestro Facilitador", mail.outbox[0].subject)

        # Comprobar presencia de alternativa HTML
        html_alternatives = [
            content
            for content, mime in mail.outbox[0].alternatives
            if mime == "text/html"
        ]
        self.assertTrue(len(html_alternatives) > 0)
        self.assertIn("Maestro Facilitador", html_alternatives[0])

    def test_motivation_warning_dispatches_notification_and_html_email(self):
        """Advertencia motivacional de medalla -> SÍ crea Notification + Email HTML en mail.outbox."""
        send_motivation_warning(self.user)

        # 1. Campanita en base de datos
        notif = Notification.objects.filter(
            recipient=self.user,
            notification_type="badge",
            message__icontains="estás a un solo evento",
        ).first()
        self.assertIsNotNone(notif)

        # 2. Email HTML enviado
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["terapeuta_estrella@example.com"])
        self.assertIn("próxima medalla", mail.outbox[0].subject.lower())

        html_alternatives = [
            content
            for content, mime in mail.outbox[0].alternatives
            if mime == "text/html"
        ]
        self.assertTrue(len(html_alternatives) > 0)


@override_settings(
    DEBUG=True,
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@aficionados.com",
)
class MedicalLibraryNotificationTests(TestCase):
    """
    Pruebas integrales de notificaciones para BIBLIOTECA MÉDICA:
    - Comentario en artículo -> SÍ crea Notification con FK article + Email en mail.outbox.
    - Calificación de artículo -> SÍ crea Notification con FK article + Email en mail.outbox.
    - Redirección desde la campanita hacia library:article_detail probada.
    """

    def setUp(self):
        mail.outbox.clear()
        self.author = User.objects.create_user(
            username="autor_medico",
            email="autor_medico@example.com",
            password="TestPassword123!",
        )
        self.reader = User.objects.create_user(
            username="lector_clinico",
            email="lector_clinico@example.com",
            password="TestPassword123!",
        )
        self.hobby = Hobby.objects.create(name="Acupuntura", slug="acupuntura")
        self.article = Article.objects.create(
            title="Eficacia de Puntos Shu en Dorsalgia",
            slug="eficacia-puntos-shu-dorsalgia",
            content="Estudio de casos clínicos y evidencia contemporánea.",
            author=self.author,
            hobby=self.hobby,
        )

    def test_article_comment_creates_notification_with_article_fk_and_email(self):
        """Comentario en artículo -> SÍ crea Notification con FK article + Email en mail.outbox."""
        self.client.force_login(self.reader)
        response = self.client.post(
            reverse("library:add_comment", kwargs={"slug": self.article.slug}),
            {"content": "Impresionante revisión bibliográfica. Muy riguroso."},
        )
        self.assertRedirects(
            response,
            reverse("library:article_detail", kwargs={"slug": self.article.slug}),
        )

        # 1. Campanita con FK article
        notif = Notification.objects.filter(
            recipient=self.author,
            sender=self.reader,
            notification_type="article_comment",
            article=self.article,
        ).first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.article.id, self.article.id)
        self.assertIn("ha comentado en tu artículo", notif.text)

        # 2. Email enviado
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["autor_medico@example.com"])
        self.assertIn("Nuevo comentario en tu artículo", mail.outbox[0].subject)
        self.assertIn(self.article.title, mail.outbox[0].subject)

    def test_article_rating_creates_notification_with_article_fk_and_email(self):
        """Calificación de artículo -> SÍ crea Notification con FK article + Email en mail.outbox."""
        self.client.force_login(self.reader)
        response = self.client.post(
            reverse("library:rate_article", kwargs={"slug": self.article.slug}),
            {"rating": "5"},
        )
        self.assertRedirects(
            response,
            reverse("library:article_detail", kwargs={"slug": self.article.slug}),
        )

        # 1. Campanita con FK article
        notif = Notification.objects.filter(
            recipient=self.author,
            sender=self.reader,
            notification_type="article_rating",
            article=self.article,
        ).first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.article.id, self.article.id)
        self.assertIn("ha valorado tu artículo", notif.text)

        # 2. Email enviado
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["autor_medico@example.com"])
        self.assertIn("Nueva valoración en tu artículo", mail.outbox[0].subject)
        self.assertIn(self.article.title, mail.outbox[0].subject)

    def test_bell_redirection_to_article_detail_for_comment_and_rating(self):
        """Redirección desde la campanita hacia library:article_detail comprobada."""
        self.client.force_login(self.author)

        notif_comment = Notification.objects.create(
            recipient=self.author,
            sender=self.reader,
            notification_type="article_comment",
            article=self.article,
        )
        notif_rating = Notification.objects.create(
            recipient=self.author,
            sender=self.reader,
            notification_type="article_rating",
            article=self.article,
        )

        # Redirección mediante notification_redirect
        response_comment = self.client.get(
            reverse(
                "notifications:notification_redirect",
                kwargs={"pk": notif_comment.pk},
            )
        )
        self.assertRedirects(
            response_comment,
            reverse("library:article_detail", kwargs={"slug": self.article.slug}),
        )
        notif_comment.refresh_from_db()
        self.assertTrue(notif_comment.is_read)

        # Redirección mediante read_and_redirect
        response_rating = self.client.get(
            reverse(
                "notifications:read_and_redirect",
                kwargs={"notification_id": notif_rating.pk},
            )
        )
        self.assertRedirects(
            response_rating,
            reverse("library:article_detail", kwargs={"slug": self.article.slug}),
        )
        notif_rating.refresh_from_db()
        self.assertTrue(notif_rating.is_read)


@override_settings(
    DEBUG=True,
    SECURE_SSL_REDIRECT=False,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@aficionados.com",
)
class ArchitecturalNotificationRuleTests(TestCase):
    """
    Pruebas exhaustivas para las REGLAS ARQUITECTÓNICAS DE NOTIFICACIÓN:
    - Regla Anti-Autoalerta: sender == recipient NO crea Notification ni envía email.
    - Manejo Resiliente: si Celery o el broker parpadean, la campanita persiste y se activa el fallback sin reventar el ciclo HTTP.
    - Validación defensiva de modelos ajenos asignados al campo comment.
    - Derivación inteligente de action_url.
    """

    def setUp(self):
        mail.outbox.clear()
        self.user = User.objects.create_user(
            username="usuario_sistema",
            email="usuario@example.com",
            password="TestPassword123!",
        )
        self.other_user = User.objects.create_user(
            username="otro_usuario",
            email="otro@example.com",
            password="TestPassword123!",
        )
        self.hobby = Hobby.objects.create(name="Fitoterapia", slug="fitoterapia")
        self.post = Posts.objects.create(
            user=self.user,
            title="Auto-post",
            caption="Post para test de auto-notificación",
            category=self.hobby,
        )
        self.event = Event.objects.create(
            title="Auto-evento",
            description="Evento para test",
            location="Online",
            event_date=timezone.now() + timedelta(days=5),
            organizer=self.user,
            hobby=self.hobby,
        )
        self.article = Article.objects.create(
            title="Auto-artículo",
            slug="auto-articulo",
            content="Contenido auto",
            author=self.user,
            hobby=self.hobby,
        )

    def test_anti_self_notification_rule_discards_all_social_events(self):
        """Regla Anti-Autoalerta: sender == recipient NO crea Notification ni envía email en ningún evento."""
        social_types = [
            "like",
            "comment",
            "follow",
            "event",
            "review",
            "chat_request",
            "article_comment",
            "article_rating",
        ]

        for ntype in social_types:
            with self.subTest(notification_type=ntype):
                mail.outbox.clear()
                initial_count = Notification.objects.count()

                result = NotificationDispatcher.dispatch(
                    notification_type=ntype,
                    sender=self.user,
                    recipient=self.user,
                    post=self.post,
                    event=self.event,
                    article=self.article,
                    send_email=True,
                    email_subject="Debería descartarse",
                )

                self.assertIsNone(result)
                self.assertEqual(Notification.objects.count(), initial_count)
                self.assertEqual(len(mail.outbox), 0)

    def test_anti_spam_like_strictly_suppresses_email(self):
        """Regla anti-spam estricta: Likes jamás envían email aunque se solicite explícitamente."""
        mail.outbox.clear()
        notif = NotificationDispatcher.dispatch(
            notification_type="like",
            sender=self.other_user,
            recipient=self.user,
            post=self.post,
            send_email=True,
        )

        self.assertIsNotNone(notif)
        self.assertEqual(notif.notification_type, "like")
        self.assertEqual(len(mail.outbox), 0)

    def test_resilient_handling_when_celery_broker_fails_notification_persists_and_fallback_runs(self):
        """Manejo resiliente: Si Celery task falla por broker caído, la campanita persiste y se activa fallback."""
        mail.outbox.clear()

        # Simular fallo en broker de Celery (Redis inaccesible)
        with patch(
            "aficionados_network.tasks.send_email_task.delay",
            side_effect=RuntimeError("Redis connection refused"),
        ):
            notif = NotificationDispatcher.dispatch(
                notification_type="comment",
                sender=self.other_user,
                recipient=self.user,
                post=self.post,
                message="comentó en tu post",
                send_email=True,
                email_subject="Comentario con Celery Down",
                email_body="Cuerpo de contingencia",
            )

        # 1. La notificación in-app se creó exitosamente y no se perdió
        self.assertIsNotNone(notif)
        self.assertTrue(
            Notification.objects.filter(pk=notif.pk).exists()
        )

        # 2. El fallback en mailer se ejecutó (vía ThreadPoolExecutor o sincrónico)
        time.sleep(0.15)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["usuario@example.com"])
        self.assertIn("Comentario con Celery Down", mail.outbox[0].subject)

    def test_resilient_handling_when_email_sending_crashes_http_cycle_does_not_break(self):
        """Manejo resiliente: Si el despacho de correo lanza excepción catastrófica, no revienta el ciclo HTTP."""
        with patch(
            "notifications.services.send_hubs_email_async",
            side_effect=Exception("Catastrophic SMTP Outage"),
        ):
            # No debe propagar la excepción al llamador
            notif = NotificationDispatcher.dispatch(
                notification_type="comment",
                sender=self.other_user,
                recipient=self.user,
                post=self.post,
                send_email=True,
            )

        # La campanita persiste a pesar del colapso del subsistema de correo
        self.assertIsNotNone(notif)
        self.assertTrue(Notification.objects.filter(pk=notif.pk).exists())

    def test_defensive_comment_fk_validation(self):
        """Validación defensiva: Si se pasa un objeto ajeno a posts.Comment, no explota el ORM."""
        # Creamos un objeto que no es Comment (ej. el post) y lo pasamos como comment
        notif = NotificationDispatcher.dispatch(
            notification_type="comment",
            sender=self.other_user,
            recipient=self.user,
            post=self.post,
            comment=self.post,  # Tipo de objeto erróneo intencionado
        )
        self.assertIsNotNone(notif)
        self.assertIsNone(notif.comment)

    def test_smart_action_url_derivation(self):
        """Derivación inteligente de URLs de acción según el contexto del modelo provisto."""
        with patch("notifications.services.send_hubs_email_async") as mock_mailer:
            # 1. Evento
            NotificationDispatcher.dispatch(
                notification_type="event",
                sender=self.other_user,
                recipient=self.user,
                event=self.event,
                send_email=True,
            )
            args, kwargs = mock_mailer.call_args
            self.assertEqual(
                kwargs["action_url"],
                reverse("posts:event_detail", args=[self.event.id]),
            )

            # 2. Post
            mock_mailer.reset_mock()
            NotificationDispatcher.dispatch(
                notification_type="comment",
                sender=self.other_user,
                recipient=self.user,
                post=self.post,
                send_email=True,
            )
            args, kwargs = mock_mailer.call_args
            self.assertEqual(
                kwargs["action_url"],
                reverse("posts:post_detail", args=[self.post.id]),
            )

            # 3. Artículo
            mock_mailer.reset_mock()
            NotificationDispatcher.dispatch(
                notification_type="article_comment",
                sender=self.other_user,
                recipient=self.user,
                article=self.article,
                send_email=True,
            )
            args, kwargs = mock_mailer.call_args
            self.assertEqual(
                kwargs["action_url"],
                reverse("library:article_detail", args=[self.article.slug]),
            )

            # 4. Fallback genérico a notifications:list
            mock_mailer.reset_mock()
            NotificationDispatcher.dispatch(
                notification_type="badge",
                sender=self.other_user,
                recipient=self.user,
                send_email=True,
            )
            args, kwargs = mock_mailer.call_args
            self.assertEqual(kwargs["action_url"], reverse("notifications:list"))
