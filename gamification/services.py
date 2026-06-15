from .models import Badge, UserBadge
from posts.models import Posts, Event, EventAttendance
from notifications.models import Notification
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

def check_badges(user):
    # 1. Medalla: Voz Holística (50 likes en total)
    posts = Posts.objects.filter(user=user)
    total_likes = sum(post.likes.count() for post in posts)
    
    if total_likes >= 50:
        award_badge(user, 'voz-holistica', 'Voz Holística', 'fas fa-leaf text-success')
        
    # 2. Medalla: Maestro Facilitador (3 eventos con 10 presenciales o 20 online)
    events = Event.objects.filter(organizer=user)
    qualifying_events = 0
    for event in events:
        physical = event.attendances.filter(attendance_type='physical').count()
        online = event.attendances.filter(attendance_type='online').count()
        if physical >= 10 or online >= 20:
            qualifying_events += 1
            
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
            
    # 3. Medalla: Guía de Luz (Promedio de 4.5 estrellas o más, con un mínimo de 5 valoraciones)
    from profiles.models import Review
    from django.db.models import Avg
    
    reviews = Review.objects.filter(recipient=user)
    if reviews.count() >= 5:
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        if avg_rating and avg_rating >= 4.5:
            award_badge(user, 'guia-de-luz', 'Guía de Luz', 'fas fa-star-of-life text-info')

def award_badge(user, code_name, name_fallback, icon_fallback):
    badge, created = Badge.objects.get_or_create(code_name=code_name, defaults={
        'name': name_fallback,
        'description': 'Reconocimiento a tu compromiso y participación en la comunidad naturopática.',
        'icon': icon_fallback
    })
    
    user_badge, awarded = UserBadge.objects.get_or_create(user=user, badge=badge)
    
    if awarded:
        # Admin o system user para el sender
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
