from django import template
from django.utils import timezone
from django.db.models import Count, Q
from profiles.models import UserHobby
from posts.models import Event

register = template.Library()

@register.inclusion_tag('general/components/_sidebar_terapias.html', takes_context=True)
def render_terapias_sidebar(context):
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return {'my_hobbies': []}

    user = request.user
    if not hasattr(user, 'profile'):
        return {'my_hobbies': []}

    now = timezone.now()
    my_hobbies = list(user.profile.hobbies.all().order_by('name'))
    
    if not my_hobbies:
        return {'my_hobbies': []}

    user_levels = UserHobby.objects.filter(profile=user.profile)
    levels_map = {uh.hobby_id: uh.level for uh in user_levels}

    event_q = Q()
    for hobby in my_hobbies:
        u_level = levels_map.get(hobby.id)
        if u_level:
            event_q |= Q(hobby_id=hobby.id, level__in=["all", u_level])
        else:
            event_q |= Q(hobby_id=hobby.id, level="all")

    if event_q:
        match_counts = (
            Event.objects.filter(event_date__gte=now, is_canceled=False)
            .filter(event_q)
            .values("hobby_id")
            .annotate(count=Count("id"))
        )
        counts_map = {item["hobby_id"]: item["count"] for item in match_counts}

        # Resiliencia / Desarrollo: si no hay eventos futuros activos, contar eventos activos no cancelados que hagan match
        if not any(counts_map.values()):
            fallback_counts = (
                Event.objects.filter(is_canceled=False)
                .filter(event_q)
                .values("hobby_id")
                .annotate(count=Count("id"))
            )
            counts_map = {item["hobby_id"]: item["count"] for item in fallback_counts}
    else:
        counts_map = {}

    for hobby in my_hobbies:
        hobby.match_count = counts_map.get(hobby.id, 0)
        
    return {
        'my_hobbies': my_hobbies,
        'current_hub': context.get('current_hub'),
    }
