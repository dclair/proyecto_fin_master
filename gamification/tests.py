from django.test import TestCase
from django.contrib.auth.models import User
from profiles.models import Hobby, Review
from posts.models import Posts, Event, EventAttendance
from gamification.models import Badge, UserBadge
from gamification.services import (
    check_likes_badge,
    check_event_badges,
    check_review_badges,
    has_badge
)
from notifications.models import Notification


class GamificationServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="terapeuta", email="terapeuta@test.com", password="Pass123Complex!")
        self.voter = User.objects.create_user(username="voter", email="voter@test.com", password="Pass123Complex!")
        self.hobby = Hobby.objects.create(name="Aromaterapia", slug="aromaterapia")

    def test_likes_badge_awarded_at_50_likes(self):
        # Crear posts y agregar likes
        post = Posts.objects.create(user=self.user, category=self.hobby, caption="Post de prueba")
        
        # Simular 49 likes
        users = [User.objects.create_user(username=f"u_{i}", email=f"u_{i}@test.com", password="p") for i in range(49)]
        post.likes.add(*users)

        check_likes_badge(self.user)
        self.assertFalse(has_badge(self.user, 'voz-holistica'))

        # Like número 50
        post.likes.add(self.voter)
        check_likes_badge(self.user)

        self.assertTrue(has_badge(self.user, 'voz-holistica'))
        self.assertTrue(Notification.objects.filter(recipient=self.user, notification_type='badge').exists())

    def test_event_badge_and_motivation_warning(self):
        from django.utils import timezone
        now = timezone.now()

        # Crear 2 eventos con 10 asistentes presenciales cada uno
        for i in range(2):
            ev = Event.objects.create(
                organizer=self.user,
                hobby=self.hobby,
                title=f"Evento {i}",
                description="Desc",
                event_date=now
            )
            attendees = [User.objects.create_user(username=f"att_{i}_{j}", email=f"att_{i}_{j}@test.com", password="p") for j in range(10)]
            for att in attendees:
                EventAttendance.objects.create(event=ev, user=att, attendance_type='physical')

        check_event_badges(self.user)
        self.assertFalse(has_badge(self.user, 'maestro-facilitador'))
        # Debe haber recibido notificación motivacional
        self.assertTrue(
            Notification.objects.filter(recipient=self.user, message__icontains='estás a un solo evento').exists()
        )

        # Crear el tercer evento exitoso
        ev3 = Event.objects.create(
            organizer=self.user,
            hobby=self.hobby,
            title="Evento 3",
            description="Desc",
            event_date=now
        )
        attendees3 = [User.objects.create_user(username=f"att_3_{j}", email=f"att_3_{j}@test.com", password="p") for j in range(20)]
        for att in attendees3:
            EventAttendance.objects.create(event=ev3, user=att, attendance_type='online')

        check_event_badges(self.user)
        self.assertTrue(has_badge(self.user, 'maestro-facilitador'))

    def test_review_badge_awarded_with_high_average_and_minimum_reviews(self):
        from django.utils import timezone
        ev = Event.objects.create(
            organizer=self.user,
            hobby=self.hobby,
            title="Evento Reseña",
            description="Desc",
            event_date=timezone.now()
        )

        # 4 reseñas con 5 estrellas (no califica aún, requiere 5)
        for i in range(4):
            reviewer = User.objects.create_user(username=f"rev_{i}", email=f"rev_{i}@t.com", password="p")
            Review.objects.create(author=reviewer, recipient=self.user, event=ev, rating=5, comment="Excelente")

        check_review_badges(self.user)
        self.assertFalse(has_badge(self.user, 'guia-de-luz'))

        # Quinta reseña con 4 estrellas (promedio = (5*4 + 4)/5 = 4.8 >= 4.5)
        reviewer5 = User.objects.create_user(username="rev_5", email="rev_5@t.com", password="p")
        Review.objects.create(author=reviewer5, recipient=self.user, event=ev, rating=4, comment="Muy bueno")

        check_review_badges(self.user)
        self.assertTrue(has_badge(self.user, 'guia-de-luz'))
