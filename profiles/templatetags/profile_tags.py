from django import template
from profiles.models import UserProfile

register = template.Library()

@register.simple_tag
def get_professionals_count():
    count = UserProfile.objects.count()
    if count > 999:
        return "+999"
    return str(count)

