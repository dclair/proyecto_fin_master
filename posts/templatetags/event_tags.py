from django import template
from posts.models import Event

register = template.Library()

@register.simple_tag
def get_match_status(event, user_levels_map):
    """
    Calcula si un evento hace match con el nivel del usuario y si el usuario puede ser mentor.
    Recibe:
    - event: La instancia del Evento.
    - user_levels_map: Un diccionario {hobby_id: nivel_del_usuario}.
    Devuelve un diccionario con las claves 'is_match' y 'is_mentor'.
    """
    if not user_levels_map:
        return {"is_match": False, "is_mentor": False}
        
    u_level = user_levels_map.get(event.hobby_id)
    
    # Lógica de match
    is_match = (event.level == "all") or (event.level == u_level)
    
    # Lógica de mentoría
    is_mentor = False
    if event.level != "all" and u_level:
        level_order = {"beginner": 0, "intermediate": 1, "advanced": 2, "expert": 3}
        is_mentor = level_order.get(u_level, 0) > level_order.get(event.level, -1)
        
    return {"is_match": is_match, "is_mentor": is_mentor}

@register.simple_tag
def get_events_count():
    count = Event.objects.count()
    if count > 999:
        return "+999"
    return str(count)
