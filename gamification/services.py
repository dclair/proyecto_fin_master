from .models import Badge, UserBadge
from posts.models import Posts, Event
from notifications.models import Notification
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count, Q, Avg


def has_badge(user, code_name: str) -> bool:
    """Verificación O(1) para evitar consultas si el usuario ya tiene la medalla."""
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    return UserBadge.objects.filter(user=user, badge__code_name=code_name).exists()


def check_likes_badge(user):
    """
    1. Medalla: Voz Holística (50 likes en total)
    Optimizado: 1 sola consulta SQL agregada, o salida inmediata O(1) si ya fue obtenida.
    """
    if not user or not getattr(user, 'is_authenticated', False) or has_badge(user, 'voz-holistica'):
        return

    # Consulta agregada directa a través de la tabla intermedia (0 bucles)
    total_likes = Posts.likes.through.objects.filter(posts__user=user).count()

    if total_likes >= 50:
        award_badge(user, 'voz-holistica', 'Voz Holística', 'fas fa-leaf text-success')


def check_event_badges(user):
    """
    2. Medalla: Maestro Facilitador (3 eventos con 10 presenciales o 20 online)
    Optimizado: 1 sola consulta SQL agregada con annotate condicional.
    """
    if not user or not getattr(user, 'is_authenticated', False):
        return

    if has_badge(user, 'maestro-facilitador'):
        return

    # 1 sola query con agregación filtrada en base de datos (0 bucles en Python)
    qualifying_events = (
        Event.objects.filter(organizer=user)
        .annotate(
            physical_count=Count('attendances', filter=Q(attendances__attendance_type='physical')),
            online_count=Count('attendances', filter=Q(attendances__attendance_type='online'))
        )
        .filter(Q(physical_count__gte=10) | Q(online_count__gte=20))
        .count()
    )

    if qualifying_events >= 3:
        award_badge(user, 'maestro-facilitador', 'Maestro Facilitador', 'fas fa-sun text-warning')
    elif qualifying_events == 2:
        # Aviso motivacional (si no se avisó antes)
        already_warned = Notification.objects.filter(
            recipient=user,
            notification_type='badge',
            message__icontains='estás a un solo evento'
        ).exists()

        if not already_warned:
            send_motivation_warning(user)


def check_review_badges(user):
    """
    3. Medalla: Guía de Luz (Promedio de 4.5 estrellas o más, con un mínimo de 5 valoraciones)
    Optimizado: 1 sola consulta agregada combinando conteo y promedio.
    """
    if not user or not getattr(user, 'is_authenticated', False) or has_badge(user, 'guia-de-luz'):
        return

    from profiles.models import Review

    stats = Review.objects.filter(recipient=user).aggregate(
        total_count=Count('id'),
        avg_rating=Avg('rating')
    )

    total_count = stats.get('total_count') or 0
    avg_rating = stats.get('avg_rating') or 0.0

    if total_count >= 5 and avg_rating >= 4.5:
        award_badge(user, 'guia-de-luz', 'Guía de Luz', 'fas fa-star-of-life text-info')


def check_badges(user):
    """Fachada para verificar todas las medallas del usuario (útil para tareas batch/cron)."""
    check_likes_badge(user)
    check_event_badges(user)
    check_review_badges(user)


def award_badge(user, code_name, name_fallback, icon_fallback):
    badge, created = Badge.objects.get_or_create(code_name=code_name, defaults={
        'name': name_fallback,
        'description': 'Reconocimiento a tu compromiso y participación en la comunidad naturopática.',
        'icon': icon_fallback
    })

    user_badge, awarded = UserBadge.objects.get_or_create(user=user, badge=badge)

    if awarded:
        admin_user = User.objects.filter(is_superuser=True).first() or user
        Notification.objects.create(
            recipient=user,
            sender=admin_user,
            notification_type='badge',
            message=f'¡Felicidades! Has desbloqueado la medalla: {badge.name}'
        )

        try:
            send_mail(
                f'¡Logro Desbloqueado: {badge.name}!',
                f'Hola {user.username},\n\nHas desbloqueado una nueva medalla en tu perfil: {badge.name}.\n\n¡Gracias por iluminar la red y compartir tu sabiduría!\n\nEl equipo de Aficionados Network.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True
            )
        except Exception:
            pass


def send_motivation_warning(user):
    admin_user = User.objects.filter(is_superuser=True).first() or user
    Notification.objects.create(
        recipient=user,
        sender=admin_user,
        notification_type='badge',
        message='¡Estás a un solo evento exitoso de alcanzar la medalla "Maestro Facilitador"!'
    )

    try:
        send_mail(
            '¡Estás muy cerca de tu próxima medalla!',
            f'Hola {user.username},\n\nYa has organizado 2 eventos súper exitosos (con al menos 10 asistentes presenciales o 20 online). '
            f'¡Estás a un solo evento de alcanzar la medalla honorífica de "Maestro Facilitador"!\n\nAnímate a organizar el próximo encuentro y seguir guiando a la comunidad.\n\nEl equipo de Aficionados Network.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True
        )
    except Exception:
        pass
